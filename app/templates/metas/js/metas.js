document.addEventListener('DOMContentLoaded', () => {
    cargarMetas();

    document.getElementById('form-meta').addEventListener('submit', guardarMeta);
    document.getElementById('cancelar-edicion').addEventListener('click', limpiarFormulario);
});

function cargarMetas() {
    fetch('http://localhost:5000/api/metas')
        .then(res => res.json())
        .then(metas => {
            const tbody = document.querySelector('#tabla-metas tbody');
            tbody.innerHTML = '';
            metas.forEach(meta => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${meta.id}</td>
                    <td>${meta.nombre}</td>
                    <td>${meta.descripcion}</td>
                    <td>${meta.estado}</td>
                    <td>
                        <button onclick="editarMeta(${meta.id}, '${meta.nombre}', '${meta.descripcion}', '${meta.estado}')">Editar</button>
                        <button onclick="eliminarMeta(${meta.id})">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function guardarMeta(e) {
    e.preventDefault();
    const id = document.getElementById('meta-id').value;
    const nombre = document.getElementById('meta-nombre').value;
    const descripcion = document.getElementById('meta-descripcion').value;
    const estado = document.getElementById('meta-estado').value;

    const meta = { nombre, descripcion, estado };

    if (id) {
        // Editar meta
        fetch(`http://localhost:5000/api/metas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(meta)
        }).then(() => {
            cargarMetas();
            limpiarFormulario();
        });
    } else {
        // Crear meta
        fetch('http://localhost:5000/api/metas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(meta)
        }).then(() => {
            cargarMetas();
            limpiarFormulario();
        });
    }
}

function editarMeta(id, nombre, descripcion, estado) {
    document.getElementById('meta-id').value = id;
    document.getElementById('meta-nombre').value = nombre;
    document.getElementById('meta-descripcion').value = descripcion;
    document.getElementById('meta-estado').value = estado;
    document.getElementById('cancelar-edicion').style.display = 'inline';
}

function limpiarFormulario() {
    document.getElementById('meta-id').value = '';
    document.getElementById('form-meta').reset();
    document.getElementById('cancelar-edicion').style.display = 'none';
}

function eliminarMeta(id) {
    if (confirm('¿Seguro que deseas eliminar esta meta?')) {
        fetch(`http://localhost:5000/api/metas/${id}`, {
            method: 'DELETE'
        }).then(() => cargarMetas());
    }
}