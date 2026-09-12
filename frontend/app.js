const API_URL = "http://127.0.0.1:8000";


function mostrarMensaje(texto, tipo) {
    const div = document.getElementById("mensaje");
    div.textContent = texto;
    div.className = "mensaje " + tipo;
    setTimeout(() => div.classList.add("oculto"), 3000);
}

async function manejarRespuesta(respuesta) {
    if (!respuesta.ok) {
        const error = await respuesta.json().catch(() => ({}));
        throw new Error(error.detail || "Ocurrió un error inesperado");
    }
    if (respuesta.status === 204) return null;
    return respuesta.json();
}

function limpiarFormulario(idForm, idOculto) {
    document.getElementById(idForm).reset();
    document.getElementById(idOculto).value = "";
}

const MAPA_BADGES = {
    activo: "exito",
    inactivo: "neutro",
    inscrito: "advertencia",
    aprobado: "exito",
    reprobado: "peligro",
};

function badgeEstado(estado) {
    const clase = MAPA_BADGES[estado] || "neutro";
    return `<span class="badge badge-${clase}">${estado}</span>`;
}

function activarPestana(nombre) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("activo", b.dataset.tab === nombre));
    document.querySelectorAll(".tab-contenido").forEach(t => t.classList.add("oculto"));
    document.getElementById(`tab-${nombre}`).classList.remove("oculto");
}

document.querySelectorAll(".tab-btn").forEach(boton => {
    boton.addEventListener("click", () => activarPestana(boton.dataset.tab));
});

document.querySelectorAll(".btn-cancelar").forEach(boton => {
    boton.addEventListener("click", () => {
        const form = document.getElementById(boton.dataset.form);
        form.reset();
        form.querySelector('input[type="hidden"]').value = "";
    });
});


const formProfesor = document.getElementById("form-profesor");

async function cargarProfesores() {
    const profesores = await fetch(`${API_URL}/profesores`).then(manejarRespuesta);

    document.getElementById("tabla-profesores").innerHTML = profesores.map(p => `
        <tr>
            <td class="celda-codigo">${p.id}</td><td>${p.nombre}</td><td>${p.email}</td><td>${p.especialidad ?? ""}</td>
            <td class="acciones">
                <button onclick="editarProfesor(${p.id})">Editar</button>
                <button onclick="eliminarProfesor(${p.id})">Eliminar</button>
            </td>
        </tr>`).join("");

    const select = document.getElementById("curso-profesor");
    select.innerHTML = profesores.map(p => `<option value="${p.id}">${p.nombre}</option>`).join("");

    return profesores;
}

formProfesor.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("profesor-id").value;
    const datos = {
        nombre: document.getElementById("profesor-nombre").value.trim(),
        email: document.getElementById("profesor-email").value.trim(),
        especialidad: document.getElementById("profesor-especialidad").value.trim() || null
    };
    try {
        const url = id ? `${API_URL}/profesores/${id}` : `${API_URL}/profesores`;
        await fetch(url, {
            method: id ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        }).then(manejarRespuesta);
        mostrarMensaje(id ? "Profesor actualizado" : "Profesor creado", "exito");
        limpiarFormulario("form-profesor", "profesor-id");
        await cargarProfesores();
        await cargarCursos();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
});

async function editarProfesor(id) {
    const p = await fetch(`${API_URL}/profesores/${id}`).then(manejarRespuesta);
    document.getElementById("profesor-id").value = p.id;
    document.getElementById("profesor-nombre").value = p.nombre;
    document.getElementById("profesor-email").value = p.email;
    document.getElementById("profesor-especialidad").value = p.especialidad ?? "";
}

