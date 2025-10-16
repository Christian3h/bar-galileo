document.addEventListener('DOMContentLoaded', () => {
  console.log('[DEBUG] Script de notificaciones cargado');

  const icon      = document.getElementById('notification-icon');
  const badge     = document.getElementById('notification-badge');
  const panel     = document.getElementById('notifications-panel');
  const list      = document.getElementById('notification-list');
  const markAllBtn= document.getElementById('mark-all-as-read');
  const floater   = document.getElementById('notificaciones-flotantes');

  if (!floater) {
    console.error('[DEBUG] No se encontró el contenedor de notificaciones flotantes');
    return;
  }

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
    if (!floater) return;

    const now = Date.now();
    if (msg === lastPopupMessage && now - lastPopupTime < 2000) return;

    lastPopupMessage = msg;
    lastPopupTime = now;

    const div = document.createElement('div');
    div.className = `alert-message ${level}`;
    div.innerHTML = `
      <span class="message-text">${msg}</span>
      <button class="close-btn" style="margin-left:10px;background:none;color:#fff;border:none;cursor:pointer;font-weight:bold;">✕</button>`;

    div.style.background = '#323232';
    div.style.color = '#fff';
    div.style.marginBottom = '12px';
    div.style.padding = '14px 22px';
    div.style.borderRadius = '8px';
    div.style.boxShadow = '0 2px 8px rgba(0,0,0,0.18)';
    div.style.opacity = '0.95';
    div.style.fontSize = '1rem';
    div.style.display = 'flex';
    div.style.justifyContent = 'space-between';
    div.style.alignItems = 'center';
    div.style.transition = 'opacity 0.5s';

    div.querySelector('.close-btn').onclick = () => {
      div.style.opacity = '0';
      setTimeout(() => div.remove(), 500);
    };

    floater.prepend(div);
    setTimeout(() => {
      div.style.opacity = '0';
      setTimeout(() => div.remove(), 500);
    }, 5000);
  };

  /* -----------  WebSocket ----------- */
  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const wsPath   = `${wsScheme}://${window.location.host}/ws/notificaciones/`;
  const ws       = new WebSocket(wsPath);

  ws.onopen = () => {
    console.log('[DEBUG][WS] Conectado');
    fetchNotifications();
    fetchPendingPopups();
  };

  ws.onmessage = e => {
    console.log('[DEBUG][WS] Mensaje recibido:', e.data);
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

  ws.onerror = e => console.error('[DEBUG][WS] Error:', e);
  ws.onclose = () => console.log('[DEBUG][WS] Cerrado');

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

  function getCookie(name) {
    return document.cookie.split('; ')
      .find(row => row.startsWith(name + '='))
      ?.split('=')[1];
  }
});
