function toggleMenu(id) {
  const submenu = document.getElementById(id);
  if (submenu) {
    submenu.classList.toggle('show');
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  document.body.classList.toggle('sidebar-is-open'); // Toggle class on body
  document.body.style.overflow = 'hidden';
  if (sidebar.classList.contains('collapsed') || sidebar.classList.contains('mobile-show')) {
      document.body.style.overflow = 'auto';
  }

  const scrxd = sidebar.classList.contains('collapsed');
  console.log(scrxd);
  if (scrxd) {
    document.body.style.overflow = 'scroll';
  }

  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-show');
  } else {
    sidebar.classList.toggle('collapsed');

  }
}