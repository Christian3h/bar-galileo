document.getElementById('adminForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Obtener valores del formulario
    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const usuario = document.getElementById('usuario').value;
    const password = document.getElementById('password').value;
    const confirmarPassword = document.getElementById('confirmarPassword').value;
    
    // Validaciones
    if (password !== confirmarPassword) {
        mostrarMensaje('Las contraseñas no coinciden', 'error');
        return;
    }

    if (password.length < 6) {
        mostrarMensaje('La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }

    // Obtener administradores existentes
    const admins = JSON.parse(localStorage.getItem('admins')) || [];
    
    // Verificar si el usuario ya existe
    if (admins.some(admin => admin.usuario === usuario)) {
        mostrarMensaje('Este nombre de usuario ya está registrado', 'error');
        return;
    }

    // Crear objeto con datos del administrador
    const adminData = {
        nombre: nombre,
        email: email,
        usuario: usuario,
        password: password
    };

    // Guardar administrador
    guardarAdministrador(adminData);
});

function guardarAdministrador(adminData) {
    try {
        // Obtener administradores existentes o crear array vacío
        let admins = JSON.parse(localStorage.getItem('admins')) || [];
        
        // Agregar nuevo administrador
        admins.push(adminData);
        
        // Guardar en localStorage
        localStorage.setItem('admins', JSON.stringify(admins));
        
        // Mostrar mensaje de éxito
        mostrarMensaje('¡Usuario administrador registrado exitosamente!', 'exito');
        
        // Limpiar el formulario
        document.getElementById('adminForm').reset();
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    } catch (error) {
        mostrarMensaje('Error al guardar los datos', 'error');
    }
}

function mostrarMensaje(texto, tipo) {
    const mensajeDiv = document.getElementById('mensaje');
    mensajeDiv.textContent = texto;
    mensajeDiv.className = `mensaje ${tipo}`;
    mensajeDiv.style.display = 'block';
    
    // Para mensajes de error, ocultarlos después de 3 segundos
    if (tipo === 'error') {
        setTimeout(() => {
            mensajeDiv.style.display = 'none';
        }, 3000);
    }
    
    // Para mensajes de éxito, mostrar por 5 segundos
    if (tipo === 'exito') {
        setTimeout(() => {
            mensajeDiv.style.display = 'none';
        }, 5000);
    }
}
