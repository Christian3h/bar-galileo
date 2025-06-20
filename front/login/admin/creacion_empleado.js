// Función para mostrar mensajes al usuario
function mostrarMensaje(mensaje, tipo) {
    const mensajeDiv = document.getElementById('mensajeCreacion');
    mensajeDiv.textContent = mensaje;
    mensajeDiv.className = `mensaje ${tipo}`;
    mensajeDiv.style.display = 'block';
    
    setTimeout(() => {
        mensajeDiv.style.display = 'none';
    }, 3000);
}

// Función para validar el formulario
function validarFormulario(usuario, password, confirmPassword) {
    if (!usuario || !password || !confirmPassword) {
        mostrarMensaje('Por favor complete todos los campos', 'error');
        return false;
    }

    if (password !== confirmPassword) {
        mostrarMensaje('Las contraseñas no coinciden', 'error');
        return false;
    }

    if (password.length < 6) {
        mostrarMensaje('La contraseña debe tener al menos 6 caracteres', 'error');
        return false;
    }

    // Verificar si el usuario ya existe
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios') || '[]');
    if (empleados.some(e => e.usuario === usuario)) {
        mostrarMensaje('Este nombre de usuario ya está en uso', 'error');
        return false;
    }

    return true;
}

// Función principal para crear empleado
function crearEmpleado(event) {
    event.preventDefault();
    
    // Obtener valores del formulario
    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const usuario = document.getElementById('usuario').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validar el formulario
    if (!validarFormulario(usuario, password, confirmPassword)) {
        return false;
    }

    // Crear objeto del nuevo empleado
    const nuevoEmpleado = {
        nombre,
        apellido,
        usuario,
        password,
        fechaCreacion: new Date().toISOString(),
        rol: 'empleado'
    };

    try {
        // Obtener lista actual de empleados
        const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios') || '[]');
        
        // Agregar nuevo empleado
        empleados.push(nuevoEmpleado);
        
        // Guardar en localStorage
        localStorage.setItem('empleadosUsuarios', JSON.stringify(empleados));

        // Mostrar mensaje de éxito
        mostrarMensaje('Usuario empleado creado exitosamente', 'exito');

        // Limpiar el formulario
        document.getElementById('empleadoForm').reset();

        // Redireccionar después de 2 segundos
        setTimeout(() => {
            window.location.href = 'estadisticas.html';
        }, 2000);

    } catch (error) {
        console.error('Error al crear empleado:', error);
        mostrarMensaje('Error al crear el usuario empleado', 'error');
    }

    return false;
}

// Agregar event listener cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('empleadoForm');
    const btnMostrarUsuarios = document.getElementById('btnMostrarUsuarios');
    const searchInput = document.getElementById('searchInput');
    
    form.addEventListener('submit', crearEmpleado);
    
    // Event listener para mostrar/ocultar tabla de usuarios
    btnMostrarUsuarios.addEventListener('click', function() {
        const tablaUsuarios = document.getElementById('tablaUsuarios');
        if (tablaUsuarios.style.display === 'none') {
            tablaUsuarios.style.display = 'block';
            cargarUsuarios();
        } else {
            tablaUsuarios.style.display = 'none';
        }
    });

    // Event listener para búsqueda
    searchInput.addEventListener('input', function() {
        cargarUsuarios(this.value.toLowerCase());
    });
});

// Función para cargar usuarios
function cargarUsuarios(filtro = '') {
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
    const tablaBody = document.getElementById('tablaBody');
    tablaBody.innerHTML = '';

    empleados.filter(empleado => 
        empleado.nombre.toLowerCase().includes(filtro) ||
        empleado.apellido.toLowerCase().includes(filtro) ||
        empleado.usuario.toLowerCase().includes(filtro)
    ).forEach(empleado => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${empleado.nombre}</td>
            <td>${empleado.apellido}</td>
            <td>${empleado.usuario}</td>
            <td>
                <span class="password-mask">****</span>
                <button class="btn-show" onclick="togglePassword(this, '${empleado.password}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
            <td>${new Date(empleado.fechaCreacion).toLocaleString()}</td>
            <td>
                <button class="btn-action btn-edit" onclick="editarUsuario('${empleado.usuario}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-action btn-delete" onclick="eliminarUsuario('${empleado.usuario}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tablaBody.appendChild(tr);
    });
}

// Función para mostrar/ocultar contraseña
function togglePassword(button, password) {
    const span = button.previousElementSibling;
    if (span.textContent === '****') {
        span.textContent = password;
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        span.textContent = '****';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Función para editar usuario
function editarUsuario(usuario) {
    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
    const empleado = empleados.find(emp => emp.usuario === usuario);
    
    if (empleado) {
        document.getElementById('nombre').value = empleado.nombre;
        document.getElementById('apellido').value = empleado.apellido;
        document.getElementById('usuario').value = empleado.usuario;
        document.getElementById('password').value = empleado.password;
        document.getElementById('confirmPassword').value = empleado.password;
        
        // Eliminar usuario actual (sin confirmar)
        eliminarUsuario(usuario, false);
        
        // Scroll al formulario
        document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
    }
}

// Función para eliminar usuario
function eliminarUsuario(usuario, confirmar = true) {
    if (confirmar && !confirm('¿Está seguro de eliminar este usuario?')) {
        return;
    }

    const empleados = JSON.parse(localStorage.getItem('empleadosUsuarios')) || [];
    const empleadosFiltrados = empleados.filter(emp => emp.usuario !== usuario);
    localStorage.setItem('empleadosUsuarios', JSON.stringify(empleadosFiltrados));
    
    if (confirmar) {
        mostrarMensaje('Usuario eliminado exitosamente', 'exito');
    }
    
    cargarUsuarios();
}
