// Verificar si el usuario está autenticado
document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('isLoggedIn')) {
        window.location.href = '../index.html';
        return;
    }

    // Cargar empleados existentes
    cargarEmpleados();

    // Configurar el formulario
    document.getElementById('empleadoForm').addEventListener('submit', agregarEmpleado);

    // Configurar búsqueda
    document.getElementById('searchEmployee').addEventListener('input', filtrarEmpleados);

    // Configurar cierre de sesión
    document.getElementById('cerrarSesion').addEventListener('click', function() {
        localStorage.removeItem('isLoggedIn');
        window.location.href = '../index.html';
    });
});

function agregarEmpleado(e) {
    e.preventDefault();

    // Obtener valores del formulario
    const empleado = {
        nombre: document.getElementById('nombre').value,
        apellido: document.getElementById('apellido').value,
        cedula: document.getElementById('cedula').value,
        telefono: document.getElementById('telefono').value,
        salario: parseFloat(document.getElementById('salario').value),
        cargo: document.getElementById('cargo').value,
        id: Date.now() // Usar timestamp como ID único
    };

    // Validar cédula única
    const empleados = JSON.parse(localStorage.getItem('empleados')) || [];
    if (empleados.some(emp => emp.cedula === empleado.cedula)) {
        mostrarMensaje('Ya existe un empleado con esta cédula', 'error');
        return;
    }

    // Guardar empleado
    empleados.push(empleado);
    localStorage.setItem('empleados', JSON.stringify(empleados));

    // Limpiar formulario
    document.getElementById('empleadoForm').reset();

    // Mostrar mensaje de éxito
    mostrarMensaje('Empleado agregado exitosamente', 'exito');

    // Actualizar lista de empleados
    cargarEmpleados();
}

function cargarEmpleados() {
    const empleados = JSON.parse(localStorage.getItem('empleados')) || [];
    const tbody = document.getElementById('employeesList');
    tbody.innerHTML = '';

    empleados.forEach(empleado => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${empleado.nombre}</td>
            <td>${empleado.apellido}</td>
            <td>${empleado.cedula}</td>
            <td>${empleado.telefono}</td>
            <td>$${empleado.salario ? empleado.salario.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '0.00'}</td>
            <td>${empleado.cargo}</td>
            <td>
                <button onclick="editarEmpleado(${empleado.id})" class="btn-action btn-edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarEmpleado(${empleado.id})" class="btn-action btn-delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarEmpleados() {
    const busqueda = document.getElementById('searchEmployee').value.toLowerCase();
    const empleados = JSON.parse(localStorage.getItem('empleados')) || [];
    const tbody = document.getElementById('employeesList');
    tbody.innerHTML = '';

    empleados.filter(empleado => 
        empleado.nombre.toLowerCase().includes(busqueda) ||
        empleado.apellido.toLowerCase().includes(busqueda) ||
        empleado.cedula.includes(busqueda) ||
        empleado.cargo.toLowerCase().includes(busqueda)
    ).forEach(empleado => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${empleado.nombre}</td>
            <td>${empleado.apellido}</td>
            <td>${empleado.cedula}</td>
            <td>${empleado.telefono}</td>
            <td>$${empleado.salario ? empleado.salario.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '0.00'}</td>
            <td>${empleado.cargo}</td>
            <td>
                <button onclick="editarEmpleado(${empleado.id})" class="btn-action btn-edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarEmpleado(${empleado.id})" class="btn-action btn-delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function editarEmpleado(id) {
    const empleados = JSON.parse(localStorage.getItem('empleados')) || [];
    const empleado = empleados.find(emp => emp.id === id);
    
    if (empleado) {
        document.getElementById('nombre').value = empleado.nombre;
        document.getElementById('apellido').value = empleado.apellido;
        document.getElementById('cedula').value = empleado.cedula;
        document.getElementById('telefono').value = empleado.telefono;
        document.getElementById('salario').value = empleado.salario || '';
        document.getElementById('cargo').value = empleado.cargo;
        
        // Eliminar el empleado actual
        eliminarEmpleado(id, false);
        
        // Hacer scroll al formulario
        document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
    }
}

function eliminarEmpleado(id, mostrarConfirmacion = true) {
    if (mostrarConfirmacion && !confirm('¿Está seguro de eliminar este empleado?')) {
        return;
    }

    const empleados = JSON.parse(localStorage.getItem('empleados')) || [];
    const empleadosFiltrados = empleados.filter(emp => emp.id !== id);
    localStorage.setItem('empleados', JSON.stringify(empleadosFiltrados));
    
    if (mostrarConfirmacion) {
        mostrarMensaje('Empleado eliminado exitosamente', 'exito');
    }
    
    cargarEmpleados();
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
