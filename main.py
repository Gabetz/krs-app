from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import get_db, Base, engine 
from routes.auth import router as auth_router
from routes.dashboard import router as dash_router
from routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KRS Online — FastAPI & SQLite")

app.add_middleware(SessionMiddleware, secret_key="GANTI_SECRET_KEY_ANDA_INI_2024")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(dash_router)
app.include_router(admin_router)