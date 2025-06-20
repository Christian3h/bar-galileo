// Verificar si el usuario está autenticado
document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = '../../../index.html';
        return;
    }

    // Cargar datos guardados
    cargarDatosGuardados();

    // Manejar cierre de sesión
    document.getElementById('cerrarSesion').addEventListener('click', function() {
        localStorage.removeItem('isLoggedIn');
        window.location.href = '../../../index.html';
    });
});

// Función para mostrar/ocultar formularios
function mostrarFormulario(tipo) {
    const formularios = document.querySelectorAll('.formulario-edicion');
    formularios.forEach(form => form.classList.remove('visible'));
    
    const formulario = document.getElementById(`form${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`);
    formulario.classList.add('visible');
}

// Función para cerrar formularios
function cerrarFormulario(tipo) {
    document.getElementById('form' + tipo).classList.remove('visible');
    if (tipo === 'Stock') {
        limpiarFormularioStock();
    }
}

// Función para actualizar ventas
function actualizarVentas() {
    const ventas = parseFloat(document.getElementById('inputVentas').value) || 0;
    document.getElementById('totalVentas').textContent = ventas.toLocaleString();
    
    // Guardar datos
    const datos = obtenerDatosGuardados();
    datos.ventas = ventas;
    guardarDatos(datos);
    
    // Ocultar formulario
    document.getElementById('formVentas').classList.remove('visible');
    
    // Actualizar gráfico
    actualizarGrafico();
    calcularGanancias();
}

// Funciones para manejar productos
function guardarProducto() {
    const nuevoProducto = {
        nombre: document.getElementById('inputProducto').value.trim(),
        codigo: document.getElementById('inputCodigo').value.trim(),
        cantidad: parseInt(document.getElementById('inputCantidad').value) || 0,
        precioCompra: parseFloat(document.getElementById('inputPrecioCompra').value) || 0,
        precioVenta: parseFloat(document.getElementById('inputPrecioVenta').value) || 0
    };

    // Validar campos requeridos
    if (!nuevoProducto.nombre || !nuevoProducto.codigo) {
        mostrarMensaje('Por favor complete los campos nombre y código', 'error');
        return;
    }

    // Validar cantidad y precios
    if (nuevoProducto.cantidad <= 0) {
        mostrarMensaje('La cantidad debe ser mayor a 0', 'error');
        return;
    }

    if (nuevoProducto.precioCompra <= 0 || nuevoProducto.precioVenta <= 0) {
        mostrarMensaje('Los precios deben ser mayores a 0', 'error');
        return;
    }

    const datos = obtenerDatosGuardados();
    const productos = datos.productos || [];
    const codigoOriginal = document.getElementById('inputCodigo').dataset.originalCode;
    
    // Verificar si el código ya existe
    const productoExistente = productos.find(p => p.codigo === nuevoProducto.codigo);
    
    // Si estamos editando un producto
    if (codigoOriginal) {
        // Si el código nuevo es diferente al original y ya existe
        if (nuevoProducto.codigo !== codigoOriginal && productoExistente) {
            mostrarMensaje(`El código ${nuevoProducto.codigo} ya está en uso por otro producto`, 'error');
            return;
        }
        
        // Actualizar producto existente
        const index = productos.findIndex(p => p.codigo === codigoOriginal);
        if (index !== -1) {
            productos[index] = nuevoProducto;
            mostrarMensaje('Producto actualizado correctamente', 'exito');
        }
    } else {
        // Si es un producto nuevo y el código ya existe
        if (productoExistente) {
            mostrarMensaje(`No se puede guardar: El código ${nuevoProducto.codigo} ya existe en otro producto`, 'error');
            return;
        }
        // Agregar nuevo producto
        productos.push(nuevoProducto);
        mostrarMensaje('Producto agregado correctamente', 'exito');
    }

    // Guardar cambios
    datos.productos = productos;
    guardarDatos(datos);
    
    // Actualizar interfaz
    actualizarListaProductos();
    actualizarTotalStock();
    calcularGanancias();
    limpiarFormularioStock();
    cerrarFormulario('Stock');
}

