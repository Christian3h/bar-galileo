document.addEventListener('DOMContentLoaded', function() {
    cargarGastos();
    configurarEventListeners();
});

function configurarEventListeners() {
    document.getElementById('save-btn').addEventListener('click', guardarGasto);
    document.getElementById('update-btn').addEventListener('click', actualizarGasto);
    document.getElementById('cancel-btn').addEventListener('click', cancelarEdicion);
    document.getElementById('buscar').addEventListener('input', buscarGastos);
}

function guardarGasto() {
    const gasto = obtenerDatosFormulario();
    if (!validarGasto(gasto)) return;

    const gastos = obtenerGastos();
    gasto.id = Date.now();
    gasto.fecha = new Date().toISOString();
    
    gastos.push(gasto);
    guardarGastos(gastos);
    
    mostrarMensaje('Gasto guardado exitosamente', 'exito');
    limpiarFormulario();
    cargarGastos();
}

function editarGasto(id) {
    const gastos = obtenerGastos();
    const gasto = gastos.find(g => g.id === id);
    
    if (gasto) {
        document.getElementById('edit-index').value = id;
        document.getElementById('nombre').value = gasto.nombre;
        document.getElementById('tipo').value = gasto.tipo;
        document.getElementById('monto').value = gasto.monto;
        
        mostrarBotonesEdicion(true);
    }
}

function actualizarGasto() {
    const id = parseInt(document.getElementById('edit-index').value);
    const gastoActualizado = obtenerDatosFormulario();
    
    if (!validarGasto(gastoActualizado)) return;

    const gastos = obtenerGastos();
    const indice = gastos.findIndex(g => g.id === id);
    
    if (indice !== -1) {
        gastos[indice] = { ...gastos[indice], ...gastoActualizado };
        guardarGastos(gastos);
        
        mostrarMensaje('Gasto actualizado exitosamente', 'exito');
        cancelarEdicion();
        cargarGastos();
    }
}

function eliminarGasto(id) {
    if (!confirm('¿Está seguro de eliminar este gasto?')) return;
    
    const gastos = obtenerGastos().filter(g => g.id !== id);
    guardarGastos(gastos);
    
    mostrarMensaje('Gasto eliminado exitosamente', 'exito');
    cargarGastos();
}

function cargarGastos(filtro = '') {
    const gastos = obtenerGastos();
    const tbody = document.getElementById('lista-gastos');
    tbody.innerHTML = '';

    const gastosFiltrados = gastos
        .filter(gasto => 
            gasto.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
            gasto.tipo.toLowerCase().includes(filtro.toLowerCase())
        )
        .sort((a, b) => b.id - a.id);

    if (gastosFiltrados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="no-datos">
                    <i class="fas fa-info-circle"></i>
                    No se encontraron gastos
                </td>
            </tr>
        `;
        return;
    }

    gastosFiltrados.forEach(gasto => {
        const tr = document.createElement('tr');
        tr.className = 'gasto-row';
        
        tr.innerHTML = `
            <td class="nombre-col">${gasto.nombre}</td>
            <td class="tipo-col">
                <span class="tipo-badge ${gasto.tipo.toLowerCase()}">
                    ${gasto.tipo}
                </span>
            </td>
            <td class="monto-col">
                ${formatearMoneda(gasto.monto)}
            </td>
            <td class="acciones-col">
                <button onclick="editarGasto(${gasto.id})" class="btn-edit" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarGasto(${gasto.id})" class="btn-delete" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Función para formatear moneda
function formatearMoneda(monto) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(monto);
}

// Funciones auxiliares
function obtenerDatosFormulario() {
    return {
        nombre: document.getElementById('nombre').value.trim(),
        tipo: document.getElementById('tipo').value,
        monto: parseInt(document.getElementById('monto').value) || 0
    };
}

function validarGasto(gasto) {
    if (!gasto.nombre) {
        mostrarMensaje('El nombre del gasto es requerido', 'error');
        return false;
    }
    if (gasto.monto <= 0) {
        mostrarMensaje('El monto debe ser mayor a 0', 'error');
        return false;
    }
    return true;
}

function mostrarBotonesEdicion(editando) {
    document.getElementById('save-btn').classList.toggle('hidden', editando);
    document.getElementById('update-btn').classList.toggle('hidden', !editando);
    document.getElementById('cancel-btn').classList.toggle('hidden', !editando);
    document.getElementById('form-title').textContent = editando ? 'Editar Gasto' : 'Agregar Gasto';
}

function cancelarEdicion() {
    limpiarFormulario();
    mostrarBotonesEdicion(false);
}

function limpiarFormulario() {
    document.getElementById('edit-index').value = '';
    document.getElementById('nombre').value = '';
    document.getElementById('tipo').value = 'Directo';
    document.getElementById('monto').value = '';
}

function formatearNumero(numero) {
    return new Intl.NumberFormat('es-MX').format(numero);
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

// Funciones de almacenamiento
function obtenerGastos() {
    return JSON.parse(localStorage.getItem('gastos')) || [];
}

function guardarGastos(gastos) {
    localStorage.setItem('gastos', JSON.stringify(gastos));
}