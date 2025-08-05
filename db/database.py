# Motor y sesion de la BBDD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base
from dotenv import load_dotenv
load_dotenv()
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Aquí creamos una base de datos SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL, echo=False)
    # Intentar conectar y crear las tablas
    Base.metadata.create_all(engine)
    logger.info("Conexión a la base de datos establecida y tablas creadas correctamente.")
except SQLAlchemyError as e:
    logger.error(f"No se pudo conectar a la base de datos: {e}")

SessionLocal = sessionmaker(bind=engine)

def init_db():
    # Esto crea las tablas en la base de datos si no existen
    Base.metadata.create_all(engine)
