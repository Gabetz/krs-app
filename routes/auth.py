from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from database import get_db
from models.models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ── helper ─────────────────────────────────────────────────────────────────────
def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    uid = request.session.get("user_id")
    if not uid:
        return None
    return db.query(User).filter(User.id == uid, User.is_active == True).first()


# ── Halaman Utama ──────────────────────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    from models.models import Kelas
    total_kelas = db.query(Kelas).filter(Kelas.is_active == True).count()
    total_mhs   = db.query(User).filter(User.role == "mahasiswa").count()
    return templates.TemplateResponse("home.html", {
        "request": request, "user": user,
        "total_kelas": total_kelas, "total_mhs": total_mhs,
    })


# ── Login ──────────────────────────────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Username atau password salah."
        })
    request.session["user_id"]   = user.id
    request.session["user_role"] = user.role
    
    if user.role in ("dosen", "admin"):
        return RedirectResponse("/admin/dashboard", status_code=302)
    return RedirectResponse("/dashboard", status_code=302)


# ── Register ───────────────────────────────────────────────────────────────────
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_post(
    request: Request,
    nama_lengkap: str = Form(...),
    username: str    = Form(...),
    email: str       = Form(...),
    nim_nip: str     = Form(""),
    password: str    = Form(...),
    role: str        = Form("mahasiswa"),
    db: Session      = Depends(get_db),
):
    dup = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if dup:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Username atau email sudah digunakan."
        })

    user = User(
        nama_lengkap=nama_lengkap,
        username=username,
        email=email,
        nim_nip=nim_nip or None,
        hashed_password=bcrypt.hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"]   = user.id
    request.session["user_role"] = user.role

    if user.role in ("dosen", "admin"):
        return RedirectResponse("/admin/dashboard", status_code=302)
    return RedirectResponse("/dashboard", status_code=302)


# ── Logout ─────────────────────────────────────────────────────────────────────
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