async function eliminarProfesor(id) {
    if (!confirm("¿Eliminar este profesor?")) return;
    try {
        await fetch(`${API_URL}/profesores/${id}`, { method: "DELETE" }).then(manejarRespuesta);
        mostrarMensaje("Profesor eliminado", "exito");
        await cargarProfesores();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}


const formCurso = document.getElementById("form-curso");
let CACHE_CURSOS = [];

async function cargarCursos() {
    const [cursos, profesores] = await Promise.all([
        fetch(`${API_URL}/cursos`).then(manejarRespuesta),
        fetch(`${API_URL}/profesores`).then(manejarRespuesta)
    ]);
    CACHE_CURSOS = cursos;

    const nombreProfesor = (id) => profesores.find(p => p.id === id)?.nombre ?? "—";

    document.getElementById("tabla-cursos").innerHTML = cursos.map(c => `
        <tr>
            <td class="celda-codigo">${c.id}</td><td>${c.nombre}</td><td>${c.descripcion ?? ""}</td><td>${nombreProfesor(c.profesor_id)}</td>
            <td class="acciones">
                <button onclick="editarCurso(${c.id})">Editar</button>
                <button onclick="eliminarCurso(${c.id})">Eliminar</button>
            </td>
        </tr>`).join("");

    const select = document.getElementById("inscripcion-curso");
    select.innerHTML = cursos.map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");

    return cursos;
}

formCurso.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("curso-id").value;
    const datos = {
        nombre: document.getElementById("curso-nombre").value.trim(),
        descripcion: document.getElementById("curso-descripcion").value.trim() || null,
        profesor_id: parseInt(document.getElementById("curso-profesor").value)
    };
    if (!datos.profesor_id) {
        mostrarMensaje("Debes seleccionar un profesor", "error");
        return;
    }
    try {
        const url = id ? `${API_URL}/cursos/${id}` : `${API_URL}/cursos`;
        await fetch(url, {
            method: id ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        }).then(manejarRespuesta);
        mostrarMensaje(id ? "Curso actualizado" : "Curso creado", "exito");
        limpiarFormulario("form-curso", "curso-id");
        await cargarCursos();
        await cargarInscripciones();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
});

async function editarCurso(id) {
    const c = await fetch(`${API_URL}/cursos/${id}`).then(manejarRespuesta);
    document.getElementById("curso-id").value = c.id;
    document.getElementById("curso-nombre").value = c.nombre;
    document.getElementById("curso-descripcion").value = c.descripcion ?? "";
    document.getElementById("curso-profesor").value = c.profesor_id;
}

async function eliminarCurso(id) {
    if (!confirm("¿Eliminar este curso? También se eliminarán sus inscripciones.")) return;
    try {
        await fetch(`${API_URL}/cursos/${id}`, { method: "DELETE" }).then(manejarRespuesta);
        mostrarMensaje("Curso eliminado", "exito");
        await cargarCursos();
        await cargarInscripciones();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}


const formEstudiante = document.getElementById("form-estudiante");

async function cargarEstudiantes() {
    const estudiantes = await fetch(`${API_URL}/estudiantes`).then(manejarRespuesta);

    document.getElementById("tabla-estudiantes").innerHTML = estudiantes.map(e => `
        <tr>
            <td class="celda-codigo">${e.id}</td><td>${e.nombre}</td><td>${e.email}</td>
            <td>${e.fecha_nacimiento ?? ""}</td><td>${badgeEstado(e.estado)}</td>
            <td class="acciones">
                <button onclick="editarEstudiante(${e.id})">Editar</button>
                <button onclick="eliminarEstudiante(${e.id})">Eliminar</button>
            </td>
        </tr>`).join("");

    const select = document.getElementById("inscripcion-estudiante");
    select.innerHTML = estudiantes.map(e => `<option value="${e.id}">${e.nombre}</option>`).join("");

    return estudiantes;
}

formEstudiante.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("estudiante-id").value;
    const datos = {
        nombre: document.getElementById("estudiante-nombre").value.trim(),
        email: document.getElementById("estudiante-email").value.trim(),
        fecha_nacimiento: document.getElementById("estudiante-fecha").value || null,
        estado: document.getElementById("estudiante-estado").value
    };
    try {
        const url = id ? `${API_URL}/estudiantes/${id}` : `${API_URL}/estudiantes`;
        await fetch(url, {
            method: id ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        }).then(manejarRespuesta);
        mostrarMensaje(id ? "Estudiante actualizado" : "Estudiante creado", "exito");
        limpiarFormulario("form-estudiante", "estudiante-id");
        await cargarEstudiantes();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
});

