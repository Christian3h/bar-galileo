document.addEventListener('DOMContentLoaded', function () {
    const notificationIcon = document.getElementById('notification-icon');
    const notificationBadge = document.getElementById('notification-badge');
    const notificationsPanel = document.getElementById('notifications-panel');
    const notificationList = document.getElementById('notification-list');
    const markAllAsReadBtn = document.getElementById('mark-all-as-read');
    const notificacionesFlotantes = document.getElementById("notificaciones-flotantes");

    function fetchNotifications() {
        fetch('/api/notifications/history/')
            .then(response => response.json())
            .then(data => {
                updateBadge(data.unread_count);
                updatePanel(data.history);
            });
    }

    function updateBadge(count) {
        if (count > 0) {
            notificationBadge.textContent = count;
            notificationBadge.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    function updatePanel(notifications) {
        notificationList.innerHTML = '';
        notifications.forEach(notif => {
            const item = document.createElement('li');
            item.className = 'notification-item';
            if (!notif.leida) {
                item.classList.add('unread');
            }
            item.innerHTML = `
                <a href="#" data-id="${notif.id}">
                    <p>${notif.mensaje}</p>
                    <span class="timestamp">${new Date(notif.fecha).toLocaleString()}</span>
                </a>
            `;
            notificationList.appendChild(item);
        });
    }

    function mostrarNotificacion(mensaje, level = 'info') {
        if (!notificacionesFlotantes) return;

        const div = document.createElement("div");
        div.className = `alert-message ${level}`;
        div.innerHTML = `
            <span class="message-text">${mensaje}</span>
            <button class="close-btn">✕</button>
        `;

        const cerrarBtn = div.querySelector(".close-btn");
        cerrarBtn.addEventListener("click", () => {
            div.classList.add('fade-out');
            div.addEventListener('animationend', () => div.remove());
        });

        notificacionesFlotantes.prepend(div);

        setTimeout(() => {
            div.classList.add('fade-out');
            div.addEventListener('animationend', () => div.remove());
        }, 5000); // La notificación desaparece después de 5 segundos
    }

    notificationIcon.addEventListener('click', () => {
        notificationsPanel.classList.toggle('show');
        if (notificationsPanel.classList.contains('show')) {
            fetchNotifications();
        }
    });

    markAllAsReadBtn.addEventListener('click', () => {
        fetch('/api/notifications/mark-as-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ ids: [] })
        }).then(() => {
            fetchNotifications();
        });
    });

    notificationList.addEventListener('click', e => {
        e.preventDefault();
        const target = e.target.closest('a');
        if (target) {
            const id = target.dataset.id;
            fetch('/api/notifications/mark-as-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ ids: [id] })
            }).then(() => {
                fetchNotifications();
            });
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Fetch initial state
    fetchNotifications();

    // WebSocket integration
    const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    const ws_path = ws_scheme + '://' + window.location.host + "/ws/notificaciones/";
    const socket = new WebSocket(ws_path);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.message) {
            mostrarNotificacion(data.message); // Muestra el pop-up
            fetchNotifications(); // Actualiza la campana y el historial
        }
    };
});
