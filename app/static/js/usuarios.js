document.addEventListener('DOMContentLoaded', () => {
    cargarUsuarios();

    document.getElementById('form-usuario').addEventListener('submit', guardarUsuario);
    document.getElementById('cancelar-edicion').addEventListener('click', limpiarFormulario);
});

function cargarUsuarios() {
    fetch('http://localhost:5000/api/usuarios')
        .then(res => res.json())
        .then(usuarios => {
            const tbody = document.querySelector('#tabla-usuarios tbody');
            tbody.innerHTML = '';
            usuarios.forEach(usuario => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${usuario.id}</td>
                    <td>${usuario.nombre}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.rol}</td>
                    <td>
                        <button onclick="editarUsuario(${usuario.id}, '${usuario.nombre}', '${usuario.email}', '${usuario.rol}')">Editar</button>
                        <button onclick="eliminarUsuario(${usuario.id})">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function guardarUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('usuario-id').value;
    const nombre = document.getElementById('usuario-nombre').value;
    const email = document.getElementById('usuario-email').value;
    const rol = document.getElementById('usuario-rol').value;

    const usuario = { nombre, email, rol };

    if (id) {
        // Editar usuario
        fetch(`http://localhost:5000/api/usuarios/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(usuario)
        }).then(() => {
            cargarUsuarios();
            limpiarFormulario();
        });
    } else {
        // Crear usuario
        fetch('http://localhost:5000/api/usuarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(usuario)
        }).then(() => {
            cargarUsuarios();
            limpiarFormulario();
        });
    }
}

function editarUsuario(id, nombre, email, rol) {
    document.getElementById('usuario-id').value = id;
    document.getElementById('usuario-nombre').value = nombre;
    document.getElementById('usuario-email').value = email;
    document.getElementById('usuario-rol').value = rol;
    document.getElementById('cancelar-edicion').style.display = 'inline';
}

function limpiarFormulario() {
    document.getElementById('usuario-id').value = '';
    document.getElementById('form-usuario').reset();
    document.getElementById('cancelar-edicion').style.display = 'none';
}

function eliminarUsuario(id) {
    if (confirm('¿Seguro que deseas eliminar este usuario?')) {
        fetch(`http://localhost:5000/api/usuarios/${id}`, {
            method: 'DELETE'
        }).then(() => cargarUsuarios());
    }
}