async function editarEstudiante(id) {
    const e = await fetch(`${API_URL}/estudiantes/${id}`).then(manejarRespuesta);
    document.getElementById("estudiante-id").value = e.id;
    document.getElementById("estudiante-nombre").value = e.nombre;
    document.getElementById("estudiante-email").value = e.email;
    document.getElementById("estudiante-fecha").value = e.fecha_nacimiento ?? "";
    document.getElementById("estudiante-estado").value = e.estado;
}

async function eliminarEstudiante(id) {
    if (!confirm("¿Eliminar este estudiante? También se eliminarán sus inscripciones.")) return;
    try {
        await fetch(`${API_URL}/estudiantes/${id}`, { method: "DELETE" }).then(manejarRespuesta);
        mostrarMensaje("Estudiante eliminado", "exito");
        await cargarEstudiantes();
        await cargarInscripciones();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}


const formInscripcion = document.getElementById("form-inscripcion");

async function cargarInscripciones() {
    const [inscripciones, estudiantes, cursos] = await Promise.all([
        fetch(`${API_URL}/inscripciones`).then(manejarRespuesta),
        fetch(`${API_URL}/estudiantes`).then(manejarRespuesta),
        fetch(`${API_URL}/cursos`).then(manejarRespuesta)
    ]);

    const nombreEstudiante = (id) => estudiantes.find(e => e.id === id)?.nombre ?? "—";
    const nombreCurso = (id) => cursos.find(c => c.id === id)?.nombre ?? "—";

    document.getElementById("tabla-inscripciones").innerHTML = inscripciones.map(i => `
        <tr>
            <td class="celda-codigo">${i.id}</td><td>${nombreEstudiante(i.estudiante_id)}</td><td>${nombreCurso(i.curso_id)}</td>
            <td>${i.fecha_inscripcion}</td><td>${i.nota ?? ""}</td><td>${badgeEstado(i.estado)}</td>
            <td class="acciones">
                <button onclick="editarInscripcion(${i.id})">Editar</button>
                <button onclick="eliminarInscripcion(${i.id})">Eliminar</button>
            </td>
        </tr>`).join("");
}

formInscripcion.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("inscripcion-id").value;
    const notaValor = document.getElementById("inscripcion-nota").value;
    const datos = {
        estudiante_id: parseInt(document.getElementById("inscripcion-estudiante").value),
        curso_id: parseInt(document.getElementById("inscripcion-curso").value),
        fecha_inscripcion: document.getElementById("inscripcion-fecha").value,
        nota: notaValor !== "" ? parseFloat(notaValor) : null,
        estado: document.getElementById("inscripcion-estado").value
    };
    if (!datos.estudiante_id || !datos.curso_id || !datos.fecha_inscripcion) {
        mostrarMensaje("Estudiante, curso y fecha son obligatorios", "error");
        return;
    }
    try {
        const url = id ? `${API_URL}/inscripciones/${id}` : `${API_URL}/inscripciones`;
        await fetch(url, {
            method: id ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        }).then(manejarRespuesta);
        mostrarMensaje(id ? "Inscripción actualizada" : "Inscripción creada", "exito");
        limpiarFormulario("form-inscripcion", "inscripcion-id");
        await cargarInscripciones();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
});

