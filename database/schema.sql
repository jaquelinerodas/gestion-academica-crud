
CREATE TABLE IF NOT EXISTS profesor (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    especialidad VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS curso (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  VARCHAR(255),
    profesor_id  INTEGER NOT NULL,
    FOREIGN KEY (profesor_id) REFERENCES profesor(id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS estudiante (
    id                SERIAL PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    email             VARCHAR(150) NOT NULL UNIQUE,
    fecha_nacimiento  DATE,
    estado            VARCHAR(20) NOT NULL DEFAULT 'activo'
);


CREATE TABLE IF NOT EXISTS inscripcion (
    id                 SERIAL PRIMARY KEY,
    estudiante_id      INTEGER NOT NULL,
    curso_id           INTEGER NOT NULL,
    fecha_inscripcion  DATE NOT NULL,
    nota               DECIMAL(4,2),
    estado             VARCHAR(20) NOT NULL DEFAULT 'inscrito',
    FOREIGN KEY (estudiante_id) REFERENCES estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES curso(id) ON DELETE CASCADE,
    UNIQUE (estudiante_id, curso_id)  -- evita inscribir 2 veces al mismo curso
);


INSERT INTO profesor (nombre, email, especialidad) VALUES
    ('Lic. María Gómez', 'maria.gomez@universidad.edu', 'Bases de Datos'),
    ('Ing. Luis Ramírez', 'luis.ramirez@universidad.edu', 'Desarrollo Web');

INSERT INTO curso (nombre, descripcion, profesor_id) VALUES
    ('Bases de Datos I', 'Modelado y SQL básico', 1),
    ('Programación Web', 'Desarrollo con FastAPI y JavaScript', 2);

INSERT INTO estudiante (nombre, email, fecha_nacimiento, estado) VALUES
    ('Ana López', 'ana.lopez@correo.com', '2001-05-14', 'activo'),
    ('Carlos Pérez', 'carlos.perez@correo.com', '2000-11-02', 'activo');

INSERT INTO inscripcion (estudiante_id, curso_id, fecha_inscripcion, nota, estado) VALUES
    (1, 1, '2026-01-15', 85.5, 'aprobado'),
    (2, 2, '2026-01-15', NULL, 'inscrito');
