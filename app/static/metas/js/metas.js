document.addEventListener('DOMContentLoaded', () => {
 
    console.log("Valor inicial de meta-id al cargar la página:", document.getElementById('meta-id').value);

    limpiarFormulario(); 

    cargarMetas();

    document.getElementById('form-meta').addEventListener('submit', guardarMeta);
    document.getElementById('cancelar-edicion').addEventListener('click', limpiarFormulario);
    
});

function cargarMetas() {
    fetch('http://localhost:5000/api/metas') 
        .then(res => {
            if (!res.ok) {
                return res.json().then(err => { throw new Error(err.error || `Error HTTP: ${res.status} - ${res.statusText}`); });
            }
            return res.json();
        })
        .then(metas => {
            const tbody = document.querySelector('#tabla-metas tbody');
            tbody.innerHTML = '';
            metas.forEach(meta => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${meta.meta_id}</td> <td>${meta.nombre}</td>
                    <td>${meta.meta_resultado}</td> <td>${meta.descripcion_resultado}</td> <td>${meta.unidad_medida}</td> <td>${meta.estado}</td>
                    <td>${meta.fecha_inicio ? new Date(meta.fecha_inicio).toLocaleDateString() : ''}</td>
                    <td>${meta.fecha_fin ? new Date(meta.fecha_fin).toLocaleDateString() : ''}</td>
                    <td>${meta.fecha_registro ? new Date(meta.fecha_registro).toLocaleDateString() : ''}</td>
                    <td>
                        <button onclick="editarMeta('${meta.meta_id}', '${meta.nombre}', '${meta.meta_resultado}', '${meta.descripcion_resultado}', '${meta.unidad_medida}', '${meta.estado}', '${meta.fecha_inicio}', '${meta.fecha_fin}')">Editar</button>
                        <button onclick="eliminarMeta('${meta.meta_id}')">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error al cargar metas:', error);
            alert('No se pudieron cargar las metas. Intenta de nuevo más tarde.');
        });
}

function guardarMeta(e) {
    e.preventDefault();
    const metaId = document.getElementById('meta-id').value; 
    const nombre = document.getElementById('meta-nombre').value;
    const metaResultado = document.getElementById('meta-resultado').value; 
    const descripcionResultado = document.getElementById('meta-descripcion').value;
    const unidadMedida = document.getElementById('meta-unidad').value;
    const fechaInicio = document.getElementById('meta-fecha-inicio').value;
    const fechaFin = document.getElementById('meta-fecha-fin').value;
    const estado = document.getElementById('meta-estado').value;

    const metaData = { 
        meta_id: metaId, 
        nombre: nombre,
        meta_resultado: metaResultado,
        descripcion_resultado: descripcionResultado,
        unidad_medida: unidadMedida,
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        estado: estado 
    };

    let url;
    let method;

    if (metaId) { 
        url = `http://localhost:5000/api/metas/${metaId}`; 
        method = 'PUT';
        console.log(`DEBUG JS: Preparando PUT request a ${url} con datos:`, metaData); 
    } else { 
        url = 'http://localhost:5000/api/metas'; 
        method = 'POST';
        console.log(`DEBUG JS: Preparando POST request a ${url} con datos:`, metaData); 
    }

    fetch(url, {
        method: method,
        headers: { 
            'Content-Type': 'application/json' 
        },
        body: JSON.stringify(metaData)
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { 
                console.error('Error en la respuesta del servidor:', err); 
                throw new Error(err.error || `Error HTTP: ${res.status}`); 
            });
        }
        return res.json();
    })
    .then(data => {
        alert(data.mensaje || 'Operación exitosa.');
        cargarMetas();
        limpiarFormulario();
    })
    .catch(error => {
        console.error('Error al guardar la meta:', error);
        alert('Error al guardar la meta: ' + error.message);
    });
}

function editarMeta(id, nombre, metaResultado, descripcionResultado, unidadMedida, estado, fechaInicio, fechaFin) {
    document.getElementById('meta-id').value = id;
    document.getElementById('meta-nombre').value = nombre;
    document.getElementById('meta-resultado').value = metaResultado;
    document.getElementById('meta-descripcion').value = descripcionResultado;
    document.getElementById('meta-unidad').value = unidadMedida;
    document.getElementById('meta-estado').value = estado;
    document.getElementById('meta-fecha-inicio').value = fechaInicio; 
    document.getElementById('meta-fecha-fin').value = fechaFin;
    document.getElementById('cancelar-edicion').style.display = 'inline';
    
    document.getElementById('meta-id').readOnly = true; 
    document.getElementById('meta-id').disabled = false; 
}

function limpiarFormulario() {
    document.getElementById('meta-id').value = ''; 
    document.getElementById('form-meta').reset(); 
    document.getElementById('cancelar-edicion').style.display = 'none';
    
    document.getElementById('meta-id').readOnly = false; 
    document.getElementById('meta-id').disabled = false;
}

function eliminarMeta(id) {
    if (confirm('¿Seguro que deseas eliminar esta meta?')) {
        fetch(`http://localhost:5000/api/metas/${id}`, {
            method: 'DELETE'
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(err => { throw new Error(err.error || `Error HTTP: ${res.status}`); });
            }
            return res.json();
        })
        .then(data => {
            alert(data.mensaje || 'Meta eliminada exitosamente.');
            cargarMetas();
        })
        .catch(error => {
            console.error('Error al eliminar la meta:', error);
            alert('Error al eliminar la meta: ' + error.message);
        });
    }
}