async function editarInscripcion(id) {
    const i = await fetch(`${API_URL}/inscripciones/${id}`).then(manejarRespuesta);
    document.getElementById("inscripcion-id").value = i.id;
    document.getElementById("inscripcion-estudiante").value = i.estudiante_id;
    document.getElementById("inscripcion-curso").value = i.curso_id;
    document.getElementById("inscripcion-fecha").value = i.fecha_inscripcion;
    document.getElementById("inscripcion-nota").value = i.nota ?? "";
    document.getElementById("inscripcion-estado").value = i.estado;
}

async function eliminarInscripcion(id) {
    if (!confirm("¿Eliminar esta inscripción?")) return;
    try {
        await fetch(`${API_URL}/inscripciones/${id}`, { method: "DELETE" }).then(manejarRespuesta);
        mostrarMensaje("Inscripción eliminada", "exito");
        await cargarInscripciones();
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}


document.getElementById("form-buscar-estudiantes").addEventListener("submit", async (e) => {
    e.preventDefault();
    const nombre = document.getElementById("buscar-nombre").value.trim();
    const estado = document.getElementById("buscar-estado").value;

    const params = new URLSearchParams();
    if (nombre) params.set("nombre", nombre);
    if (estado) params.set("estado", estado);

    try {
        const resultados = await fetch(`${API_URL}/estudiantes?${params}`).then(manejarRespuesta);
        document.getElementById("resultado-busqueda-estudiantes").innerHTML = resultados.map(e => `
            <tr><td class="celda-codigo">${e.id}</td><td>${e.nombre}</td><td>${e.email}</td><td>${badgeEstado(e.estado)}</td></tr>
        `).join("") || `<tr><td colspan="4">Sin resultados</td></tr>`;
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
});

const selectConsultaCurso = document.getElementById("consulta-curso");

async function cargarSelectConsultaCurso() {
    selectConsultaCurso.innerHTML = CACHE_CURSOS.map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");
    if (CACHE_CURSOS.length) await mostrarRosterCurso(selectConsultaCurso.value);
}

async function mostrarRosterCurso(cursoId) {
    if (!cursoId) return;
    try {
        const roster = await fetch(`${API_URL}/consultas/cursos/${cursoId}/estudiantes`).then(manejarRespuesta);
        document.getElementById("resultado-roster-curso").innerHTML = roster.map(r => `
            <tr><td>${r.nombre}</td><td>${r.email}</td><td>${r.nota ?? "—"}</td><td>${badgeEstado(r.estado)}</td></tr>
        `).join("") || `<tr><td colspan="4">Este curso no tiene estudiantes inscritos</td></tr>`;
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}

selectConsultaCurso.addEventListener("change", (e) => mostrarRosterCurso(e.target.value));

// ---- Historial académico de un estudiante ----
const selectConsultaEstudiante = document.getElementById("consulta-estudiante");

async function cargarSelectConsultaEstudiante(estudiantes) {
    selectConsultaEstudiante.innerHTML = estudiantes.map(e => `<option value="${e.id}">${e.nombre}</option>`).join("");
    if (estudiantes.length) await mostrarHistorialEstudiante(selectConsultaEstudiante.value);
}

async function mostrarHistorialEstudiante(estudianteId) {
    if (!estudianteId) return;
    try {
        const historial = await fetch(`${API_URL}/consultas/estudiantes/${estudianteId}/historial`).then(manejarRespuesta);
        document.getElementById("resultado-historial-estudiante").innerHTML = historial.map(h => `
            <tr><td>${h.nombre_curso}</td><td>${h.fecha_inscripcion}</td><td>${h.nota ?? "—"}</td><td>${badgeEstado(h.estado)}</td></tr>
        `).join("") || `<tr><td colspan="4">Este estudiante no tiene inscripciones</td></tr>`;
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}

selectConsultaEstudiante.addEventListener("change", (e) => mostrarHistorialEstudiante(e.target.value));

// ---- Resumen por curso (agregación) ----
async function cargarResumenCursos() {
    try {
        const resumen = await fetch(`${API_URL}/consultas/resumen-cursos`).then(manejarRespuesta);
        document.getElementById("resultado-resumen-cursos").innerHTML = resumen.map(r => `
            <tr>
                <td>${r.nombre_curso}</td><td>${r.profesor}</td>
                <td>${r.total_estudiantes}</td>
                <td>${r.promedio_nota !== null ? r.promedio_nota.toFixed(2) : "—"}</td>
            </tr>
        `).join("");
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}

async function cargarConsultas() {
    const estudiantes = await fetch(`${API_URL}/estudiantes`).then(manejarRespuesta);
    await cargarSelectConsultaCurso();
    await cargarSelectConsultaEstudiante(estudiantes);
    await cargarResumenCursos();
}



async function ejecutarBusquedaGlobal() {
    const texto = document.getElementById("input-busqueda-global").value.trim();
    const panel = document.getElementById("resultados-busqueda-global");

    if (texto.length < 1) {
        mostrarMensaje("Escribe un nombre o un código para buscar", "error");
        return;
    }

    try {
        const r = await fetch(`${API_URL}/consultas/buscar?q=${encodeURIComponent(texto)}`).then(manejarRespuesta);
        const sinResultados = r.profesores.length === 0 && r.cursos.length === 0 && r.estudiantes.length === 0;

        if (sinResultados) {
            panel.innerHTML = `<div class="sin-resultados">Sin resultados para "${texto}"</div>`;
            panel.classList.remove("oculto");
            return;
        }

        const grupo = (titulo, items, tipo, render) => {
            if (!items.length) return "";
            const filas = items.map(item => `
                <button class="item-resultado" data-tipo="${tipo}" data-id="${item.id}">
                    <span class="codigo-resultado badge-${tipo}">#${item.id}</span>
                    <span class="info-resultado">${render(item)}</span>
                </button>
            `).join("");
            return `<div class="grupo-resultados"><div class="titulo-grupo">${titulo}</div>${filas}</div>`;
        };

        panel.innerHTML =
            grupo("Profesores", r.profesores, "profesor", p => `
                <span class="nombre-resultado">${p.nombre}</span>
                <span class="detalle-resultado">${p.email}</span>
            `) +
            grupo("Cursos", r.cursos, "curso", c => `
                <span class="nombre-resultado">${c.nombre}</span>
                <span class="detalle-resultado">${c.descripcion ?? "Sin descripción"}</span>
            `) +
            grupo("Estudiantes", r.estudiantes, "estudiante", e => `
                <span class="nombre-resultado">${e.nombre}</span>
                <span class="detalle-resultado">${e.email} · ${e.estado}</span>
            `);

        panel.classList.remove("oculto");

        panel.querySelectorAll(".item-resultado").forEach(boton => {
            boton.addEventListener("click", () => {
                const { tipo, id } = boton.dataset;
                const destino = { profesor: "profesores", curso: "cursos", estudiante: "estudiantes" }[tipo];
                activarPestana(destino);
                if (tipo === "profesor") editarProfesor(Number(id));
                if (tipo === "curso") editarCurso(Number(id));
                if (tipo === "estudiante") editarEstudiante(Number(id));
                panel.classList.add("oculto");
                document.getElementById("input-busqueda-global").value = "";
            });
        });
    } catch (err) {
        mostrarMensaje(err.message, "error");
    }
}

document.getElementById("btn-busqueda-global").addEventListener("click", ejecutarBusquedaGlobal);
document.getElementById("input-busqueda-global").addEventListener("keydown", (e) => {
    if (e.key === "Enter") ejecutarBusquedaGlobal();
});
document.addEventListener("click", (e) => {
    const panel = document.getElementById("resultados-busqueda-global");
    if (!panel.contains(e.target) && !document.querySelector(".buscador-global").contains(e.target)) {
        panel.classList.add("oculto");
    }
});

(async function iniciar() {
    await cargarProfesores();
    await cargarCursos();
    await cargarEstudiantes();
    await cargarInscripciones();
    await cargarConsultas();
})();
