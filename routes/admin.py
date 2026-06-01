from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.models import User, Kelas

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


def _require_dosen(request: Request, db: Session) -> User | None:
    uid = request.session.get("user_id")
    if not uid:
        return None
    user = db.query(User).filter(User.id == uid, User.is_active == True).first()
    if not user or user.role not in ("dosen", "admin"):
        return None
    return user


# ── Dashboard Admin ────────────────────────────────────────────────────────────
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    total_mhs    = db.query(User).filter(User.role == "mahasiswa").count()
    total_kelas  = db.query(Kelas).count()
    total_aktif  = db.query(Kelas).filter(Kelas.is_active == True).count()
    total_krs    = db.execute(text("SELECT COUNT(*) FROM krs")).scalar()
    kelas_list   = db.query(Kelas).order_by(Kelas.created_at.desc()).all()
    recent_mhs   = db.query(User).filter(User.role == "mahasiswa").order_by(User.created_at.desc()).limit(5).all()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request, "user": user,
        "total_mhs": total_mhs, "total_kelas": total_kelas,
        "total_aktif": total_aktif, "total_krs": total_krs,
        "kelas_list": kelas_list, "recent_mhs": recent_mhs,
    })


# ── Manajemen Kelas ────────────────────────────────────────────────────────────
@router.get("/kelas", response_class=HTMLResponse)
async def admin_kelas(request: Request, db: Session = Depends(get_db)):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    kelas_list = db.query(Kelas).order_by(Kelas.created_at.desc()).all()
    dosen_list = db.query(User).filter(User.role.in_(["dosen", "admin"])).all()
    return templates.TemplateResponse("admin_kelas.html", {
        "request": request, "user": user,
        "kelas_list": kelas_list, "dosen_list": dosen_list,
    })


@router.post("/kelas/create")
async def kelas_create(
    request: Request,
    kode_kelas:   str = Form(...),
    nama_matkul:  str = Form(...),
    deskripsi:    str = Form(""),
    sks:          int = Form(2),
    hari:         str = Form(...),
    jam_mulai:    str = Form(...),
    jam_selesai:  str = Form(...),
    ruangan:      str = Form(""),
    kuota:        int = Form(30),
    semester:     str = Form("Genap 2024/2025"),
    dosen_id:     int = Form(None),
    db: Session = Depends(get_db),
):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    k = Kelas(
        kode_kelas=kode_kelas, nama_matkul=nama_matkul,
        deskripsi=deskripsi, sks=sks, hari=hari,
        jam_mulai=jam_mulai, jam_selesai=jam_selesai,
        ruangan=ruangan, kuota=kuota, semester=semester,
        dosen_id=dosen_id or user.id,
    )
    db.add(k)
    db.commit()
    return RedirectResponse("/admin/kelas", status_code=302)


@router.post("/kelas/{kelas_id}/edit")
async def kelas_edit(
    kelas_id: int, request: Request,
    nama_matkul:  str = Form(...),
    deskripsi:    str = Form(""),
    sks:          int = Form(2),
    hari:         str = Form(...),
    jam_mulai:    str = Form(...),
    jam_selesai:  str = Form(...),
    ruangan:      str = Form(""),
    kuota:        int = Form(30),
    semester:     str = Form("Genap 2024/2025"),
    is_active:    bool = Form(True),
    db: Session = Depends(get_db),
):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    k = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if k:
        k.nama_matkul = nama_matkul
        k.deskripsi   = deskripsi
        k.sks         = sks
        k.hari        = hari
        k.jam_mulai   = jam_mulai
        k.jam_selesai = jam_selesai
        k.ruangan     = ruangan
        k.kuota       = kuota
        k.semester    = semester
        k.is_active   = is_active
        db.commit()
    return RedirectResponse("/admin/kelas", status_code=302)


@router.post("/kelas/{kelas_id}/delete")
async def kelas_delete(kelas_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)
    k = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if k:
        db.delete(k)
        db.commit()
    return RedirectResponse("/admin/kelas", status_code=302)


# ── Detail peserta kelas ───────────────────────────────────────────────────────
@router.get("/kelas/{kelas_id}/peserta", response_class=HTMLResponse)
async def kelas_peserta(kelas_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    kelas = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not kelas:
        return RedirectResponse("/admin/kelas", status_code=302)

    rows = db.execute(
        text("""
            SELECT u.id, u.nama_lengkap, u.nim_nip, u.email, k.submitted, k.created_at
            FROM krs k JOIN users u ON k.mahasiswa_id = u.id
            WHERE k.kelas_id = :kid
            ORDER BY u.nama_lengkap
        """),
        {"kid": kelas_id}
    ).fetchall()

    return templates.TemplateResponse("admin_peserta.html", {
        "request": request, "user": user,
        "kelas": kelas, "peserta": rows,
    })


# ── Manajemen Mahasiswa ────────────────────────────────────────────────────────
@router.get("/mahasiswa", response_class=HTMLResponse)
async def admin_mahasiswa(request: Request, db: Session = Depends(get_db)):
    user = _require_dosen(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    mhs_list = db.query(User).filter(User.role == "mahasiswa").order_by(User.nama_lengkap).all()
    return templates.TemplateResponse("admin_mahasiswa.html", {
        "request": request, "user": user, "mhs_list": mhs_list,
    })
