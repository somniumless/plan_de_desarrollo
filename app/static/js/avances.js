// static/avances/js/avances.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("avances.js cargado correctamente");
    
    // 1. Variables y estado de la aplicación
    let avances = JSON.parse(localStorage.getItem('avances')) || [
        {
            id: 1,
            metaId: 101,
            meta: "Meta de Ventas Q1",
            descripcion: "Primer incremento de ventas",
            porcentaje: 65,
            fecha: "2023-03-15"
        },
        {
            id: 2,
            metaId: 102,
            meta: "Implementación Software",
            descripcion: "Fase 1 completada",
            porcentaje: 100,
            fecha: "2023-02-28"
        }
    ];
    
    let editando = false;
    let avanceEditandoId = null;
    
    // 2. Elementos del DOM
    const elementos = {
        tablaAvances: document.getElementById('tabla-avances'),
        formAvance: document.getElementById('form-avance'),
        btnGuardar: document.getElementById('guardar-avance'),
        btnCancelar: document.getElementById('cancelar-edicion'),
        campos: {
            id: document.getElementById('avance-id'),
            metaId: document.getElementById('avance-meta-id'),
            descripcion: document.getElementById('avance-descripcion'),
            porcentaje: document.getElementById('avance-porcentaje'),
            fecha: document.getElementById('avance-fecha')
        }
    };
    
    // 3. Inicialización
    function inicializar() {
        renderizarTabla();
        configurarEventListeners();
        actualizarListaMetas(); // Para el select de metas (si lo implementas)
    }
    
    // 4. Configuración de event listeners
    function configurarEventListeners() {
        elementos.formAvance.addEventListener('submit', manejarGuardarAvance);
        elementos.btnCancelar.addEventListener('click', cancelarEdicion);
    }
    
    // 5. Funciones principales
    function manejarGuardarAvance(e) {
        e.preventDefault();
        
        const avanceData = obtenerDatosFormulario();
        
        if (!validarAvance(avanceData)) {
            return;
        }
        
        if (editando) {
            actualizarAvance(avanceData);
            mostrarMensaje('Avance actualizado correctamente', 'success');
        } else {
            crearAvance(avanceData);
            mostrarMensaje('Avance creado correctamente', 'success');
        }
        
        limpiarFormulario();
        renderizarTabla();
        guardarEnLocalStorage();
    }
    
    function crearAvance(avanceData) {
        const nuevoId = avances.length > 0 ? Math.max(...avances.map(a => a.id)) + 1 : 1;
        avances.push({
            id: nuevoId,
            ...avanceData,
            meta: obtenerNombreMeta(avanceData.metaId)
        });
    }
    
    function actualizarAvance(avanceData) {
        const index = avances.findIndex(a => a.id === avanceEditandoId);
        if (index !== -1) {
            avances[index] = { 
                ...avances[index], 
                ...avanceData,
                meta: obtenerNombreMeta(avanceData.metaId)
            };
        }
        editando = false;
        avanceEditandoId = null;
    }
    
    function eliminarAvance(id) {
        if (confirm('¿Estás seguro de que deseas eliminar este avance?')) {
            avances = avances.filter(a => a.id !== id);
            
            if (editando && avanceEditandoId === id) {
                limpiarFormulario();
                editando = false;
                avanceEditandoId = null;
            }
            
            renderizarTabla();
            guardarEnLocalStorage();
            mostrarMensaje('Avance eliminado correctamente', 'success');
        }
    }
    
    // 6. Funciones de renderizado
    function renderizarTabla() {
        const tbody = elementos.tablaAvances.querySelector('tbody');
        tbody.innerHTML = '';
        
        if (avances.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay avances registrados</td></tr>';
            return;
        }
        
        avances.forEach(avance => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${avance.id}</td>
                <td>${avance.meta}</td>
                <td>${avance.descripcion}</td>
                <td>
                    <div>${avance.porcentaje}%</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: ${avance.porcentaje}%">${avance.porcentaje}%</div>
                    </div>
                </td>
                <td><i class="govco-calendar"></i> ${formatearFecha(avance.fecha)}</td>
                <td>
                    <button class="btn-icon editar" data-id="${avance.id}"><i class="govco-edit"></i> Editar</button>
                    <button class="btn-icon eliminar" data-id="${avance.id}"><i class="govco-trash-alt"></i> Eliminar</button>
                </td>
            `;
            
            tbody.appendChild(fila);
        });
        
        // Configurar eventos para los botones
        document.querySelectorAll('.editar').forEach(btn => {
            btn.addEventListener('click', () => cargarFormularioEdicion(
                parseInt(btn.getAttribute('data-id'))
            ));
        });
        
        document.querySelectorAll('.eliminar').forEach(btn => {
            btn.addEventListener('click', () => eliminarAvance(
                parseInt(btn.getAttribute('data-id'))
            ));
        });
    }
    
    function cargarFormularioEdicion(id) {
        const avance = avances.find(a => a.id === id);
        if (!avance) return;
        
        elementos.campos.id.value = avance.id;
        elementos.campos.metaId.value = avance.metaId;
        elementos.campos.descripcion.value = avance.descripcion;
        elementos.campos.porcentaje.value = avance.porcentaje;
        elementos.campos.fecha.value = avance.fecha;
        
        editando = true;
        avanceEditandoId = id;
        elementos.formAvance.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 7. Funciones de utilidad
    function obtenerDatosFormulario() {
        return {
            metaId: parseInt(elementos.campos.metaId.value),
            descripcion: elementos.campos.descripcion.value.trim(),
            porcentaje: parseInt(elementos.campos.porcentaje.value),
            fecha: elementos.campos.fecha.value
        };
    }
    
    function validarAvance(avance) {
        if (!avance.metaId || isNaN(avance.metaId)) {
            mostrarMensaje('Por favor ingresa un ID de meta válido', 'error');
            return false;
        }
        
        if (!avance.descripcion) {
            mostrarMensaje('Por favor ingresa una descripción', 'error');
            return false;
        }
        
        if (isNaN(avance.porcentaje) || avance.porcentaje < 0 || avance.porcentaje > 100) {
            mostrarMensaje('Por favor ingresa un porcentaje válido (0-100)', 'error');
            return false;
        }
        
        if (!avance.fecha) {
            mostrarMensaje('Por favor selecciona una fecha', 'error');
            return false;
        }
        
        return true;
    }
    
    function limpiarFormulario() {
        elementos.formAvance.reset();
        elementos.campos.id.value = '';
        editando = false;
        avanceEditandoId = null;
    }
    
    function cancelarEdicion() {
        limpiarFormulario();
        mostrarMensaje('Edición cancelada', 'info');
    }
    
    function formatearFecha(fechaISO) {
        const fecha = new Date(fechaISO);
        return fecha.toLocaleDateString('es-ES');
    }
    
    function obtenerNombreMeta(metaId) {
        // En una aplicación real, esto vendría de una API o base de datos
        const metas = {
            101: "Meta de Ventas Q1",
            102: "Implementación Software",
            103: "Capacitación Equipo",
            104: "Expansión Mercado"
        };
        return metas[metaId] || `Meta ID ${metaId}`;
    }
    
    function mostrarMensaje(texto, tipo) {
        // Implementación simple - puedes mejorarla con un sistema de notificaciones
        console.log(`${tipo}: ${texto}`);
        alert(`${tipo.toUpperCase()}: ${texto}`);
    }
    
    function guardarEnLocalStorage() {
        localStorage.setItem('avances', JSON.stringify(avances));
    }
    
    // 8. Inicializar la aplicación
    inicializar();
});