function toggleMenu(id) {
  const submenu = document.getElementById(id);
  if (submenu) {
    submenu.classList.toggle('show');
  }
}

function toggleSidebar() {
<<<<<<< HEAD
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  document.body.classList.toggle('sidebar-is-open'); // Toggle class on body
  document.body.style.overflow = 'hidden';
  if (sidebar.classList.contains('collapsed') || sidebar.classList.contains('mobile-show')) {
      document.body.style.overflow = 'auto';
  }
=======
  console.log('Toggling sidebar visibility');
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a

  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-show');
  } else {
    sidebar.classList.toggle('collapsed');
  }
}