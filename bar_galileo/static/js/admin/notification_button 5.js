// JavaScript para el sistema de notificaciones
class NotificationPanel {
  constructor() {
    this.notifications = [];
    this.unreadCount = 0;
    this.isOpen = false;
    this.init();
  }

  init() {
    // Elementos del DOM
    this.iconElement = document.getElementById("notification-icon");
    this.badgeElement = document.getElementById("notification-badge");
    this.panelElement = document.getElementById("notifications-panel");
    this.listElement = document.getElementById("notification-list");
    this.markAllButton = document.getElementById("mark-all-as-read");

    // Event listeners
    this.iconElement.addEventListener("click", (e) => {
      e.stopPropagation();
      this.togglePanel();
    });

    this.markAllButton.addEventListener("click", () => {
      this.markAllAsRead();
    });

    // Cerrar panel al hacer clic fuera
    document.addEventListener("click", (e) => {
      if (!this.panelElement.contains(e.target)) {
        this.closePanel();
      }
    });

    // Inicializar
    this.updateBadge();
    this.renderNotifications();
  }

  togglePanel() {
    if (this.isOpen) {
      this.closePanel();
    } else {
      this.openPanel();
    }
  }

  openPanel() {
    this.panelElement.classList.add("show");
    this.isOpen = true;
  }

  closePanel() {
    this.panelElement.classList.remove("show");
    this.isOpen = false;
  }

  addNotification(title, message, unread = true) {
    const notification = {
      id: Date.now(),
      title: title,
      message: message,
      unread: unread,
      time: new Date().toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    this.notifications.unshift(notification);
    if (unread) {
      this.unreadCount++;
    }

    this.updateBadge();
    this.renderNotifications();
  }

  markAsRead(notificationId) {
    const notification = this.notifications.find(
      (n) => n.id === notificationId,
    );
    if (notification && notification.unread) {
      notification.unread = false;
      this.unreadCount--;
      this.updateBadge();
      this.renderNotifications();
    }
  }

  markAllAsRead() {
    this.notifications.forEach((notification) => {
      notification.unread = false;
    });
    this.unreadCount = 0;
    this.updateBadge();
    this.renderNotifications();
  }

  updateBadge() {
    if (this.unreadCount > 0) {
      this.badgeElement.textContent =
        this.unreadCount > 99 ? "99+" : this.unreadCount;
      this.badgeElement.classList.add("show");
    } else {
      this.badgeElement.classList.remove("show");
    }
  }

  renderNotifications() {
    if (this.notifications.length === 0) {
      this.listElement.innerHTML =
        '<li class="empty-notifications">No hay notificaciones</li>';
      return;
    }

    const html = this.notifications
      .map(
        (notification) => `
            <li class="notification-item ${notification.unread ? "unread" : ""}" 
                onclick="notificationPanel.markAsRead(${notification.id})">
                <strong>${notification.title}</strong><br>
                <span style="font-size: 13px; color: #666;">${notification.message}</span><br>
                <small style="color: #999;">${notification.time}</small>
            </li>
        `,
      )
      .join("");

    this.listElement.innerHTML = html;
  }

  // Método para agregar notificaciones desde fuera
  notify(title, message) {
    this.addNotification(title, message, true);
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function () {
  window.notificationPanel = new NotificationPanel();
});

// Función global para agregar notificaciones fácilmente
function addNotification(title, message) {
  if (window.notificationPanel) {
    window.notificationPanel.notify(title, message);
  }
}
