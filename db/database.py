# Motor y sesion de la BBDD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv
load_dotenv()
import os

# Aquí creamos una base de datos SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # Esto crea las tablas en la base de datos si no existen
    Base.metadata.create_all(engine)
