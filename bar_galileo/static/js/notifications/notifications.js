document.addEventListener("DOMContentLoaded", function () {
    console.log('[DEBUG][Front] Script de notificaciones cargado');

    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = `${ws_scheme}://${window.location.host}/ws/notificaciones/`;
    console.log("[DEBUG][Front] Intentando conectar al WebSocket:", ws_path);

    const socket = new WebSocket(ws_path);
    const notificacionesFlotantes = document.getElementById("notificaciones-flotantes");

    if (!notificacionesFlotantes) {
        console.error('[DEBUG][Front] No se encontró el div de notificaciones flotantes');
        return;
    }

    function mostrarNotificacion(mensaje) {
        console.log('[DEBUG][Front] Mostrando notificación:', mensaje);

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
        console.log("[DEBUG][Front] WebSocket de notificaciones conectado");
    });

    socket.addEventListener("message", (e) => {
        console.log('[DEBUG][Front] Mensaje recibido por WebSocket:', e.data);
        let data = {};
        try {
            data = JSON.parse(e.data);
            console.log('[DEBUG] JSON parseado correctamente:', data);
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
        console.log("[DEBUG][Front] WebSocket de notificaciones cerrado");
    });
});
