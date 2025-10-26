/**
 * Funcionalidad de pantalla de carga para Login
 * Muestra una pantalla de carga con el logo de Bar Galileo durante 3 segundos
 * antes de procesar el login
 */
document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.querySelector('form');
  const loadingScreen = document.getElementById('login-loading-screen');
  
  if (loginForm && loadingScreen) {
    // Variable para controlar si ya se mostró la pantalla
    let loadingShown = false;
    
    loginForm.addEventListener('submit', function(e) {
      // Prevenir el envío inmediato del formulario
      e.preventDefault();
      
      // Solo mostrar la pantalla de carga si no hay errores visibles en el formulario
      const hasErrors = document.querySelectorAll('.errorlist, .alert-danger').length > 0;
      
      if (!hasErrors && !loadingShown) {
        loadingShown = true;
        
        // Mostrar la pantalla de carga
        loadingScreen.classList.remove('hidden');
        
        // Deshabilitar scroll del body
        document.body.style.overflow = 'hidden';
        
        // Agregar animación al contenido
        const loadingContent = loadingScreen.querySelector('.loading-content');
        if (loadingContent) {
          loadingContent.style.animation = 'fadeInUp 0.8s ease';
        }
        
        // Después de 3 segundos, ocultar la pantalla y enviar el formulario
        setTimeout(function() {
          loadingScreen.classList.add('hidden');
          
          // Restaurar scroll del body
          document.body.style.overflow = '';
          
          // Esperar un poco más para que termine la animación de fade out
          setTimeout(function() {
            // Enviar el formulario después de la animación
            loginForm.submit();
          }, 500); // 0.5 segundos adicionales para la animación
          
        }, 3000); // 3 segundos de pantalla de carga
      } else {
        // Si hay errores o ya se mostró, enviar inmediatamente
        loginForm.submit();
      }
    });
  }

  // Si la página se carga con errores, asegurar que la pantalla esté oculta
  window.addEventListener('load', function() {
    const hasErrors = document.querySelectorAll('.errorlist, .alert-danger').length > 0;
    if (hasErrors && loadingScreen) {
      loadingScreen.classList.add('hidden');
      document.body.style.overflow = '';
    }
  });
});
