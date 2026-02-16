document.addEventListener('DOMContentLoaded', () => {
  const icon      = document.getElementById('notification-icon');
  const badge     = document.getElementById('notification-badge');
  const panel     = document.getElementById('notifications-panel');
  const list      = document.getElementById('notification-list');
  const markAllBtn= document.getElementById('mark-all-as-read');
  const floater   = document.getElementById('notificaciones-flotantes');

  let lastPopupMessage = '';
  let lastPopupTime = 0;

  /* -----------  API REST ----------- */
  const fetchNotifications = () =>
    fetch('/api/notifications/history/')
      .then(r => r.json())
      .then(data => {
        updateBadge(data.unread_count);
        updatePanel(data.history);
      })
      .catch(e => console.error('[DEBUG] Error cargando historial:', e));

  const fetchPendingPopups = () =>
    fetch('/api/notificaciones/pendientes/')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) {
          data.forEach(n => n.mensaje && showPopup(n.mensaje));
        }
      })
      .catch(e => console.error('[DEBUG] Error cargando pop-ups pendientes:', e));

  const updateBadge = count => {
    if (badge) {
      badge.textContent = count;
      badge.style.display = count ? 'block' : 'none';
    }
  };

  const updatePanel = notifications => {
    list.innerHTML = '';
    notifications.forEach(n => {
      const li = document.createElement('li');
      li.className = 'notification-item' + (n.leida ? '' : ' unread');
      li.innerHTML = `
        <a href="#" data-id="${n.id}">
          <p>${n.mensaje}</p>
          <span class="timestamp">${new Date(n.fecha).toLocaleString()}</span>
        </a>`;
      list.appendChild(li);
    });
  };

  /* -----------  Pop-ups flotantes ----------- */
  const showPopup = (msg, level = 'info') => {
    if (!msg) return;
    const now = Date.now();
    if (msg === lastPopupMessage && now - lastPopupTime < 2000) return;

    lastPopupMessage = msg;
    lastPopupTime = now;
    if (window.AppFeedback) {
      AppFeedback.show(msg, {
        variant: level,
        duration: 6500
      });
    } else if (floater) {
      const fallback = document.createElement('div');
      fallback.className = `alert-message ${level}`;
      fallback.textContent = msg;
      floater.prepend(fallback);
      setTimeout(() => fallback.remove(), 5000);
    } else {
      console.info('[Notificaciones]', msg);
    }
  };

  /* -----------  WebSocket ----------- */
  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const wsPath   = `${wsScheme}://${window.location.host}/ws/notificaciones/`;
  const ws       = new WebSocket(wsPath);

  ws.onopen = () => {
    fetchNotifications();
    fetchPendingPopups();
  };

  ws.onmessage = e => {
    let data = {};
    try {
      data = JSON.parse(e.data);
    } catch (err) {
      console.warn('[DEBUG] Error parseando JSON:', err);
      data = { message: e.data };
    }

    if (data.message) {
      fetchNotifications();
      showPopup(data.message);
    }
  };

  ws.onerror = e => { /* WebSocket error */ };
  ws.onclose = () => { /* WebSocket cerrado */ };

  /* -----------  Eventos UI ----------- */
  if (icon) {
    icon.addEventListener('click', () => {
      panel.classList.toggle('show');
      if (panel.classList.contains('show')) fetchNotifications();
    });
  }

  if (markAllBtn) {
    markAllBtn.addEventListener('click', () =>
      fetch('/api/notifications/mark-as-read/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ ids: [] })
      }).then(fetchNotifications)
    );
  }

  if (list) {
    list.addEventListener('click', e => {
      e.preventDefault();
      const id = e.target.closest('a')?.dataset.id;
      if (!id) return;
      fetch('/api/notifications/mark-as-read/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ ids: [id] })
      }).then(fetchNotifications);
    });
  }

  // Cerrar panel de notificaciones al hacer clic fuera
  document.addEventListener('click', function(event) {
    if (!panel) return;
    // Si el panel está abierto y el clic fue fuera del panel y fuera del icono
    if (
      panel.classList.contains('show') &&
      !panel.contains(event.target) &&
      !(icon && icon.contains(event.target))
    ) {
      panel.classList.remove('show');
    }
  });

  function getCookie(name) {
    return document.cookie.split('; ')
      .find(row => row.startsWith(name + '='))
      ?.split('=')[1];
  }
});
