import { verificarSesion } from "./validarSesion.js";
verificarSesion();

document.addEventListener("DOMContentLoaded", function () {
    const botonCerrarSesion = document.getElementById("cerrarSesion");

    if (botonCerrarSesion) {
        botonCerrarSesion.addEventListener("click", function () {
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("empleadoActual"); // Opcional, si necesitas limpiar más datos
            window.location.href = "/../login/index.html"; // Redirigir al login
        });
    }
});
 
