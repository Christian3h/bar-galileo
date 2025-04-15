// Variables globales
const MONEDA_CONFIG = {
    locale: 'es-MX',
    currency: 'MXN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
};

document.addEventListener('DOMContentLoaded', function() {
    inicializarAplicacion();
});

function inicializarAplicacion() {
    cargarProductos();
    configurarEventListeners();
}

function configurarEventListeners() {
    document.getElementById('productoForm').addEventListener('submit', guardarProducto);
    document.getElementById('searchProduct').addEventListener('input', buscarProductos);
    
    // Actualizar total al cambiar cantidad o precio
    ['cantidad', 'precio'].forEach(id => {
        document.getElementById(id).addEventListener('input', calcularTotal);
    });
}

function calcularTotal() {
    const cantidad = parseInt(document.getElementById('cantidad').value) || 0;
    const precio = parseInt(document.getElementById('precio').value) || 0;
    const total = cantidad * precio;
    
    const totalElement = document.getElementById('total');
    if (totalElement) {
        totalElement.textContent = `Total: ${formatearMoneda(total)}`;
    }
}

function guardarProducto(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const producto = {
        id: Date.now(),
        nombre: formData.get('nombre'),
        categoria: formData.get('categoria'),
        cantidad: parseInt(formData.get('cantidad')),
        precio: parseInt(formData.get('precio')),
        fechaCreacion: new Date().toISOString()
    };

    // Validaciones
    if (!validarProducto(producto)) {
        return;
    }

    // Guardar producto
    const productos = obtenerProductos();
    productos.push(producto);
    guardarProductos(productos);

    mostrarMensaje('Producto guardado exitosamente', 'exito');
    e.target.reset();
    cargarProductos();
}

function validarProducto(producto) {
    if (!producto.nombre.trim()) {
        mostrarMensaje('El nombre es requerido', 'error');
        return false;
    }
    if (!producto.categoria) {
        mostrarMensaje('Seleccione una categoría', 'error');
        return false;
    }
    if (producto.cantidad < 0) {
        mostrarMensaje('La cantidad debe ser mayor o igual a 0', 'error');
        return false;
    }
    if (producto.precio <= 0) {
        mostrarMensaje('El precio debe ser mayor a 0', 'error');
        return false;
    }
    return true;
}

function cargarProductos(filtro = '') {
    const productos = obtenerProductos();
    const tbody = document.getElementById('productsList');
    tbody.innerHTML = '';

    const productosFiltrados = filtrarProductos(productos, filtro);
    
    if (productosFiltrados.length === 0) {
        mostrarMensajeNoProductos(tbody);
        return;
    }

    productosFiltrados.forEach(producto => crearFilaProducto(producto, tbody));
}

function filtrarProductos(productos, filtro) {
    if (!filtro) return productos;
    
    const filtroLower = filtro.toLowerCase();
    return productos.filter(producto => 
        producto.nombre.toLowerCase().includes(filtroLower) ||
        producto.categoria.toLowerCase().includes(filtroLower)
    );
}

function crearFilaProducto(producto, tbody) {
    const tr = document.createElement('tr');
    tr.className = 'producto-row';
    
    const total = producto.cantidad * producto.precio;
    
    tr.innerHTML = `
        <td class="nombre-col">${producto.nombre}</td>
        <td class="categoria-col">${producto.categoria}</td>
        <td class="cantidad-col text-right">${producto.cantidad}</td>
        <td class="precio-col text-right">${formatearMoneda(producto.precio)}</td>
        <td class="total-col text-right">${formatearMoneda(total)}</td>
        <td class="acciones-col">
            <div class="btn-group">
                <button onclick="editarProducto(${producto.id})" class="btn-edit" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarProducto(${producto.id})" class="btn-delete" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    
    tbody.appendChild(tr);
}

function mostrarMensajeNoProductos(tbody) {
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="no-productos">
                <i class="fas fa-box-open"></i>
                <p>No hay productos disponibles</p>
            </td>
        </tr>
    `;
}

function formatearMoneda(valor) {
    return new Intl.NumberFormat(MONEDA_CONFIG.locale, MONEDA_CONFIG).format(valor);
}

// Funciones de localStorage
function obtenerProductos() {
    return JSON.parse(localStorage.getItem('productos')) || [];
}

function guardarProductos(productos) {
    localStorage.setItem('productos', JSON.stringify(productos));
}

// Funciones existentes mejoradas
function editarProducto(id) {
    const productos = obtenerProductos();
    const producto = productos.find(p => p.id === id);

    if (producto) {
        Object.entries(producto).forEach(([key, value]) => {
            const input = document.getElementById(key);
            if (input) input.value = value;
        });

        eliminarProducto(id, false);
        calcularTotal();
        
        // Scroll al formulario
        document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function eliminarProducto(id, confirmar = true) {
    if (confirmar && !confirm('¿Está seguro de eliminar este producto?')) {
        return;
    }

    const productos = obtenerProductos();
    const productosFiltrados = productos.filter(p => p.id !== id);
    guardarProductos(productosFiltrados);

    if (confirmar) {
        mostrarMensaje('Producto eliminado exitosamente', 'exito');
    }
    
    cargarProductos();
}

function buscarProductos(e) {
    cargarProductos(e.target.value);
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