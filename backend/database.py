import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # lee el archivo .env si existe (ver .env.example)


# Datos de conexión: se leen de variables de entorno, con valores por
# defecto pensados para una instalación local típica de PostgreSQL.
# Puedes sobreescribirlos creando un archivo .env (ver .env.example)
# o exportándolos en tu sistema antes de correr el servidor.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gestion_academica")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# pool_pre_ping=True hace que SQLAlchemy verifique que la conexión sigue
# viva antes de usarla; si el servidor de base de datos se cayó, esto
# permite detectarlo y lanzar un error controlado en vez de uno confuso.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
