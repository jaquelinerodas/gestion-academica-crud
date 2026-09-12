from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from decimal import Decimal


# ---------- Profesor ----------
class ProfesorBase(BaseModel):
    nombre: str
    email: EmailStr
    especialidad: Optional[str] = None


class ProfesorCreate(ProfesorBase):
    pass


class Profesor(ProfesorBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Curso ----------
class CursoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    profesor_id: int


class CursoCreate(CursoBase):
    pass


class Curso(CursoBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Estudiante ----------
class EstudianteBase(BaseModel):
    nombre: str
    email: EmailStr
    fecha_nacimiento: Optional[date] = None
    estado: str = Field(default="activo", pattern="^(activo|inactivo)$")


class EstudianteCreate(EstudianteBase):
    pass


class Estudiante(EstudianteBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Inscripción ----------
class InscripcionBase(BaseModel):
    estudiante_id: int
    curso_id: int
    fecha_inscripcion: date
    nota: Optional[Decimal] = Field(default=None, ge=0, le=100)
    estado: str = Field(default="inscrito", pattern="^(inscrito|aprobado|reprobado)$")


class InscripcionCreate(InscripcionBase):
    pass


class Inscripcion(InscripcionBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Esquemas para consultas (JOIN entre tablas) ----------

class EstudianteEnCurso(BaseModel):
    """Un estudiante inscrito en un curso, con su nota y estado."""
    inscripcion_id: int
    estudiante_id: int
    nombre: str
    email: str
    nota: Optional[Decimal] = None
    estado: str


class CursoDeEstudiante(BaseModel):
   
    inscripcion_id: int
    curso_id: int
    nombre_curso: str
    fecha_inscripcion: date
    nota: Optional[Decimal] = None
    estado: str


class ResumenCurso(BaseModel):
    
    curso_id: int
    nombre_curso: str
    profesor: str
    total_estudiantes: int
    promedio_nota: Optional[float] = None


class ResultadoBusqueda(BaseModel):
  
    profesores: list[Profesor]
    cursos: list[Curso]
    estudiantes: list[Estudiante]
