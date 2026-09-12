# Gestión Académica (Estudiantes, Cursos, Profesores e Inscripciones)

## Problema que resuelve
Muchas instituciones educativas manejan la información de estudiantes,
profesores y las inscripciones a cursos usando hojas de cálculo o papel, lo
que dificulta mantener los datos actualizados, consistentes y sin
duplicados (por ejemplo, evitar que un estudiante se inscriba dos veces al
mismo curso). Esta aplicación centraliza esa información permitiendo
**crear, consultar, actualizar y eliminar** profesores, cursos, estudiantes
e inscripciones, garantizando que los datos persistan en una base de datos
real.

## Tecnologías utilizadas
- **Backend:** Python + FastAPI + SQLAlchemy
- **Base de datos:** PostgreSQL
- **Frontend:** HTML + CSS + JavaScript (sin frameworks), usando `fetch` para
  consumir la API REST. Interfaz tipo panel administrativo (barra lateral +
  contenido), tipografías Lora/IBM Plex Sans/IBM Plex Mono vía Google Fonts,
  e insignias de color para los distintos estados de los registros.
- **Documentación de la API:** Swagger UI (generado automáticamente por FastAPI)

## Estructura del repositorio
```
/frontend
    index.html
    style.css
    app.js
/backend
    main.py          
    database.py       
    models.py          
    schemas.py          
    routers/
        profesores.py     
        cursos.py          
        estudiantes.py     
        inscripciones.py   
        consultas.py       
/database
    schema.sql   -> DDL con las tablas y datos de ejemplo
README.md
```

## Modelo de datos
- **Profesor**: id, nombre, email, especialidad
- **Curso**: id, nombre, descripción, profesor_id (FK)
- **Estudiante**: id, nombre, email, fecha_nacimiento, estado
- **Inscripción**: id, estudiante_id (FK), curso_id (FK), fecha_inscripcion, nota, estado

### Relaciones
- Un **profesor** imparte muchos **cursos** (1:N).
- Un **estudiante** puede inscribirse en muchos **cursos**, y un **curso**
  puede tener muchos **estudiantes**: es una relación muchos a muchos (N:N)
  implementada mediante la tabla **Inscripción**, que además guarda
  atributos propios de la relación (nota, fecha y estado).

### Reglas de negocio implementadas
- No se puede inscribir dos veces al mismo estudiante en el mismo curso
  (restricción `UNIQUE` + validación en la API).
- No se puede eliminar un profesor que tiene cursos asignados.
- No se puede crear un curso con un profesor inexistente, ni una
  inscripción con estudiante o curso inexistente.

## Funcionalidades de consulta
Además del CRUD básico, la API permite:
- **Búsqueda y filtros**: `/estudiantes?nombre=&estado=`, `/cursos?nombre=&profesor_id=`
- **Paginación**: parámetros `skip` y `limit` en los listados
- **Roster de un curso**: `/consultas/cursos/{id}/estudiantes` — estudiantes
  inscritos en un curso, con su nota y estado (JOIN Inscripción-Estudiante)
- **Historial académico**: `/consultas/estudiantes/{id}/historial` — cursos
  en los que se ha inscrito un estudiante (JOIN Inscripción-Curso)
- **Resumen por curso**: `/consultas/resumen-cursos` — profesor a cargo,
  total de estudiantes inscritos y promedio de notas por curso (JOIN entre
  Curso, Profesor e Inscripción + funciones de agregación `COUNT` y `AVG`)
- **Búsqueda global**: `/consultas/buscar?q=texto` — busca por nombre/email
  en profesores, cursos y estudiantes; si el texto es numérico (o empieza
  con `#`), también busca por código (ID) exacto

## Cómo ejecutar el backend
1. Crear la base de datos en PostgreSQL y cargar el DDL:
   ```
   psql -U postgres -c "CREATE DATABASE gestion_academica;"
   psql -U postgres -d gestion_academica -f database/schema.sql
   ```
2. Entrar a la carpeta del backend:
   ```
   cd backend
   ```
5. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
6. Configurar la conexión a la base de datos: 
   `.env` y ajustar usuario, contraseña, host, puerto y nombre de la BD
   según  instalación local de PostgreSQL:
   ```
7. Levantar el servidor:
   ```
   uvicorn main:app --reload
   ```
8. La API quedará disponible en `http://127.0.0.1:8000`. Si PostgreSQL no
   está corriendo o las credenciales son incorrectas, el servidor igual
   arranca pero muestra una advertencia en consola, y cualquier endpoint
   que use la base de datos responderá `503` con un mensaje claro en vez
   de una traza de error.

## Cómo ejecutar el frontend
1. Entrar a la carpeta del frontend:
   ```
   cd frontend
   ```
2. Abrir el archivo `index.html` directamente en el navegador

3. Asegurarse de que el backend esté corriendo en `http://127.0.0.1:8000`,
   ya que el frontend consume esa URL (definida en `app.js` en la constante
   `API_URL`).

## Endpoints disponibles (Swagger)
Con el backend corriendo, la documentación interactiva está disponible en:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`

### Profesores
| Método | Endpoint            | Descripción                    

| GET    | /profesores         | Listar todos los profesores     
| GET    | /profesores/{id}    | Obtener un profesor por ID       
| POST   | /profesores         | Crear un profesor                
| PUT    | /profesores/{id}    | Actualizar un profesor           
| DELETE | /profesores/{id}    | Eliminar un profesor (si no tiene cursos asignados) 

### Cursos
| Método | Endpoint          | Descripción                

| GET    | /cursos           | Listar cursos (filtros `nombre`, `profesor_id`) 
| GET    | /cursos/{id}      | Obtener un curso por ID     
| POST   | /cursos           | Crear un curso               
| PUT    | /cursos/{id}      | Actualizar un curso          
| DELETE | /cursos/{id}      | Eliminar un curso            

### Estudiantes
| Método | Endpoint              | Descripción                     
| GET    | /estudiantes          | Listar estudiantes (filtros `nombre`, `estado`) 
| GET    | /estudiantes/{id}     | Obtener un estudiante por ID      
| POST   | /estudiantes          | Crear un estudiante               
| PUT    | /estudiantes/{id}     | Actualizar un estudiante           
| DELETE | /estudiantes/{id}     | Eliminar un estudiante             

### Inscripciones
| Método | Endpoint                | Descripción                          

| GET    | /inscripciones          | Listar todas las inscripciones (filtro `estado`) 
| GET    | /inscripciones/{id}     | Obtener una inscripción por ID          
| POST   | /inscripciones          | Inscribir a un estudiante en un curso   
| PUT    | /inscripciones/{id}     | Actualizar nota/estado de una inscripción 
| DELETE | /inscripciones/{id}     | Eliminar una inscripción                
### Consultas (reportes con JOIN)
| Método | Endpoint                                  | Descripción                                    

| GET    | /consultas/cursos/{id}/estudiantes         | Estudiantes inscritos en un curso, con nota y estado 
| GET    | /consultas/estudiantes/{id}/historial      | Historial académico de un estudiante           
| GET    | /consultas/resumen-cursos                  | Profesor, total de estudiantes y promedio de nota por curso 
| GET    | /consultas/buscar?q=texto                  | Búsqueda global en profesores, cursos y estudiantes 

## Manejo de errores
- `404 Not Found`: cuando se busca, actualiza o elimina un registro que no existe.
- `400 Bad Request`: cuando se intenta:
  - crear/actualizar un profesor o estudiante con un email duplicado,
  - crear/actualizar un curso con un `profesor_id` que no existe,
  - crear una inscripción con un `estudiante_id` o `curso_id` que no existe,
  - crear una inscripción duplicada (mismo estudiante y mismo curso),
  - eliminar un profesor que aún tiene cursos asignados.
- `422 Unprocessable Entity`: generado automáticamente por FastAPI cuando
  faltan campos obligatorios o los tipos de datos son incorrectos (por
  ejemplo, una nota fuera del rango 0-100).
- `503 Service Unavailable`: cuando se pierde la conexión con la base de
  datos (servidor de PostgreSQL apagado, credenciales incorrectas, etc.).
  La aplicación no se cae: responde con un mensaje claro indicando que hay
  un problema de conexión.
