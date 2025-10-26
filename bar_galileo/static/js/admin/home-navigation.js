/**
 * Funcionalidad de navegación a página principal con pantalla de carga
 * Muestra una pantalla de carga con el logo de Bar Galileo por 3 segundos
 * antes de navegar a la página principal
 */
document.addEventListener("DOMContentLoaded", function () {
    const homePageBtn = document.getElementById("home-page-btn");
    const loadingScreen = document.getElementById("home-loading-screen");
    
    if (homePageBtn && loadingScreen) {
        homePageBtn.addEventListener("click", function(e) {
            e.preventDefault(); // Prevenir la navegación inmediata
            
            // Obtener la URL de la página principal
            const homeUrl = this.getAttribute('data-url');
            
            // Mostrar la pantalla de carga
            loadingScreen.classList.remove("hidden");
            
            // Deshabilitar scroll del body mientras se muestra la pantalla
            document.body.style.overflow = "hidden";
            
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
                    window.location.href = homeUrl;
                }, 500); // 0.5 segundos adicionales para la animación
                
            }, 3000); // 3 segundos de pantalla de carga
        });
    }

    // Agregar animación de salida al CSS dinámicamente si no existe
    if (!document.querySelector('style[data-animations="home-navigation"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-animations', 'home-navigation');
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
    }
});
