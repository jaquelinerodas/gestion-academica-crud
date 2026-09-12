from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import get_db

router = APIRouter(prefix="/profesores", tags=["Profesores"])


@router.post("", response_model=schemas.Profesor, status_code=201)
def crear_profesor(profesor: schemas.ProfesorCreate, db: Session = Depends(get_db)):
    nuevo = models.Profesor(**profesor.model_dump())
    db.add(nuevo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un profesor con ese email")
    db.refresh(nuevo)
    return nuevo


@router.get("", response_model=list[schemas.Profesor])
def listar_profesores(
    nombre: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Profesor)
    if nombre:
        consulta = consulta.filter(models.Profesor.nombre.ilike(f"%{nombre}%"))
    return consulta.offset(skip).limit(limit).all()


@router.get("/{profesor_id}", response_model=schemas.Profesor)
def obtener_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor


@router.put("/{profesor_id}", response_model=schemas.Profesor)
def actualizar_profesor(profesor_id: int, datos: schemas.ProfesorCreate, db: Session = Depends(get_db)):
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    profesor.nombre = datos.nombre
    profesor.email = datos.email
    profesor.especialidad = datos.especialidad
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un profesor con ese email")
    db.refresh(profesor)
    return profesor


@router.delete("/{profesor_id}", status_code=204)
def eliminar_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    if profesor.cursos:
        raise HTTPException(status_code=400, detail="No se puede eliminar: el profesor tiene cursos asignados")
    db.delete(profesor)
    db.commit()
    return None
