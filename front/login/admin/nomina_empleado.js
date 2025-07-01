document.addEventListener('DOMContentLoaded', function() {
    // Verificar si el usuario está logueado
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = '../index.html';
        return;
    }

    cargarEmpleados();
    cargarNominas();

    // Event listeners
    document.getElementById('nominaForm').addEventListener('submit', guardarNomina);
    document.getElementById('empleadoSelect').addEventListener('change', cargarDatosEmpleado);

    // Agregar event listeners para actualización en tiempo real
    ['sueldoBase', 'horasExtra', 'bonificaciones', 'descuentos'].forEach(id => {
        const input = document.getElementById(id);
        // Escuchar tanto el evento 'input' como 'change'
        input.addEventListener('input', calcularTotalNomina);
        input.addEventListener('change', calcularTotalNomina);
        input.addEventListener('keyup', calcularTotalNomina);
    });

    // Calcular totales iniciales
    calcularTotalNomina();
});

function cargarEmpleados() {
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
    const select = document.getElementById('empleadoSelect');
    select.innerHTML = '<option value="">Seleccione un empleado</option>';

    empleados.forEach(empleado => {
        const option = document.createElement('option');
        option.value = empleado.usuario;
        option.textContent = `${empleado.nombre} ${empleado.apellido}`;
        select.appendChild(option);
    });
}

function cargarDatosEmpleado() {
    const empleadoId = document.getElementById('empleadoSelect').value;
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
    const empleado = empleados.find(emp => emp.usuario === empleadoId);

    if (empleado) {
        document.getElementById('sueldoBase').value = empleado.sueldoBase || '';
        // Reiniciar otros campos
        document.getElementById('horasExtra').value = '0';
        document.getElementById('bonificaciones').value = '0';
        document.getElementById('descuentos').value = '0';
        // Calcular totales inmediatamente
        calcularTotalNomina();
    }
}

// Agregar función para formatear moneda
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

// Modificar la función calcularTotalNomina
function calcularTotalNomina() {
    // Convertir todos los valores a enteros y validar
    const sueldoBase = parseInt(document.getElementById('sueldoBase').value) || 0;
    const horasExtra = parseInt(document.getElementById('horasExtra').value) || 0;
    const bonificaciones = parseInt(document.getElementById('bonificaciones').value) || 0;
    const descuentos = parseInt(document.getElementById('descuentos').value) || 0;

    // Calcular valor de hora extra redondeado a entero
    const valorHoraExtra = Math.round((sueldoBase / 30 / 8) * 1.5);
    const totalHorasExtra = horasExtra * valorHoraExtra;
    const totalBruto = sueldoBase + totalHorasExtra + bonificaciones;
    const totalNeto = totalBruto - descuentos;

    // Actualizar los valores en tiempo real
    document.getElementById('totalBruto').value = totalBruto;
    document.getElementById('totalNeto').value = totalNeto;

    // Actualizar los valores visuales con formato de moneda
    document.getElementById('valorHoraExtra').textContent = `Valor hora extra: ${formatearMoneda(valorHoraExtra)}`;
    document.getElementById('totalHorasExtraCalc').textContent = `Total horas extra: ${formatearMoneda(totalHorasExtra)}`;
}

function guardarNomina(e) {
    e.preventDefault();

    const nomina = {
        id: Date.now(),
        empleadoId: document.getElementById('empleadoSelect').value,
        fecha: document.getElementById('fecha').value,
        sueldoBase: parseInt(document.getElementById('sueldoBase').value) || 0,
        horasExtra: parseInt(document.getElementById('horasExtra').value) || 0,
        bonificaciones: parseInt(document.getElementById('bonificaciones').value) || 0,
        descuentos: parseInt(document.getElementById('descuentos').value) || 0,
        totalBruto: parseInt(document.getElementById('totalBruto').value),
        totalNeto: parseInt(document.getElementById('totalNeto').value),
        observaciones: document.getElementById('observaciones').value
    };

    // Validaciones
    if (!nomina.empleadoId) {
        mostrarMensaje('Por favor seleccione un empleado', 'error');
        return;
    }

    if (!nomina.fecha) {
        mostrarMensaje('Por favor ingrese la fecha', 'error');
        return;
    }

    // Guardar nómina
    const nominas = JSON.parse(localStorage.getItem('nominas')) || [];
    nominas.push(nomina);
    localStorage.setItem('nominas', JSON.stringify(nominas));

    mostrarMensaje('Nómina guardada exitosamente', 'exito');
    document.getElementById('nominaForm').reset();
    cargarNominas();
}

// Modificar la función cargarNominas
function cargarNominas() {
    const nominas = JSON.parse(localStorage.getItem('nominas')) || [];
    const tbody = document.getElementById('nominasLista');
    tbody.innerHTML = '';

    nominas.forEach(nomina => {
        const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
        const empleado = empleados.find(emp => emp.usuario === nomina.empleadoId);
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${empleado ? `${empleado.nombre} ${empleado.apellido}` : 'Empleado no encontrado'}</td>
            <td>${new Date(nomina.fecha).toLocaleDateString('es-MX')}</td>
            <td>${formatearMoneda(nomina.sueldoBase)}</td>
            <td>${nomina.horasExtra} hrs</td>
            <td>${formatearMoneda(nomina.bonificaciones)}</td>
            <td>${formatearMoneda(nomina.descuentos)}</td>
            <td>${formatearMoneda(nomina.totalNeto)}</td>
            <td>
                <button onclick="editarNomina(${nomina.id})" class="btn-edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarNomina(${nomina.id})" class="btn-delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function editarNomina(id) {
    const nominas = JSON.parse(localStorage.getItem('nominas')) || [];
    const nomina = nominas.find(nom => nom.id === id);

    if (nomina) {
        document.getElementById('empleadoSelect').value = nomina.empleadoId;
        document.getElementById('fecha').value = nomina.fecha;
        document.getElementById('sueldoBase').value = nomina.sueldoBase;
        document.getElementById('horasExtra').value = nomina.horasExtra;
        document.getElementById('bonificaciones').value = nomina.bonificaciones;
        document.getElementById('descuentos').value = nomina.descuentos;
        document.getElementById('observaciones').value = nomina.observaciones;
        
        calcularTotalNomina();
        eliminarNomina(id, false);
        document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function eliminarNomina(id, confirmar = true) {
    if (confirmar && !confirm('¿Está seguro de eliminar esta nómina?')) {
        return;
    }

    const nominas = JSON.parse(localStorage.getItem('nominas')) || [];
    const nominasFiltradas = nominas.filter(nom => nom.id !== id);
    localStorage.setItem('nominas', JSON.stringify(nominasFiltradas));
    
    if (confirmar) {
        mostrarMensaje('Nómina eliminada exitosamente', 'exito');
    }
    
    cargarNominas();
}

function mostrarMensaje(texto, tipo) {
    const mensaje = document.getElementById('mensaje');
    mensaje.textContent = texto;
    mensaje.className = `mensaje ${tipo}`;
    mensaje.style.display = 'block';

    setTimeout(() => {
        mensaje.style.display = 'none';
    }, 3000);
}

// Event listeners para cálculos automáticos
['horasExtra', 'bonificaciones', 'descuentos'].forEach(id => {
    document.getElementById(id).addEventListener('input', calcularTotalNomina);
});