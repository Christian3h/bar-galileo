export function mostrarMensaje(mensaje, tipo) {
    const mensajeDiv = document.getElementById('mensaje');
    const contenedorMensaje = document.getElementById('mensaje-container');

    // Asegurar que no esté oculto
    contenedorMensaje.style.display = "grid"; 

    // Agregar mensaje y clase
    mensajeDiv.innerHTML = mensaje;
    contenedorMensaje.classList.remove("error", "acierto"); 
    contenedorMensaje.classList.add(tipo);

    // Forzar reflow para aplicar la transición correctamente
    setTimeout(() => {
        contenedorMensaje.style.opacity = "1";
        contenedorMensaje.style.transform = "translateY(0)";
    }, 10);

    // Ocultar después de 3 segundos
    setTimeout(() => {
        contenedorMensaje.style.opacity = "0";
        contenedorMensaje.style.transform = "translateY(-10px)";

        // Esperar la animación antes de ocultarlo completamente
        setTimeout(() => {
            contenedorMensaje.style.display = "none";
            contenedorMensaje.classList.remove(tipo);
        }, 500);
    }, 3000);
}
