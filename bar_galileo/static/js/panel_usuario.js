/* =======================================
   JAVASCRIPT DEL PANEL DE USUARIO
======================================= */

// Mostrar/ocultar formularios de edición
function toggleInfoForm(show) {
    const infoDisplay = document.getElementById('info-display');
    const infoForm = document.getElementById('info-form');

    if (show) {
        infoDisplay.style.display = 'none';
        infoForm.style.display = 'block';
        infoForm.classList.remove('hidden-form');
    } else {
        infoDisplay.style.display = 'block';
        infoForm.style.display = 'none';
        infoForm.classList.add('hidden-form');
    }
}

function toggleEmergenciaForm(show) {
    const emergenciaDisplay = document.getElementById('emergencia-display');
    const emergenciaForm = document.getElementById('emergencia-form');

    if (show) {
        emergenciaDisplay.style.display = 'none';
        emergenciaForm.style.display = 'block';
        emergenciaForm.classList.remove('hidden-form');
    } else {
        emergenciaDisplay.style.display = 'block';
        emergenciaForm.style.display = 'none';
        emergenciaForm.classList.add('hidden-form');
    }
}

// Ocultar mensajes de éxito después de 3.5 segundos
function hideSuccessMessages() {
    setTimeout(function() {
        document.querySelectorAll('.alert-success').forEach(function(el) {
            el.style.display = 'none';
        });
    }, 3500);
}

// Validación del formulario de información personal
function validarInfoForm() {
    let nombre = document.querySelector('input[name="nombre"]').value.trim();
    let cedula = document.querySelector('input[name="cedula"]').value.trim();
    let telefono = document.querySelector('input[name="telefono"]').value.trim();
    let email = document.querySelector('input[name="email"]').value.trim();
    let errores = [];

    if (nombre.length < 3) {
        errores.push('El nombre debe tener al menos 3 caracteres.');
    }
    if (!/^\d{6,}$/.test(cedula)) {
        errores.push('La cédula debe ser numérica y tener al menos 6 dígitos.');
    }
    if (!/^\d{10}$/.test(telefono)) {
        errores.push('El teléfono debe ser numérico y tener exactamente 10 dígitos.');
    }
    if (!email.includes('@')) {
        errores.push('El email debe ser válido.');
    }

    if (errores.length) {
        alert(errores.join('\n'));
        return false;
    }
    return true;
}

// Validación del formulario de contacto de emergencia
function validarEmergenciaForm() {
    let nombre = document.querySelector('input[name="emergencia_nombre"]').value.trim();
    let telefono = document.querySelector('input[name="emergencia_telefono"]').value.trim();
    let telefono_alt = document.querySelector('input[name="emergencia_telefono_alt"]').value.trim();
    let errores = [];

    if (nombre.length < 3) {
        errores.push('El nombre de emergencia debe tener al menos 3 caracteres.');
    }
    if (telefono && !/^\d{10}$/.test(telefono)) {
        errores.push('El teléfono debe ser numérico y tener exactamente 10 dígitos.');
    }
    if (telefono_alt && !/^\d{10}$/.test(telefono_alt)) {
        errores.push('El teléfono alternativo debe ser numérico y tener exactamente 10 dígitos.');
    }

    if (errores.length) {
        alert(errores.join('\n'));
        return false;
    }
    return true;
}

// Formatear precio en formato colombiano
function formatPrice(number) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(number);
}

// Actualizar la cuenta actual en el DOM
function updateCuentaActual(cuenta) {
    const billAmount = document.querySelector('.bill-amount');
    const billDetails = document.querySelector('.bill-details');

    if (billAmount) {
        billAmount.textContent = formatPrice(cuenta.total);
    }

    if (billDetails) {
        let itemsHtml = '';
        if (cuenta.items && cuenta.items.length > 0) {
            cuenta.items.forEach(item => {
                itemsHtml += `
                    <div class="bill-item">
                        <span>${item.nombre}</span>
                        <span>${formatPrice(item.precio)}</span>
                    </div>
                `;
            });
        }

        itemsHtml += `
            <div class="bill-item">
                <span><span class="status-indicator"></span>Total a Pagar</span>
                <span>${formatPrice(cuenta.total)}</span>
            </div>
        `;
        billDetails.innerHTML = itemsHtml;
    }
}

// Inicializar WebSocket para actualizaciones en tiempo real
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/panel/`);

    ws.onopen = function() {
        console.log("WebSocket connection for panel established.");
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.cuenta_actual) {
            updateCuentaActual(data.cuenta_actual);
        }
    };

    ws.onclose = function() {
        console.log("WebSocket connection for panel closed.");
    };

    ws.onerror = function(error) {
        console.error("WebSocket error:", error);
    };
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Ocultar mensajes de éxito
    hideSuccessMessages();

    // Asociar validaciones a los formularios
    const infoForm = document.getElementById('info-form');
    if (infoForm) {
        infoForm.onsubmit = validarInfoForm;
    }

    const emergenciaForm = document.getElementById('emergencia-form');
    if (emergenciaForm) {
        emergenciaForm.onsubmit = validarEmergenciaForm;
    }

    // Inicializar WebSocket
    initWebSocket();
});
