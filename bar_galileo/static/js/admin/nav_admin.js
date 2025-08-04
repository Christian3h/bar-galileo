function toggleMenu(id) {
  const submenu = document.getElementById(id);
  if (submenu) {
    submenu.classList.toggle('show');
  }
}

function toggleSidebar() {
  console.log('Toggling sidebar visibility');
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-show');
  } else {
    sidebar.classList.toggle('collapsed');
  }
}