document.addEventListener("DOMContentLoaded", function () {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = `${ws_scheme}://${window.location.host}/ws/notificaciones/`;

    const socket = new WebSocket(ws_path);
    const notificacionesFlotantes = document.getElementById("notificaciones-flotantes");

    if (!notificacionesFlotantes) {
        console.error('[DEBUG][Front] No se encontró el div de notificaciones flotantes');
        return;
    }

    function mostrarNotificacion(mensaje) {
        const div = document.createElement("div");
        div.innerHTML = `
            <span>${mensaje}</span>
            <button style="margin-left: 10px; background: none; color: #fff; border: none; cursor: pointer; font-weight: bold;">✕</button>
        `;

        div.style.background = "#323232";
        div.style.color = "#fff";
        div.style.marginBottom = "12px";
        div.style.padding = "14px 22px";
        div.style.borderRadius = "8px";
        div.style.boxShadow = "0 2px 8px rgba(0,0,0,0.18)";
        div.style.opacity = "0.95";
        div.style.fontSize = "1rem";
        div.style.display = "flex";
        div.style.justifyContent = "space-between";
        div.style.alignItems = "center";
        div.style.transition = "opacity 0.5s";

        // Botón de cerrar
        const cerrarBtn = div.querySelector("button");
        cerrarBtn.addEventListener("click", () => {
            div.style.opacity = "0";
            setTimeout(() => div.remove(), 500);
        });

        notificacionesFlotantes.prepend(div);
    }

    socket.addEventListener("open", () => {
        // WebSocket conectado
    });

    socket.addEventListener("message", (e) => {
        let data = {};
        try {
            data = JSON.parse(e.data);
        } catch (error) {
            console.warn('[DEBUG] No se pudo parsear JSON:', error);
            data = { message: e.data };
        }

        if (data.message) {
            mostrarNotificacion(data.message);
        }
    });

    socket.addEventListener("error", (e) => {
        console.error("[DEBUG][Front] WebSocket error:", e);
    });

    socket.addEventListener("close", () => {
        // WebSocket cerrado
    });
});
