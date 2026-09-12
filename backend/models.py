from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Profesor(Base):
    __tablename__ = "profesor"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    especialidad = Column(String(100))

    # Un profesor imparte muchos cursos
    cursos = relationship("Curso", back_populates="profesor")


class Curso(Base):
    __tablename__ = "curso"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    profesor_id = Column(Integer, ForeignKey("profesor.id"), nullable=False)

    profesor = relationship("Profesor", back_populates="cursos")
    inscripciones = relationship("Inscripcion", back_populates="curso", cascade="all, delete-orphan")


class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")

    inscripciones = relationship("Inscripcion", back_populates="estudiante", cascade="all, delete-orphan")


class Inscripcion(Base):
    """
    Tabla intermedia que representa la relación N:N entre
    Estudiante y Curso, con atributos propios (nota, fecha, estado).
    """
    __tablename__ = "inscripcion"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "curso_id", name="uq_estudiante_curso"),
    )

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiante.id"), nullable=False)
    curso_id = Column(Integer, ForeignKey("curso.id"), nullable=False)
    fecha_inscripcion = Column(Date, nullable=False)
    nota = Column(Numeric(4, 2), nullable=True)
    estado = Column(String(20), nullable=False, default="inscrito")

    estudiante = relationship("Estudiante", back_populates="inscripciones")
    curso = relationship("Curso", back_populates="inscripciones")
