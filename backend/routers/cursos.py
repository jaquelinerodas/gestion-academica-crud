from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.post("", response_model=schemas.Curso, status_code=201)
def crear_curso(curso: schemas.CursoCreate, db: Session = Depends(get_db)):
    profesor = db.query(models.Profesor).filter(models.Profesor.id == curso.profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=400, detail="El profesor indicado no existe")
    nuevo = models.Curso(**curso.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get("", response_model=list[schemas.Curso])
def listar_cursos(
    nombre: str | None = None,
    profesor_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Curso)
    if nombre:
        consulta = consulta.filter(models.Curso.nombre.ilike(f"%{nombre}%"))
    if profesor_id:
        consulta = consulta.filter(models.Curso.profesor_id == profesor_id)
    return consulta.offset(skip).limit(limit).all()


@router.get("/{curso_id}", response_model=schemas.Curso)
def obtener_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@router.put("/{curso_id}", response_model=schemas.Curso)
def actualizar_curso(curso_id: int, datos: schemas.CursoCreate, db: Session = Depends(get_db)):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    profesor = db.query(models.Profesor).filter(models.Profesor.id == datos.profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=400, detail="El profesor indicado no existe")
    curso.nombre = datos.nombre
    curso.descripcion = datos.descripcion
    curso.profesor_id = datos.profesor_id
    db.commit()
    db.refresh(curso)
    return curso


@router.delete("/{curso_id}", status_code=204)
def eliminar_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    db.delete(curso)
    db.commit()
    return None
