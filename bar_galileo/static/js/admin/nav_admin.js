function toggleMenu(id) {
  const submenu = document.getElementById(id);
  if (submenu) {
    submenu.classList.toggle('show');
  }
}

// Función auxiliar para verificar si el sidebar está abierto
function isSidebarOpen() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return false;
  
  const isMobile = window.innerWidth <= 768;
  
  if (isMobile) {
    return sidebar.classList.contains('mobile-show');
  } else {
    // En desktop, está abierto si SÍ tiene 'collapsed' (invertido)
    return sidebar.classList.contains('collapsed');
  }
}

// Función para abrir el sidebar
function openSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  
  const isMobile = window.innerWidth <= 768;
  
  if (isMobile) {
    sidebar.classList.add('mobile-show');
  } else {
    sidebar.classList.add('collapsed');
  }
  
  document.body.classList.add('sidebar-is-open');
  document.body.style.overflow = 'hidden';
}

// Función para cerrar el sidebar
function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  
  const isMobile = window.innerWidth <= 768;
  
  if (isMobile) {
    sidebar.classList.remove('mobile-show');
  } else {
    sidebar.classList.remove('collapsed');
  }
  
  document.body.classList.remove('sidebar-is-open');
  document.body.style.overflow = 'auto';
}

// Función para alternar el sidebar (toggle)
function toggleSidebar() {
  if (isSidebarOpen()) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

// Cerrar el sidebar al hacer clic fuera de él
document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const toggleButton = document.querySelector('.toggle-sidebar-btn');
  
  if (!sidebar) return;

  // Detectar clics en todo el documento
  document.addEventListener('click', function(event) {
    // Solo actuar si el sidebar está abierto
    if (!isSidebarOpen()) return;

    // Verificar si el clic fue dentro del sidebar o en el botón toggle
    const clickedInsideSidebar = sidebar.contains(event.target);
    const clickedToggleButton = toggleButton && toggleButton.contains(event.target);
    
    // Si se hizo clic fuera del sidebar y fuera del botón toggle, CERRAR
    if (!clickedInsideSidebar && !clickedToggleButton) {
      closeSidebar();
    }
  });
});