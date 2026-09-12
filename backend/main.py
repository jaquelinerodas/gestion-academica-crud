from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

import models
from database import engine
from routers import profesores, cursos, estudiantes, inscripciones, consultas


try:
    models.Base.metadata.create_all(bind=engine)
except OperationalError:
    print(
        "ADVERTENCIA: no se pudo conectar a la base de datos al iniciar. "
        "Verifique que PostgreSQL esté corriendo y que las credenciales "
        "en las variables de entorno (o el archivo .env) sean correctas."
    )

app = FastAPI(
    title="API Gestión Académica",
    description=(
        "CRUD persistente para Profesores, Cursos, Estudiantes e "
        "Inscripciones, con endpoints de consulta y reportes."
    ),
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(OperationalError)
async def error_conexion_bd(request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Error de conexión con la base de datos. Verifique que el servidor esté activo."}
    )


@app.get("/", tags=["Raíz"])
def raiz():
    return {"mensaje": "API de Gestión Académica funcionando correctamente"}



app.include_router(profesores.router)
app.include_router(cursos.router)
app.include_router(estudiantes.router)
app.include_router(inscripciones.router)
app.include_router(consultas.router)
