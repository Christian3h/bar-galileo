/**
 * Sistema de Notificaciones - Bar Galileo
 * Maneja el panel de notificaciones, badge y marcado como leídas.
 * Usa sessionStorage para persistir notificaciones a través de redirecciones.
 */
document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  // Elementos del DOM
  const icon = document.getElementById("notification-icon");
  const badge = document.getElementById("notification-badge");
  const panel = document.getElementById("notifications-panel");
  const list = document.getElementById("notification-list");
  const markAllBtn = document.getElementById("mark-all-as-read");
  const floater = document.getElementById("notificaciones-flotantes");

  // Verificar elementos requeridos
  if (!icon || !panel || !list) {
    //console.warn('[Notificaciones] Elementos del DOM no encontrados');
    return;
  }

  // Control de popups duplicados
  let lastPopupMessage = "";
  let lastPopupTime = 0;

  /* ==================================================
     UTILIDADES - sessionStorage para persistir notificaciones
  ================================================== */

  /**
   * Guarda una notificación pendiente para mostrar después de una redirección
   */
  function savePendingNotification(message) {
    if (!message) return;
    
    // Obtener notificaciones pendientes actuales
    const pending = JSON.parse(sessionStorage.getItem('pending_notifications') || '[]');
    
    // Agregar la nueva (evitar duplicados)
    if (!pending.includes(message)) {
      pending.push(message);
      sessionStorage.setItem('pending_notifications', JSON.stringify(pending));
    }
  }

  /**
   * Muestra y limpia las notificaciones pendientes de sessionStorage
   */
  function showPendingNotifications() {
    const pending = JSON.parse(sessionStorage.getItem('pending_notifications') || '[]');
    
    if (pending.length > 0) {
      // Mostrar cada notificación pendiente como popup
      pending.forEach((msg, index) => {
        setTimeout(() => {
          showPopup(msg);
        }, index * 500); // Mostrar una cada 500ms para no saturar
      });
      
      // Limpiar después de mostrarlas
      sessionStorage.removeItem('pending_notifications');
    }
  }

  /**
   * Obtiene el valor de una cookie por nombre
   */
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  /**
   * Actualiza el badge con el conteo de no leídas
   */
  function updateBadge(count) {
    if (!badge) return;
    const num = parseInt(count, 10) || 0;
    badge.textContent = num;
    badge.classList.toggle("show", num > 0);
    //console.log('[Notificaciones] Badge actualizado:', num);
  }

  /**
   * Renderiza la lista de notificaciones en el panel
   */
  function updatePanel(notifications) {
    list.innerHTML = "";

    if (!notifications || !notifications.length) {
      list.innerHTML =
        '<li class="empty-notifications">No hay notificaciones</li>';
      return;
    }

    notifications.forEach((n) => {
      const li = document.createElement("li");
      li.className = "notification-item" + (n.leida ? "" : " unread");

      const a = document.createElement("a");
      a.href = "#";
      a.dataset.id = n.id;

      const p = document.createElement("p");
      p.textContent = n.mensaje;

      const span = document.createElement("span");
      span.className = "timestamp";
      span.textContent = new Date(n.fecha).toLocaleString();

      a.appendChild(p);
      a.appendChild(span);
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  /* ==================================================
     API REST
  ================================================== */

  /**
   * Obtiene el historial de notificaciones y el conteo de no leídas
   */
  function fetchNotifications() {
    //console.log('[Notificaciones] Cargando historial...');
    return fetch("/api/notifications/history/", {
      method: "GET",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw new Error("Error HTTP: " + response.status);
        return response.json();
      })
      .then((data) => {
        //console.log('[Notificaciones] Historial recibido:', data);
        updateBadge(data.unread_count);
        updatePanel(data.history);
        return data;
      })
      .catch((error) => {
        //console.error('[Notificaciones] Error cargando historial:', error);
      });
  }

  /**
   * Marca todas las notificaciones como leídas en la base de datos
   */
  function markAllAsRead() {
    const csrfToken = getCookie("csrftoken");
    //console.log('[Notificaciones] Marcando todas como leídas...');

    return fetch("/api/notifications/mark-as-read/", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({ ids: [] }),
    })
      .then((response) => {
        if (response.status === 403) {
          showPopup(
            "No tienes permisos para marcar notificaciones como leídas.",
            "warning",
          );
        }
        if (!response.ok) throw new Error("Error HTTP: " + response.status);
        return response.json();
      })
      .then((data) => {
        //console.log('[Notificaciones] Marcadas como leídas:', data);
        return data;
      })
      .catch((error) => {
        //console.error('[Notificaciones] Error en mark-as-read:', error);
        throw error;
      });
  }

  /* ==================================================
     POPUPS FLOTANTES
  ================================================== */

  function showPopup(msg, level = "info") {
    if (!msg) return;

    // Evitar duplicados en corto tiempo
    const now = Date.now();
    if (msg === lastPopupMessage && now - lastPopupTime < 2000) return;
    lastPopupMessage = msg;
    lastPopupTime = now;

    if (window.AppFeedback) {
      AppFeedback.show(msg, { variant: level, duration: 6500 });
    } else if (floater) {
      const fallback = document.createElement("div");
      fallback.className = `alert-message ${level}`;
      fallback.textContent = msg;
      floater.prepend(fallback);
      setTimeout(() => fallback.remove(), 5000);
    }
  }

  /* ==================================================
     WEBSOCKET - Guardar notificación si hay redirección pendiente
  ================================================== */

  function initWebSocket() {
    try {
      const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
      const wsPath = `${wsScheme}://${window.location.host}/ws/notificaciones/`;
      const ws = new WebSocket(wsPath);

      ws.onopen = () => {
        //console.log('[Notificaciones] WebSocket conectado');
        fetchNotifications();
        
        // Mostrar notificaciones pendientes de redirecciones anteriores
        showPendingNotifications();
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.message) {
            // Verificar si hay una redirección pendiente
            // Si la hay, guardar en sessionStorage en vez de mostrar inmediatamente
            const isRedirecting = sessionStorage.getItem('pending_redirect');
            
            if (isRedirecting) {
              // Guardar para después de la redirección
              savePendingNotification(data.message);
              sessionStorage.removeItem('pending_redirect');
            } else {
              // Mostrar inmediatamente (no hay redirección)
              fetchNotifications();
              showPopup(data.message);
            }
          }
        } catch (err) {
          //console.warn('[Notificaciones] Error parseando mensaje WS:', err);
        }
      };

      ws.onerror = () => {
        //console.warn('[Notificaciones] Error en WebSocket');
      };

      ws.onclose = () => {
        //console.log("[Notificaciones] WebSocket cerrado");
      };
      
      // Guardar referencia al WebSocket para uso global
      window.notificationWebSocket = ws;
    } catch (err) {
      //console.warn('[Notificaciones] WebSocket no disponible:', err);
    }
  }

  /* ==================================================
     EVENTOS DE UI
  ================================================== */

  // Click en el icono de la campana
  icon.addEventListener("click", (event) => {
    event.stopPropagation();

    const isOpening = !panel.classList.contains("show");
    panel.classList.toggle("show");

    if (isOpening) {
      //console.log('[Notificaciones] Abriendo panel...');
      fetchNotifications();
    }
  });

  // Botón "Marcar todas como leídas"
  if (markAllBtn) {
    markAllBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      //console.log('[Notificaciones] Click en "Marcar todas como leídas"');

      // 1. Actualizar UI inmediatamente
      updateBadge(0);
      list.innerHTML =
        '<li class="empty-notifications">No hay notificaciones</li>';

      // 2. Marcar en BD (sin recargar para que no aparezcan las leídas)
      markAllAsRead()
        .then((data) => {
          //console.log("[Notificaciones] Todas marcadas como leídas exitosamente");
        })
        .catch((err) => {
          //console.error('[Notificaciones] Error en marcar todas:', err);
        });
    });
  }

  // Click en notificación individual para marcarla como leída
  list.addEventListener("click", (event) => {
    event.preventDefault();
    const anchor = event.target.closest("a");
    if (!anchor) return;

    const id = anchor.dataset.id;
    if (!id) return;

    const csrfToken = getCookie("csrftoken");
    fetch("/api/notifications/mark-as-read/", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({ ids: [parseInt(id, 10)] }),
    })
      .then(() => fetchNotifications())
      .catch((err) => {});
  });

  // Cerrar panel al hacer click fuera
  document.addEventListener("click", (event) => {
    if (
      panel.classList.contains("show") &&
      !panel.contains(event.target) &&
      !icon.contains(event.target)
    ) {
      panel.classList.remove("show");
    }
  });

  /* ==================================================
     INICIALIZACIÓN
  ================================================== */

  // Cargar notificaciones al inicio (solo para el panel, NO como popup)
  fetchNotifications();

  // Mostrar notificaciones pendientes de redirecciones anteriores
  showPendingNotifications();

  // Intentar conectar WebSocket para tiempo real
  initWebSocket();

  //console.log('[Notificaciones] Sistema inicializado');
});

/* ==================================================
   FUNCIÓN GLOBAL PARA INTERCEPTAR REDIRECCIONES
   Llamar antes de cualquier redirect que siga a una acción
================================================== */

window.savePendingRedirect = function() {
  sessionStorage.setItem('pending_redirect', 'true');
};

// Auto-guardar redirect en formularios
document.addEventListener('submit', (event) => {
  const form = event.target;
  // Solo interceptar formularios que probablemente generan notificaciones
  if (form.method.toLowerCase() === 'post' && !form.dataset.noNotify) {
    sessionStorage.setItem('pending_redirect', 'true');
  }
});
