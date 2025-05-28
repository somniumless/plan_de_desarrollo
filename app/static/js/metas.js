// metas.js - Gestión completa de metas
 
const API_URLS = {
    listarMetas: "/api/metas",
    crearMeta: "/api/metas/crear",
    obtenerMetaBase: "/api/metas/", 
    actualizarMetaBase: "/api/metas/", 
    eliminarMetaBase: "/api/metas/" 
};

const ESTADO_META_VALUES = [
    "Pendiente",
    "En progreso",
    "Completada"
];

/**
 * Parsea una cadena de fecha YYYY-MM-DD y crea un objeto Date en la zona horaria local.
 * @param {string} dateString - La cadena de fecha en formato YYYY-MM-DD.
 * @returns {Date|null} Un objeto Date local o null si la cadena es inválida/vacía.
 */
function parseLocalDate(dateString) {
    if (!dateString) return null;
    const parts = dateString.split('-');
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; 
    const day = parseInt(parts[2], 10);
    return new Date(year, month, day);
}


document.addEventListener('DOMContentLoaded', function() {
    const tablaMetas = document.getElementById('tabla-metas');
    const formMeta = document.getElementById('form-meta');
    const btnCancelar = document.getElementById('cancelar-edicion');
    
    const metaIdInput = document.getElementById('meta-id');
    const metaNombreInput = document.getElementById('meta-nombre');
    const metaResultadoInput = document.getElementById('meta-resultado');
    const metaDescripcionInput = document.getElementById('meta-descripcion');
    const metaUnidadInput = document.getElementById('meta-unidad');
    const metaFechaInicioInput = document.getElementById('meta-fecha-inicio');
    const metaFechaFinInput = document.getElementById('meta-fecha-fin');
    const metaEstadoSelect = document.getElementById('meta-estado');

    let editMode = false;
    let currentEditId = null;

    cargarMetas();

    formMeta.addEventListener('submit', manejarEnvioFormulario);
    btnCancelar.addEventListener('click', cancelarEdicion);

    async function cargarMetas() {
        try {
            const response = await fetch(API_URLS.listarMetas);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error al cargar metas: ${response.status} - ${errorText}`);
            }
            
            const metas = await response.json();
            renderizarMetas(metas);
        } catch (error) {
            console.error('Error al cargar metas:', error);
            alert(`Error al cargar las metas: ${error.message}`);
            tablaMetas.querySelector('tbody').innerHTML = `<tr><td colspan="10">No se pudieron cargar las metas. Intente de nuevo.</td></tr>`;
        }
    }

    /**
     * Renderiza las metas en la tabla HTML.
     * @param {Array<Object>} metas - Array de objetos de meta.
     */
    function renderizarMetas(metas) {
        const tbody = tablaMetas.querySelector('tbody');
        tbody.innerHTML = '';

        if (metas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10">No hay metas registradas.</td></tr>`;
            return;
        }

        metas.forEach(meta => {
            const tr = document.createElement('tr');
            const fechaInicioObj = parseLocalDate(meta.fecha_inicio);
            const fechaInicio = fechaInicioObj ? fechaInicioObj.toLocaleDateString('es-CO') : 'N/A';
            const fechaFinObj = parseLocalDate(meta.fecha_fin);
            const fechaFin = fechaFinObj ? fechaFinObj.toLocaleDateString('es-CO') : 'N/A';
            const fechaRegistro = meta.fecha_registro ? new Date(meta.fecha_registro).toLocaleDateString('es-CO') : 'N/A';

            tr.innerHTML = `
                <td>${meta.meta_id || 'N/A'}</td>
                <td>${meta.nombre || 'N/A'}</td>
                <td>${meta.meta_resultado || 'N/A'}</td> 
                <td>${meta.descripcion_resultado || 'N/A'}</td>
                <td>${meta.unidad_medida || 'N/A'}</td>
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

        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', () => iniciarEdicion(btn.dataset.id));
        });

        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', () => eliminarMeta(btn.dataset.id));
        });
    }

    /**
     * Maneja el envío del formulario, ya sea para crear o actualizar una meta.
     * @param {Event} e - El evento de envío del formulario.
     */
    async function manejarEnvioFormulario(e) {
        e.preventDefault();
        
        const metaData = {
            meta_id: metaIdInput.value, 
            nombre: metaNombreInput.value,
            resultado_esperado: metaResultadoInput.value, 
            descripcion_resultado: metaDescripcionInput.value,
            unidad_medida: metaUnidadInput.value,
            estado: metaEstadoSelect.value,
            fecha_inicio: metaFechaInicioInput.value, 
            fecha_fin: metaFechaFinInput.value      
        };

        try {
            let response;
            if (editMode) {
                if (!currentEditId) {
                    throw new Error('ID de meta no definido para la edición.');
                }
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

            if (!response.ok) {
                const errorData = await response.json(); 
                throw new Error(errorData.message || `Error al guardar la meta: ${response.status}`);
            }

            resetFormulario();
            cargarMetas();
            alert(`Meta ${editMode ? 'actualizada' : 'creada'} correctamente`);
        } catch (error) {
            console.error('Error al procesar la solicitud:', error);
            alert(`Error al procesar la solicitud: ${error.message}`);
        }
    }

    /**
     * Carga los datos de una meta para su edición en el formulario.
     * @param {string} id - El ID de la meta a editar.
     */
    async function iniciarEdicion(id) {
        try {
            const response = await fetch(`${API_URLS.obtenerMetaBase}${id}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error al cargar meta para edición: ${response.status} - ${errorText}`);
            }
            
            const meta = await response.json();
            
            metaIdInput.value = meta.meta_id || ''; 
            metaIdInput.readOnly = true; 
            metaNombreInput.value = meta.nombre || '';
            metaResultadoInput.value = meta.meta_resultado || ''; 
            metaDescripcionInput.value = meta.descripcion_resultado || '';
            metaUnidadInput.value = meta.unidad_medida || '';
            metaEstadoSelect.value = meta.estado || 'Pendiente'; 
            metaFechaInicioInput.value = meta.fecha_inicio || '';
            metaFechaFinInput.value = meta.fecha_fin || '';
            
            editMode = true;
            currentEditId = id; 
            btnCancelar.style.display = 'inline-block';
            formMeta.querySelector('button[type="submit"]').textContent = 'Actualizar';
            
            document.querySelector('form').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error al iniciar edición:', error);
            alert(`Error al cargar la meta para edición: ${error.message}`);
        }
    }

    /**
     * Elimina una meta por su ID.
     * @param {string} id - El ID de la meta a eliminar.
     */
    async function eliminarMeta(id) {
        if (!confirm('¿Estás seguro de eliminar esta meta?')) return;
        
        try {
            const response = await fetch(`${API_URLS.eliminarMetaBase}${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error al eliminar meta: ${response.status} - ${errorText}`);
            }
            cargarMetas();
            alert('Meta eliminada correctamente');
        } catch (error) {
            console.error('Error al eliminar meta:', error);
            alert(`Error al eliminar la meta: ${error.message}`);
        }
    }

    function cancelarEdicion() {
        resetFormulario();
    }

    function resetFormulario() {
        formMeta.reset();
        metaIdInput.readOnly = false; 
        editMode = false;
        currentEditId = null;
        btnCancelar.style.display = 'none';
        formMeta.querySelector('button[type="submit"]').textContent = 'Guardar'; 
    }
});