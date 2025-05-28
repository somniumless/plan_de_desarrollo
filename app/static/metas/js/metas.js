document.addEventListener('DOMContentLoaded', () => {
    // Añade esta línea:
    console.log("Valor inicial de meta-id al cargar la página:", document.getElementById('meta-id').value);

    cargarMetas();

    document.getElementById('form-meta').addEventListener('submit', guardarMeta);
    document.getElementById('cancelar-edicion').addEventListener('click', limpiarFormulario);
});

function cargarMetas() {
    // Es mejor usar las URLs dinámicas de API_URLS si ya las tienes definidas en HTML
    // fetch(API_URLS.listarMetas) 
    fetch('http://localhost:5000/api/metas') // Usando localhost explícitamente para coincidir con la config del servidor
        .then(res => {
            if (!res.ok) {
                // Si la respuesta no es 2xx, lanza un error
                throw new Error(`Error HTTP: ${res.status} - ${res.statusText}`);
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
            // Opcional: mostrar un mensaje al usuario en la UI
            alert('No se pudieron cargar las metas. Intenta de nuevo más tarde.');
        });
}

function guardarMeta(e) {
    e.preventDefault();
    const metaId = document.getElementById('meta-id').value; // Usar metaId para claridad
    const nombre = document.getElementById('meta-nombre').value;
    const metaResultado = document.getElementById('meta-resultado').value; // Nuevo campo
    const descripcionResultado = document.getElementById('meta-descripcion').value; // Nuevo campo
    const unidadMedida = document.getElementById('meta-unidad').value; // Nuevo campo
    const fechaInicio = document.getElementById('meta-fecha-inicio').value;
    const fechaFin = document.getElementById('meta-fecha-fin').value;
    const estado = document.getElementById('meta-estado').value;

    const metaData = { 
        meta_id: metaId, // Asegúrate de incluir el ID para la creación (si aplica)
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

    if (metaId) { // Si hay un ID en el formulario, es una actualización (PUT)
        url = `http://localhost:5000/api/metas/${metaId}`; // La URL correcta para PUT
        method = 'PUT';
    } else { // Si no hay ID, es una creación (POST)
        url = 'http://localhost:5000/api/metas'; // La URL correcta para POST
        method = 'POST';
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
            // Intenta leer el mensaje de error del servidor si es un JSON
            return res.json().then(err => { throw new Error(err.error || `Error HTTP: ${res.status}`); });
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

// Actualizada la función editarMeta para incluir todos los campos
function editarMeta(id, nombre, metaResultado, descripcionResultado, unidadMedida, estado, fechaInicio, fechaFin) {
    document.getElementById('meta-id').value = id;
    document.getElementById('meta-nombre').value = nombre;
    document.getElementById('meta-resultado').value = metaResultado;
    document.getElementById('meta-descripcion').value = descripcionResultado;
    document.getElementById('meta-unidad').value = unidadMedida;
    document.getElementById('meta-estado').value = estado;
    document.getElementById('meta-fecha-inicio').value = fechaInicio; // Las fechas ya vienen en formato 'YYYY-MM-DD'
    document.getElementById('meta-fecha-fin').value = fechaFin;
    document.getElementById('cancelar-edicion').style.display = 'inline';
}

function limpiarFormulario() {
    document.getElementById('meta-id').value = '';
    document.getElementById('form-meta').reset();
    document.getElementById('cancelar-edicion').style.display = 'none';
    // Opcional: Deshabilita el campo ID para nuevas creaciones si no quieres que el usuario lo edite
    // document.getElementById('meta-id').disabled = false;
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