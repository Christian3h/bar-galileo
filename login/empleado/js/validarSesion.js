// Función que verifica si hay una sesión activa
export function verificarSesion() {
    const isLoggedIn = localStorage.getItem("isLoggedIn");

    // Si no hay sesión iniciada, redirige al login
    if (!isLoggedIn) {
        window.location.href = "/../login/index.html"; // Ajusta la ruta según tu estructura
    }
}

// Ejecutar la función inmediatamente en todos los archivos JS
verificarSesion();
