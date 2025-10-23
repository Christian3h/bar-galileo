/**
 * Funcionalidad de pantalla de carga del Dashboard
 * Muestra una pantalla de carga con el logo de Bar Galileo por 3 segundos
 * antes de navegar al dashboard
 */
document.addEventListener("DOMContentLoaded", function () {
  const dashboardLink = document.getElementById("dashboard-link");
  const loadingScreen = document.getElementById("dashboard-loading-screen");
  
  if (dashboardLink && loadingScreen) {
    dashboardLink.addEventListener("click", function(e) {
      e.preventDefault(); // Prevenir la navegación inmediata
      
      // Mostrar la pantalla de carga con una pequeña animación de entrada
      loadingScreen.classList.remove("hidden");
      
      // Deshabilitar scroll del body mientras se muestra la pantalla
      document.body.style.overflow = "hidden";
      
      // Guardar la URL del dashboard
      const dashboardUrl = this.href;
      
      // Agregar clase de animación al contenido
      const loadingContent = loadingScreen.querySelector('.loading-content');
      if (loadingContent) {
        loadingContent.style.animation = 'fadeInUp 0.8s ease';
      }
      
      // Después de 3 segundos, ocultar la pantalla y navegar
      setTimeout(function() {
        // Agregar animación de salida
        if (loadingContent) {
          loadingContent.style.animation = 'fadeOutDown 0.5s ease';
        }
        
        loadingScreen.classList.add("hidden");
        
        // Restaurar scroll del body
        document.body.style.overflow = "";
        
        // Esperar un poco más para que termine la animación de fade out
        setTimeout(function() {
          window.location.href = dashboardUrl;
        }, 500); // 0.5 segundos adicionales para la animación
        
      }, 3000); // 3 segundos de pantalla de carga
    });
  }

  // Agregar animación de salida al CSS dinámicamente
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeOutDown {
      from {
        opacity: 1;
        transform: translateY(0);
      }
      to {
        opacity: 0;
        transform: translateY(30px);
      }
    }
  `;
  document.head.appendChild(style);
});
