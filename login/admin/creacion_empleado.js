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
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('empleadoForm');
    if (form) {
        form.addEventListener('submit', crearEmpleado);
    }
});
