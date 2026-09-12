from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import get_db

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])


@router.post("", response_model=schemas.Inscripcion, status_code=201)
def crear_inscripcion(inscripcion: schemas.InscripcionCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == inscripcion.estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=400, detail="El estudiante indicado no existe")

    curso = db.query(models.Curso).filter(models.Curso.id == inscripcion.curso_id).first()
    if not curso:
        raise HTTPException(status_code=400, detail="El curso indicado no existe")

    nueva = models.Inscripcion(**inscripcion.model_dump())
    db.add(nueva)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El estudiante ya está inscrito en ese curso")
    db.refresh(nueva)
    return nueva


@router.get("", response_model=list[schemas.Inscripcion])
def listar_inscripciones(
    estado: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Inscripcion)
    if estado:
        consulta = consulta.filter(models.Inscripcion.estado == estado)
    return consulta.offset(skip).limit(limit).all()


@router.get("/{inscripcion_id}", response_model=schemas.Inscripcion)
def obtener_inscripcion(inscripcion_id: int, db: Session = Depends(get_db)):
    inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return inscripcion


@router.put("/{inscripcion_id}", response_model=schemas.Inscripcion)
def actualizar_inscripcion(inscripcion_id: int, datos: schemas.InscripcionCreate, db: Session = Depends(get_db)):
    inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")

    inscripcion.fecha_inscripcion = datos.fecha_inscripcion
    inscripcion.nota = datos.nota
    inscripcion.estado = datos.estado
    db.commit()
    db.refresh(inscripcion)
    return inscripcion


@router.delete("/{inscripcion_id}", status_code=204)
def eliminar_inscripcion(inscripcion_id: int, db: Session = Depends(get_db)):
    inscripcion = db.query(models.Inscripcion).filter(models.Inscripcion.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    db.delete(inscripcion)
    db.commit()
    return None
