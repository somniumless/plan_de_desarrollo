document.addEventListener('DOMContentLoaded', () => {
    cargarAvances();

    document.getElementById('form-avance').addEventListener('submit', guardarAvance);
    document.getElementById('cancelar-edicion').addEventListener('click', limpiarFormulario);
});

function cargarAvances() {
    fetch('http://localhost:5000/api/avances')
        .then(res => res.json())
        .then(avances => {
            const tbody = document.querySelector('#tabla-avances tbody');
            tbody.innerHTML = '';
            avances.forEach(avance => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${avance.id}</td>
                    <td>${avance.meta_id}</td>
                    <td>${avance.descripcion}</td>
                    <td>${avance.porcentaje}%</td>
                    <td>${avance.fecha}</td>
                    <td>
                        <button onclick="editarAvance(${avance.id}, ${avance.meta_id}, '${avance.descripcion}', ${avance.porcentaje}, '${avance.fecha}')">Editar</button>
                        <button onclick="eliminarAvance(${avance.id})">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function guardarAvance(e) {
    e.preventDefault();
    const id = document.getElementById('avance-id').value;
    const meta_id = document.getElementById('avance-meta-id').value;
    const descripcion = document.getElementById('avance-descripcion').value;
    const porcentaje = document.getElementById('avance-porcentaje').value;
    const fecha = document.getElementById('avance-fecha').value;

    const avance = { meta_id, descripcion, porcentaje, fecha };

    if (id) {
        // Editar avance
        fetch(`http://localhost:5000/api/avances/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(avance)
        }).then(() => {
            cargarAvances();
            limpiarFormulario();
        });
    } else {
        // Crear avance
        fetch('http://localhost:5000/api/avances', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(avance)
        }).then(() => {
            cargarAvances();
            limpiarFormulario();
        });
    }
}

function editarAvance(id, meta_id, descripcion, porcentaje, fecha) {
    document.getElementById('avance-id').value = id;
    document.getElementById('avance-meta-id').value = meta_id;
    document.getElementById('avance-descripcion').value = descripcion;
    document.getElementById('avance-porcentaje').value = porcentaje;
    document.getElementById('avance-fecha').value = fecha;
    document.getElementById('cancelar-edicion').style.display = 'inline';
}

function limpiarFormulario() {
    document.getElementById('avance-id').value = '';
    document.getElementById('form-avance').reset();
    document.getElementById('cancelar-edicion').style.display = 'none';
}

function eliminarAvance(id) {
    if (confirm('¿Seguro que deseas eliminar este avance?')) {
        fetch(`http://localhost:5000/api/avances/${id}`, {
            method: 'DELETE'
        }).then(() => cargarAvances());
    }
}