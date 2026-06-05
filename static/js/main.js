// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    
    // 1. Inicializar tooltips de Bootstrap [cite: 1261]
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(el => new bootstrap.Tooltip(el));

    // 2. Auto-cerrar alertas flash despues de 5 segundos [cite: 1265]
    // (complementa la animacion CSS de styles.css) [cite: 1266]
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    // 3. Confirmacion antes de eliminar [cite: 1275]
    // Uso en el template:
    // <button onclick="return confirmar('¿Eliminar este registro?')" form="formEliminar">Eliminar</button> [cite: 1277, 1278]
    window.confirmar = function (mensaje) {
        return confirm(mensaje || '¿Estás seguro?');
    };

    // 4. Resaltar fila al hacer clic (navegacion intuitiva en tablas) [cite: 1287]
    // Uso en la etiqueta tr del template: <tr class="fila-link" data-href="{% url 'encomienda_detalle' enc.pk %}"> [cite: 1288]
    document.querySelectorAll('.fila-link').forEach(function (fila) {
        fila.addEventListener('click', function () {
            window.location = this.dataset.href;
        });
    });

});