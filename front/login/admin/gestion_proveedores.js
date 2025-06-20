// Verificar si el usuario está autenticado
document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = '../index.html';
        return;
    }

    // Cargar proveedores existentes
    cargarProveedores();

    // Configurar el formulario
    document.getElementById('proveedorForm').addEventListener('submit', agregarProveedor);

    // Configurar búsqueda
    document.getElementById('searchProvider').addEventListener('input', filtrarProveedores);

    // Configurar cierre de sesión
    document.getElementById('cerrarSesion').addEventListener('click', function() {
        localStorage.removeItem('isLoggedIn');
        window.location.href = '../index.html';
    });
});

function agregarProveedor(e) {
    e.preventDefault();

    const proveedor = {
        nombre: document.getElementById('nombre').value,
        apellido: document.getElementById('apellido').value,
        cedula: document.getElementById('cedula').value,
        telefono: document.getElementById('telefono').value,
        productos: document.getElementById('productos').value,
        categoria: document.getElementById('categoria').value,
        id: Date.now()
    };

    const proveedores = JSON.parse(localStorage.getItem('proveedores')) || [];
    
    if (proveedores.some(prov => prov.cedula === proveedor.cedula)) {
        mostrarMensaje('Ya existe un proveedor con esta cédula/RUC', 'error');
        return;
    }

    proveedores.push(proveedor);
    localStorage.setItem('proveedores', JSON.stringify(proveedores));

    document.getElementById('proveedorForm').reset();
    mostrarMensaje('Proveedor agregado exitosamente', 'exito');
    cargarProveedores();
}

function cargarProveedores() {
    const proveedores = JSON.parse(localStorage.getItem('proveedores')) || [];
    const tbody = document.getElementById('providersList');
    tbody.innerHTML = '';

    proveedores.forEach(proveedor => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${proveedor.nombre}</td>
            <td>${proveedor.apellido}</td>
            <td>${proveedor.cedula}</td>
            <td>${proveedor.telefono}</td>
            <td>${proveedor.productos}</td>
            <td>${proveedor.categoria}</td>
            <td>
                <button onclick="editarProveedor(${proveedor.id})" class="btn-action btn-edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarProveedor(${proveedor.id})" class="btn-action btn-delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarProveedores() {
    const busqueda = document.getElementById('searchProvider').value.toLowerCase();
    const proveedores = JSON.parse(localStorage.getItem('proveedores')) || [];
    const tbody = document.getElementById('providersList');
    tbody.innerHTML = '';

    proveedores.filter(proveedor => 
        proveedor.nombre.toLowerCase().includes(busqueda) ||
        proveedor.apellido.toLowerCase().includes(busqueda) ||
        proveedor.cedula.includes(busqueda) ||
        proveedor.productos.toLowerCase().includes(busqueda) ||
        proveedor.categoria.toLowerCase().includes(busqueda)
    ).forEach(proveedor => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${proveedor.nombre}</td>
            <td>${proveedor.apellido}</td>
            <td>${proveedor.cedula}</td>
            <td>${proveedor.telefono}</td>
            <td>${proveedor.productos}</td>
            <td>${proveedor.categoria}</td>
            <td>
                <button onclick="editarProveedor(${proveedor.id})" class="btn-action btn-edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarProveedor(${proveedor.id})" class="btn-action btn-delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function editarProveedor(id) {
    const proveedores = JSON.parse(localStorage.getItem('proveedores')) || [];
    const proveedor = proveedores.find(prov => prov.id === id);
    
    if (proveedor) {
        document.getElementById('nombre').value = proveedor.nombre;
        document.getElementById('apellido').value = proveedor.apellido;
        document.getElementById('cedula').value = proveedor.cedula;
        document.getElementById('telefono').value = proveedor.telefono;
        document.getElementById('productos').value = proveedor.productos;
        document.getElementById('categoria').value = proveedor.categoria;
        
        eliminarProveedor(id, false);
        document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function eliminarProveedor(id, mostrarConfirmacion = true) {
    if (mostrarConfirmacion && !confirm('¿Está seguro de eliminar este proveedor?')) {
        return;
    }

    const proveedores = JSON.parse(localStorage.getItem('proveedores')) || [];
    const proveedoresFiltrados = proveedores.filter(prov => prov.id !== id);
    localStorage.setItem('proveedores', JSON.stringify(proveedoresFiltrados));
    
    if (mostrarConfirmacion) {
        mostrarMensaje('Proveedor eliminado exitosamente', 'exito');
    }
    
    cargarProveedores();
}

function mostrarMensaje(texto, tipo) {
    const mensajeDiv = document.getElementById('mensaje');
    mensajeDiv.textContent = texto;
    mensajeDiv.className = `mensaje ${tipo}`;
    mensajeDiv.style.display = 'block';
    
    setTimeout(() => {
        mensajeDiv.style.display = 'none';
    }, 3000);
}
