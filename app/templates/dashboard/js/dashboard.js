document.addEventListener('DOMContentLoaded', () => {
    cargarMetas();
    cargarAvances();
    cargarNotificaciones();
});

function cargarMetas() {
    fetch('http://localhost:5000/api/metas') // Ajusta la URL según tu backend
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('metas-container');
            container.innerHTML = '';
            data.forEach(meta => {
                const div = document.createElement('div');
                div.textContent = `${meta.nombre}: ${meta.estado}`;
                container.appendChild(div);
            });
        });
}

function cargarAvances() {
    fetch('http://localhost:5000/api/avances')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('avances-container');
            container.innerHTML = '';
            data.forEach(avance => {
                const div = document.createElement('div');
                div.textContent = `${avance.descripcion} - ${avance.porcentaje}%`;
                container.appendChild(div);
            });
        });
}

function cargarNotificaciones() {
    fetch('http://localhost:5000/api/notificaciones')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('notificaciones-list');
            list.innerHTML = '';
            data.forEach(notif => {
                const li = document.createElement('li');
                li.textContent = notif.mensaje;
                list.appendChild(li);
            });
        });
}