function editarProducto(codigo) {
    const datos = obtenerDatosGuardados();
    const producto = datos.productos.find(p => p.codigo === codigo);
    
    if (producto) {
        // Mostrar el formulario
        mostrarFormulario('stock');
        
        // Llenar el formulario con los datos del producto
        document.getElementById('inputProducto').value = producto.nombre;
        document.getElementById('inputCodigo').value = producto.codigo;
        document.getElementById('inputCantidad').value = producto.cantidad;
        document.getElementById('inputPrecioCompra').value = producto.precioCompra;
        document.getElementById('inputPrecioVenta').value = producto.precioVenta;
        
        // Guardar el código original para la actualización
        document.getElementById('inputCodigo').dataset.originalCode = producto.codigo;
    }
}

function limpiarFormularioStock() {
    document.getElementById('inputProducto').value = '';
    document.getElementById('inputCodigo').value = '';
    document.getElementById('inputCantidad').value = '';
    document.getElementById('inputPrecioCompra').value = '';
    document.getElementById('inputPrecioVenta').value = '';
    document.getElementById('buscarProducto').value = '';
    // Limpiar el código original
    delete document.getElementById('inputCodigo').dataset.originalCode;
}

function buscarProducto() {
    const searchTerm = document.getElementById('buscarProducto').value.toLowerCase();
    const datos = obtenerDatosGuardados();
    const productos = datos.productos || [];
    const productoEncontrado = productos.find(p => 
        p.nombre.toLowerCase().includes(searchTerm) || 
        p.codigo.toLowerCase().includes(searchTerm)
    );

    if (productoEncontrado) {
        // Llenar el formulario con los datos del producto encontrado
        document.getElementById('inputProducto').value = productoEncontrado.nombre;
        document.getElementById('inputCodigo').value = productoEncontrado.codigo;
        document.getElementById('inputCantidad').value = productoEncontrado.cantidad;
        document.getElementById('inputPrecioCompra').value = productoEncontrado.precioCompra;
        document.getElementById('inputPrecioVenta').value = productoEncontrado.precioVenta;
        
        // Guardar el código original para la actualización
        document.getElementById('inputCodigo').dataset.originalCode = productoEncontrado.codigo;
    } else {
        alert('Producto no encontrado');
    }
}

function eliminarProducto(codigo) {
    if (confirm('¿Está seguro de que desea eliminar este producto?')) {
        const datos = obtenerDatosGuardados();
        datos.productos = datos.productos.filter(p => p.codigo !== codigo);
        guardarDatos(datos);
        actualizarListaProductos();
        actualizarTotalStock();
    }
}

