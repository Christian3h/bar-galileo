document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Obtener valores del formulario
    const usuario = document.getElementById('loginUsuario').value;
    const password = document.getElementById('loginPassword').value;
    
    // Obtener lista de administradores
    const admins = JSON.parse(localStorage.getItem('admins')) || [];
    
    // Buscar el administrador
    const admin = admins.find(a => a.usuario === usuario && a.password === password);
    
    if (admin) {
        // Login exitoso
        mostrarMensaje('¡Inicio de sesión exitoso!', 'exito');
        
        // Guardar estado de sesión
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('currentAdmin', JSON.stringify(admin));
        
        // Redirigir a la página de estadísticas después de 1 segundo
        setTimeout(() => {
            window.location.href = 'estadisticas.html';
        }, 1000);
    } else {
        // Login fallido
        mostrarMensaje('Usuario o contraseña incorrectos', 'error');
    }
});

function mostrarMensaje(texto, tipo) {
    const mensajeDiv = document.getElementById('mensaje');
    mensajeDiv.textContent = texto;
    mensajeDiv.className = `mensaje ${tipo}`;
    mensajeDiv.style.display = 'block';
    
    if (tipo === 'error') {
        setTimeout(() => {
            mensajeDiv.style.display = 'none';
        }, 3000);
    }
}



