from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from weasyprint import HTML
from database import get_db
from models.models import User, Kelas

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def _require_mahasiswa(request: Request, db: Session) -> User | None:
    uid = request.session.get("user_id")
    if not uid:
        return None
    user = db.query(User).filter(User.id == uid, User.is_active == True).first()
    if not user or user.role not in ("mahasiswa",):
        return None
    return user

# ── Dashboard Mahasiswa ────────────────────────────────────────────────────────
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_mahasiswa(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    rows = db.execute(
        text("SELECT kelas_id, submitted FROM krs WHERE mahasiswa_id = :uid"),
        {"uid": user.id}
    ).fetchall()

    kelas_ids = [r.kelas_id for r in rows]
    submitted_ids = {r.kelas_id for r in rows if r.submitted}
    kelas_dipilih = db.query(Kelas).filter(Kelas.id.in_(kelas_ids)).all() if kelas_ids else []

    total_sks = sum(k.sks for k in kelas_dipilih)
    all_submitted = bool(kelas_dipilih) and all(k.id in submitted_ids for k in kelas_dipilih)

    return templates.TemplateResponse("user_dashboard.html", {
        "request": request,
        "user": user,
        "kelas_dipilih": kelas_dipilih,
        "submitted_ids": submitted_ids,
        "total_sks": total_sks,
        "all_submitted": all_submitted,
    })

# ── Daftar semua kelas tersedia ────────────────────────────────────────────────
@router.get("/dashboard/kelas", response_class=HTMLResponse)
async def pilih_kelas(request: Request, db: Session = Depends(get_db)):
    user = _require_mahasiswa(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    semua_kelas = db.query(Kelas).filter(Kelas.is_active == True).all()
    rows = db.execute(
        text("SELECT kelas_id FROM krs WHERE mahasiswa_id = :uid"),
        {"uid": user.id}
    ).fetchall()
    dipilih_ids = {r.kelas_id for r in rows}

    return templates.TemplateResponse("kelas_list.html", {
        "request": request,
        "user": user,
        "semua_kelas": semua_kelas,
        "dipilih_ids": dipilih_ids,
    })

# ── Pilih / batalkan kelas ─────────────────────────────────────────────────────
@router.post("/dashboard/kelas/{kelas_id}/pilih")
async def pilih(kelas_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_mahasiswa(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    kelas = db.query(Kelas).filter(Kelas.id == kelas_id, Kelas.is_active == True).first()
    if not kelas:
        return RedirectResponse("/dashboard/kelas", status_code=302)

    existing = db.execute(
        text("SELECT id, submitted FROM krs WHERE mahasiswa_id=:uid AND kelas_id=:kid"),
        {"uid": user.id, "kid": kelas_id}
    ).fetchone()

    if existing:
        if not existing.submitted:
            db.execute(
                text("DELETE FROM krs WHERE mahasiswa_id=:uid AND kelas_id=:kid"),
                {"uid": user.id, "kid": kelas_id}
            )
            db.commit()
    else:
        if kelas.sisa_kuota > 0:
            db.execute(
                text("INSERT INTO krs (mahasiswa_id, kelas_id, submitted) VALUES (:uid, :kid, FALSE)"),
                {"uid": user.id, "kid": kelas_id}
            )
            db.commit()

    return RedirectResponse("/dashboard/kelas", status_code=302)

# ── Submit semua KRS (kunci) ───────────────────────────────────────────────────
@router.get("/dashboard/kelas/submit-all")
async def submit_all(request: Request, db: Session = Depends(get_db)):
    user = _require_mahasiswa(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    db.execute(
        text("UPDATE krs SET submitted=TRUE WHERE mahasiswa_id=:uid AND submitted=FALSE"),
        {"uid": user.id}
    )
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)

@router.get("/cetak-krs")
async def cetak_krs(request: Request, db: Session = Depends(get_db)):
    # 1. Pastikan user login
    user = _require_mahasiswa(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # 2. Ambil data kelas yang dipilih
    krs_data = user.krs_list 

    # 3. Render HTML
    template = templates.get_template("cetak_krs.html")
    html_content = template.render(
        request=request, 
        krs_list=krs_data, 
        # Kirim objek 'user' sebagai 'mahasiswa' agar cocok dengan template
        mahasiswa={
            "nama_lengkap": user.nama_lengkap,
            "nim": user.nim_nip # Sesuaikan dengan field di model User Anda
        }
    )
    
    # 4. Konversi HTML ke PDF
    pdf = HTML(string=html_content).write_pdf()
    
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=KRS.pdf"}
    )