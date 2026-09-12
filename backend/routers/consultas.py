from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

import models
import schemas
from database import get_db

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.get("/cursos/{curso_id}/estudiantes", response_model=list[schemas.EstudianteEnCurso])
def estudiantes_de_un_curso(curso_id: int, db: Session = Depends(get_db)):
    """Lista de estudiantes inscritos en un curso, con su nota y estado."""
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    filas = (
        db.query(
            models.Inscripcion.id.label("inscripcion_id"),
            models.Estudiante.id.label("estudiante_id"),
            models.Estudiante.nombre,
            models.Estudiante.email,
            models.Inscripcion.nota,
            models.Inscripcion.estado,
        )
        .join(models.Estudiante, models.Estudiante.id == models.Inscripcion.estudiante_id)
        .filter(models.Inscripcion.curso_id == curso_id)
        .all()
    )
    return [schemas.EstudianteEnCurso(**fila._mapping) for fila in filas]


@router.get("/estudiantes/{estudiante_id}/historial", response_model=list[schemas.CursoDeEstudiante])
def historial_de_un_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Cursos en los que se ha inscrito un estudiante, con nota y estado."""
    estudiante = db.query(models.Estudiante).filter(models.Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    filas = (
        db.query(
            models.Inscripcion.id.label("inscripcion_id"),
            models.Curso.id.label("curso_id"),
            models.Curso.nombre.label("nombre_curso"),
            models.Inscripcion.fecha_inscripcion,
            models.Inscripcion.nota,
            models.Inscripcion.estado,
        )
        .join(models.Curso, models.Curso.id == models.Inscripcion.curso_id)
        .filter(models.Inscripcion.estudiante_id == estudiante_id)
        .all()
    )
    return [schemas.CursoDeEstudiante(**fila._mapping) for fila in filas]


def _calcular_resumen_cursos(db: Session) -> list[schemas.ResumenCurso]:
    """Calcula, por cada curso, su profesor, total de estudiantes y promedio de notas."""
    filas = (
        db.query(
            models.Curso.id.label("curso_id"),
            models.Curso.nombre.label("nombre_curso"),
            models.Profesor.nombre.label("profesor"),
            func.count(models.Inscripcion.id).label("total_estudiantes"),
            func.avg(models.Inscripcion.nota).label("promedio_nota"),
        )
        .join(models.Profesor, models.Profesor.id == models.Curso.profesor_id)
        .outerjoin(models.Inscripcion, models.Inscripcion.curso_id == models.Curso.id)
        .group_by(models.Curso.id, models.Curso.nombre, models.Profesor.nombre)
        .all()
    )
    resultado = []
    for fila in filas:
        promedio = float(fila.promedio_nota) if fila.promedio_nota is not None else None
        resultado.append(schemas.ResumenCurso(
            curso_id=fila.curso_id,
            nombre_curso=fila.nombre_curso,
            profesor=fila.profesor,
            total_estudiantes=fila.total_estudiantes,
            promedio_nota=promedio,
        ))
    return resultado


@router.get("/resumen-cursos", response_model=list[schemas.ResumenCurso])
def resumen_por_curso(db: Session = Depends(get_db)):
  
    return _calcular_resumen_cursos(db)


@router.get("/buscar", response_model=schemas.ResultadoBusqueda)
def buscar_global(q: str, db: Session = Depends(get_db)):
    
    texto = q.strip().lstrip("#")
    codigo = int(texto) if texto.isdigit() else None

    if not codigo and len(texto) < 2:
        raise HTTPException(status_code=400, detail="Ingrese al menos 2 caracteres, o un código (#id) para buscar")

    patron = f"%{texto}%"

    filtro_profesor = [models.Profesor.nombre.ilike(patron)]
    filtro_curso = [models.Curso.nombre.ilike(patron)]
    filtro_estudiante = [models.Estudiante.nombre.ilike(patron), models.Estudiante.email.ilike(patron)]

    if codigo is not None:
        filtro_profesor.append(models.Profesor.id == codigo)
        filtro_curso.append(models.Curso.id == codigo)
        filtro_estudiante.append(models.Estudiante.id == codigo)

    profesores = db.query(models.Profesor).filter(or_(*filtro_profesor)).limit(10).all()
    cursos = db.query(models.Curso).filter(or_(*filtro_curso)).limit(10).all()
    estudiantes = db.query(models.Estudiante).filter(or_(*filtro_estudiante)).limit(10).all()

    return schemas.ResultadoBusqueda(profesores=profesores, cursos=cursos, estudiantes=estudiantes)
