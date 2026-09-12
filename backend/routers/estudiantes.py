from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import get_db

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.post("", response_model=schemas.Estudiante, status_code=201)
def crear_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    nuevo = models.Estudiante(**estudiante.model_dump())
    db.add(nuevo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un estudiante con ese email")
    db.refresh(nuevo)
    return nuevo


@router.get("", response_model=list[schemas.Estudiante])
def listar_estudiantes(
    nombre: str | None = None,
    estado: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Estudiante)
    if nombre:
        consulta = consulta.filter(models.Estudiante.nombre.ilike(f"%{nombre}%"))
    if estado:
        consulta = consulta.filter(models.Estudiante.estado == estado)
    return consulta.offset(skip).limit(limit).all()


@router.get("/{estudiante_id}", response_model=schemas.Estudiante)
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante


@router.put("/{estudiante_id}", response_model=schemas.Estudiante)
def actualizar_estudiante(estudiante_id: int, datos: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    estudiante.nombre = datos.nombre
    estudiante.email = datos.email
    estudiante.fecha_nacimiento = datos.fecha_nacimiento
    estudiante.estado = datos.estado
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un estudiante con ese email")
    db.refresh(estudiante)
    return estudiante


@router.delete("/{estudiante_id}", status_code=204)
def eliminar_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(estudiante)
    db.commit()
    return None
