// metas.js - Gestión completa de metas
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const tablaMetas = document.getElementById('tabla-metas');
    const formMeta = document.getElementById('form-meta');
    const btnCancelar = document.getElementById('cancelar-edicion');
    
    // Variables de estado
    let editMode = false;
    let currentEditId = null;

    // Cargar metas al iniciar
    cargarMetas();

    // Event Listeners
    formMeta.addEventListener('submit', manejarEnvioFormulario);
    btnCancelar.addEventListener('click', cancelarEdicion);

    // Función para cargar las metas desde la API
    async function cargarMetas() {
        try {
            const response = await fetch(API_URLS.listarMetas);
            if (!response.ok) throw new Error('Error al cargar metas');
            
            const metas = await response.json();
            renderizarMetas(metas);
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cargar las metas');
        }
    }

    // Función para renderizar las metas en la tabla
    function renderizarMetas(metas) {
        const tbody = tablaMetas.querySelector('tbody');
        tbody.innerHTML = '';

        metas.forEach(meta => {
            const tr = document.createElement('tr');
            
            // Formatear fechas para visualización
            const fechaInicio = new Date(meta.fecha_inicio).toLocaleDateString();
            const fechaFin = new Date(meta.fecha_fin).toLocaleDateString();
            const fechaRegistro = new Date(meta.fecha_registro).toLocaleDateString();

            tr.innerHTML = `
                <td>${meta.meta_id}</td>
                <td>${meta.nombre}</td>
                <td>${meta.meta_resultado}</td> <!-- <--- CAMBIA AQUÍ -->
                <td>${meta.descripcion_resultado}</td>
                <td>${meta.unidad_medida}</td>
                <td class="estado-${meta.estado ? meta.estado.toLowerCase().replace(' ', '-') : 'sin-estado'}">${meta.estado || 'Sin estado'}</td>
                <td>${fechaInicio}</td>
                <td>${fechaFin}</td>
                <td>${fechaRegistro}</td>
                <td>
                    <button class="btn-editar" data-id="${meta.meta_id}">Editar</button>
                    <button class="btn-eliminar" data-id="${meta.meta_id}">Eliminar</button>
                </td>
            `;

            tbody.appendChild(tr);
        });

        // Agregar event listeners a los botones
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', () => iniciarEdicion(btn.dataset.id));
        });

        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', () => eliminarMeta(btn.dataset.id));
        });
    }

    // Función para manejar el envío del formulario (crear/editar)
    async function manejarEnvioFormulario(e) {
        e.preventDefault();
        
        const metaData = {
            meta_id: document.getElementById('meta-id').value, 
            nombre: document.getElementById('meta-nombre').value,
            meta_resultado: document.getElementById('meta-resultado').value, // <--- CAMBIA AQUÍ
            descripcion_resultado: document.getElementById('meta-descripcion').value,
            unidad_medida: document.getElementById('meta-unidad').value,
            estado: document.getElementById('meta-estado').value,
            fecha_inicio: document.getElementById('meta-fecha-inicio').value,
            fecha_fin: document.getElementById('meta-fecha-fin').value
        };

        try {
            let response;
            if (editMode) {
                response = await fetch(`${API_URLS.actualizarMetaBase}${currentEditId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(metaData)
                });
            } else {
                response = await fetch(API_URLS.crearMeta, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(metaData)
                });
            }

            if (!response.ok) throw new Error('Error al guardar la meta');

            resetFormulario();
            cargarMetas();
            alert(`Meta ${editMode ? 'actualizada' : 'creada'} correctamente`);
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar la solicitud');
        }
    }

    // Función para iniciar el modo edición
    async function iniciarEdicion(id) {
        try {
            const response = await fetch(`${API_URLS.obtenerMetaBase}${id}`);
            if (!response.ok) throw new Error('Error al cargar meta');
            
            const meta = await response.json();
            
            // Llenar el formulario con los datos de la meta
            document.getElementById('meta-id').value = meta.meta_id;
            document.getElementById('meta-nombre').value = meta.nombre;
            document.getElementById('meta-resultado').value = meta.meta_resultado; // <--- CAMBIA AQUÍ
            document.getElementById('meta-descripcion').value = meta.descripcion_resultado;
            document.getElementById('meta-unidad').value = meta.unidad_medida;
            document.getElementById('meta-estado').value = meta.estado;
            document.getElementById('meta-fecha-inicio').value = meta.fecha_inicio.split('T')[0];
            document.getElementById('meta-fecha-fin').value = meta.fecha_fin.split('T')[0];
            
            // Cambiar a modo edición
            editMode = true;
            currentEditId = id;
            btnCancelar.style.display = 'inline-block';
            
            // Scroll al formulario
            document.querySelector('form').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cargar la meta para edición');
        }
    }

    // Función para eliminar una meta
    async function eliminarMeta(id) {
        if (!confirm('¿Estás seguro de eliminar esta meta?')) return;
        
        try {
            const response = await fetch(`${API_URLS.eliminarMetaBase}${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Error al eliminar meta');
            
            cargarMetas();
            alert('Meta eliminada correctamente');
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar la meta');
        }
    }

    // Función para cancelar la edición
    function cancelarEdicion() {
        resetFormulario();
    }

    // Función para resetear el formulario
    function resetFormulario() {
        formMeta.reset();
        editMode = false;
        currentEditId = null;
        btnCancelar.style.display = 'none';
    }
});