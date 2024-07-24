from fastapi import FastAPI, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
import databases
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

DATABASE_URL = "postgresql+asyncpg://postgres:Millonarios1@localhost/forms_qhronus_devs"

database = databases.Database(DATABASE_URL)
Base = declarative_base()

class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, index=True)
    ciudad = Column(String, index=True)
    celular = Column(String, index=True)
    tecnologias = Column(String)
    expectativa_salarial = Column(String)
    experiencia = Column(Integer)
    disponibilidad = Column(String)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

app = FastAPI()

class DeveloperCreate(BaseModel):
    nombre: str
    email: str
    ciudad: str
    celular: str
    tecnologias: str
    expectativa_salarial: float
    experiencia: int
    disponibilidad: bool

@app.on_event("startup")
async def startup():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/submit_developer")
async def create_developer(
    nombre: str = Form(...),
    email: str = Form(...),
    ciudad: str = Form(...),
    celular: str = Form(...),
    tecnologias: str = Form(...),
    expectativa_salarial: float = Form(...),
    experiencia: int = Form(...),
    disponibilidad: bool = Form(...)
):
    query = Developer.__table__.insert().values(
        nombre=nombre,
        email=email,
        ciudad=ciudad,
        celular=celular,
        tecnologias=tecnologias,
        expectativa_salarial=expectativa_salarial,
        experiencia=experiencia,
        disponibilidad=disponibilidad
    )
    last_record_id = await database.execute(query)
    return {"id": last_record_id}

# Sirve el archivo HTML
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("static/form.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