function actualizarListaProductos() {
    const datos = obtenerDatosGuardados();
    const listaProductos = document.getElementById('listaProductos');
    listaProductos.innerHTML = '';

    if (datos.productos && datos.productos.length > 0) {
        datos.productos.forEach(producto => {
            const itemProducto = document.createElement('div');
            itemProducto.className = 'item-lista';
            itemProducto.innerHTML = `
                <div class="producto-info">
                    <h4>${producto.nombre}</h4>
                    <p><strong>Código:</strong> ${producto.codigo}</p>
                    <p><strong>Cantidad:</strong> ${producto.cantidad}</p>
                    <p><strong>Precio Compra:</strong> $${producto.precioCompra}</p>
                    <p><strong>Precio Venta:</strong> $${producto.precioVenta}</p>
                </div>
                <div class="producto-acciones">
                    <button onclick="editarProducto('${producto.codigo}')" class="btn-accion btn-editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="eliminarProducto('${producto.codigo}')" class="btn-accion btn-eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            listaProductos.appendChild(itemProducto);
        });
    } else {
        listaProductos.innerHTML = '<p class="no-items">No hay productos en el stock</p>';
    }
}

function actualizarTotalStock() {
    const datos = obtenerDatosGuardados();
    const totalStock = datos.productos ? datos.productos.reduce((total, producto) => total + producto.cantidad, 0) : 0;
    document.getElementById('totalStock').textContent = totalStock.toLocaleString();
}

// Funciones para manejar gastos
function agregarGasto() {
    const gasto = {
        descripcion: document.getElementById('inputDescripcionGasto').value,
        monto: parseFloat(document.getElementById('inputMontoGasto').value) || 0,
        fecha: new Date().toISOString()
    };

    if (!gasto.descripcion || gasto.monto <= 0) {
        alert('Por favor complete todos los campos correctamente');
        return;
    }

    // Guardar gasto
    const datos = obtenerDatosGuardados();
    datos.gastos = datos.gastos || [];
    datos.gastos.push(gasto);
    guardarDatos(datos);

    // Actualizar interfaz
    actualizarListaGastos();
    actualizarTotalGastos();
    calcularGanancias();

    // Limpiar formulario
    document.getElementById('formGastos').reset();
    document.getElementById('formGastos').classList.remove('visible');
}

function actualizarListaGastos() {
    const datos = obtenerDatosGuardados();
    const listaGastos = document.getElementById('listaGastos');
    listaGastos.innerHTML = '';

    if (datos.gastos && datos.gastos.length > 0) {
        datos.gastos.forEach((gasto, index) => {
            const item = document.createElement('div');
            item.className = 'item-lista';
            item.innerHTML = `
                <p><strong>${gasto.descripcion}</strong></p>
                <p>Monto: $${gasto.monto.toLocaleString()}</p>
                <p>Fecha: ${new Date(gasto.fecha).toLocaleDateString()}</p>
                <button onclick="eliminarGasto(${index})" class="btn-eliminar">Eliminar</button>
            `;
            listaGastos.appendChild(item);
        });
    }
}

function eliminarGasto(index) {
    const datos = obtenerDatosGuardados();
    datos.gastos.splice(index, 1);
    guardarDatos(datos);
    actualizarListaGastos();
    actualizarTotalGastos();
    calcularGanancias();
}

function actualizarTotalGastos() {
    const datos = obtenerDatosGuardados();
    const totalGastos = datos.gastos ? datos.gastos.reduce((total, gasto) => total + gasto.monto, 0) : 0;
    document.getElementById('totalGastos').textContent = totalGastos.toLocaleString();
}

// Función para calcular ganancias
function calcularGanancias() {
    const datos = obtenerDatosGuardados();
    let ganancias = 0;

    // Calcular ganancias por productos vendidos
    if (datos.productos && datos.productos.length > 0) {
        ganancias = datos.productos.reduce((total, producto) => {
            const gananciaUnitaria = producto.precioVenta - producto.precioCompra;
            return total + (gananciaUnitaria * producto.cantidad);
        }, 0);
    }

    // Restar gastos
    if (datos.gastos && datos.gastos.length > 0) {
        const totalGastos = datos.gastos.reduce((total, gasto) => total + gasto.monto, 0);
        ganancias -= totalGastos;
    }
}

// Funciones para manejar el almacenamiento local
function obtenerDatosGuardados() {
    const datosGuardados = localStorage.getItem('estadisticasData');
    return datosGuardados ? JSON.parse(datosGuardados) : {
        ventas: 0,
        productos: [],
        gastos: []
    };
}

function guardarDatos(datos) {
    localStorage.setItem('estadisticasData', JSON.stringify(datos));
}

function cargarDatosGuardados() {
    const datos = obtenerDatosGuardados();
    
    // Cargar ventas
    document.getElementById('totalVentas').textContent = datos.ventas.toLocaleString();
    
    // Cargar productos y stock
    actualizarListaProductos();
    actualizarTotalStock();
    
    // Cargar gastos
    actualizarListaGastos();
    actualizarTotalGastos();
    
    // Calcular ganancias
    calcularGanancias();
}

// Función para inicializar el gráfico
function inicializarGrafico() {
    const ctx = document.getElementById('ventasChart').getContext('2d');
    const datos = obtenerDatosGuardados();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
            datasets: [{
                label: 'Ventas Mensuales',
                data: [datos.ventas, 0, 0, 0, 0, 0], // Solo mostramos el mes actual
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Tendencia de Ventas'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Función para actualizar el gráfico
function actualizarGrafico() {
    const datos = obtenerDatosGuardados();
    const chart = Chart.getChart('ventasChart');
    if (chart) {
        chart.data.datasets[0].data[0] = datos.ventas;
        chart.update();
    }
}

// Función para mostrar mensajes
function mostrarMensaje(texto, tipo) {
    const mensaje = document.createElement('div');
    mensaje.className = `mensaje mensaje-${tipo}`;
    mensaje.textContent = texto;
    document.body.appendChild(mensaje);
    
    // Mostrar el mensaje
    setTimeout(() => mensaje.classList.add('visible'), 100);
    
    // Ocultar y eliminar el mensaje después de 3 segundos
    setTimeout(() => {
        mensaje.classList.remove('visible');
        setTimeout(() => mensaje.remove(), 300);
    }, 3000);
}

// Función para crear usuarios empleados
function crearUsuarioEmpleado() {
    const nombre = document.getElementById('inputNombreEmpleado').value.trim();
    const usuario = document.getElementById('inputUsuarioEmpleado').value.trim();
    const password = document.getElementById('inputPasswordEmpleado').value;
    const confirmPassword = document.getElementById('inputConfirmPasswordEmpleado').value;

    // Validaciones
    if (!nombre || !usuario || !password || !confirmPassword) {
        mostrarMensaje('Por favor complete todos los campos', 'error');
        return;
    }

    if (password !== confirmPassword) {
        mostrarMensaje('Las contraseñas no coinciden', 'error');
        return;
    }

    if (password.length < 6) {
        mostrarMensaje('La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }

    // Verificar si el usuario ya existe
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios') || '[]');
    if (empleados.some(e => e.usuario === usuario)) {
        mostrarMensaje('Este nombre de usuario ya está en uso', 'error');
        return;
    }

    // Crear nuevo usuario empleado
    const nuevoEmpleado = {
        nombre,
        usuario,
        password,
        fechaCreacion: new Date().toISOString()
    };

    empleados.push(nuevoEmpleado);
    localStorage.setItem('empleadosUsuarios', JSON.stringify(empleados));

    // Limpiar formulario y mostrar mensaje de éxito
    document.getElementById('inputNombreEmpleado').value = '';
    document.getElementById('inputUsuarioEmpleado').value = '';
    document.getElementById('inputPasswordEmpleado').value = '';
    document.getElementById('inputConfirmPasswordEmpleado').value = '';
    
    mostrarMensaje('Usuario empleado creado exitosamente', 'exito');
    cerrarFormulario('Empleados');
}


function cargarProductosDisponibles() {
    const datos = obtenerDatosGuardados();
    const selectProducto = document.getElementById('selectProducto');
    selectProducto.innerHTML = '<option value="">Seleccione un producto</option>';

    datos.productos.forEach(producto => {
        if (producto.cantidad > 0) {  // Solo mostrar productos con stock
            const option = document.createElement('option');
            option.value = producto.codigo;
            option.textContent = `${producto.nombre} - ${producto.cantidad} disponibles`;
            selectProducto.appendChild(option);
        }
    });
}


function cargarDatosGuardados() {
    const datos = obtenerDatosGuardados();
    document.getElementById('totalVentas').textContent = datos.ventas.toLocaleString();
    actualizarListaProductos();
    actualizarTotalStock();
    cargarProductosDisponibles(); // Cargar lista de productos en el select
    actualizarListaGastos();
    actualizarTotalGastos();
    calcularGanancias();
}


window.venderProducto = function() {
    const codigo = document.getElementById('selectProducto').value;
    const cantidadVenta = parseInt(document.getElementById('inputCantidadVenta').value);

    if (!codigo || cantidadVenta <= 0) {
        alert('Seleccione un producto y una cantidad válida.');
        return;
    }

    const datos = obtenerDatosGuardados();
    const producto = datos.productos.find(p => p.codigo === codigo);

    if (!producto || producto.cantidad < cantidadVenta) {
        alert('Stock insuficiente para esta venta.');
        return;
    }

    // Actualizar stock
    producto.cantidad -= cantidadVenta;

    // Registrar venta
    datos.ventas += producto.precioVenta * cantidadVenta;

    // Guardar cambios
    guardarDatos(datos);
    actualizarListaProductos();
    actualizarTotalStock();
    cargarProductosDisponibles();
    document.getElementById('totalVentas').textContent = datos.ventas.toLocaleString();

    alert(`Venta realizada: ${cantidadVenta} x ${producto.nombre}`);
};
