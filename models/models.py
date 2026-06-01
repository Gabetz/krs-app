from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ─── Tabel pivot (Cukup definisikan ini saja untuk KRS) ───────────────
krs_table = Table(
    "krs",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("mahasiswa_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("kelas_id",     Integer, ForeignKey("kelas.id",  ondelete="CASCADE")),
    Column("submitted",    Boolean, default=False),
    Column("created_at",   DateTime, default=func.now()),
    UniqueConstraint("mahasiswa_id", "kelas_id", name="uq_krs"),
)

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    nama_lengkap    = Column(String(120), nullable=False)
    username        = Column(String(60),  unique=True, index=True, nullable=False)
    email           = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(String(20),  default="mahasiswa")
    nim_nip         = Column(String(30),  unique=True, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime,    default=func.now())

    kelas_diajar    = relationship("Kelas", back_populates="dosen")
    krs_list        = relationship("Kelas", secondary=krs_table, back_populates="peserta")

class Kelas(Base):
    __tablename__ = "kelas"
    id          = Column(Integer, primary_key=True, index=True)
    kode_kelas  = Column(String(20),  unique=True, nullable=False)
    nama_matkul = Column(String(150), nullable=False)
    sks         = Column(Integer,     default=2)
    kuota       = Column(Integer,     default=30)
    
    hari        = Column(String(20),  nullable=True)
    jam_mulai   = Column(String(10),  nullable=True)
    jam_selesai = Column(String(10),  nullable=True)
    ruangan     = Column(String(50),  nullable=True)
    semester    = Column(String(50),  nullable=True)
    
    is_active   = Column(Boolean,     default=True)
    created_at  = Column(DateTime,    default=func.now())
    
    dosen_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    dosen       = relationship("User", back_populates="kelas_diajar")
    peserta     = relationship("User", secondary=krs_table, back_populates="krs_list")

    

    @property
    def terisi(self):
        return len(self.peserta)

    @property
    def sisa_kuota(self):
        return self.kuota - len(self.peserta)