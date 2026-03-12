/**
 * dashboard-loading.js
 * ─────────────────────────────────────────────────────────────────
 * Lógica de la pantalla de carga de Bar Galileo.
 *
 * FLUJO CORRECTO:
 *  1. Usuario hace clic en el enlace al dashboard.
 *  2. Se muestra el overlay (fade-in rápido).
 *  3. Se redirige DE INMEDIATO (sin esperar animación).
 *  4. La nueva página arranca con el overlay visible
 *     y lo desvanece cuando el DOM está listo.
 *
 * Así nunca se ve el contenido anterior ni hay espera artificial.
 * ─────────────────────────────────────────────────────────────────
 */

(function () {
  "use strict";

  /* ── 1. En cuanto el script se parsea, cubrir la página si venimos
          de una navegación interna (sessionStorage flag). ─────────── */
  const COVER_KEY = "bg_cover_next_page";

  if (sessionStorage.getItem(COVER_KEY)) {
    sessionStorage.removeItem(COVER_KEY);

    // Crear overlay temporal lo antes posible (antes del DOMContentLoaded)
    // para que nunca haya un frame sin cubrir.
    const early = document.createElement("div");
    early.id = "early-cover";
    early.style.cssText = [
      "position:fixed",
      "inset:0",
      "z-index:99999",
      "background-color:var(--color-accent,#fff)",
      "display:flex",
      "justify-content:center",
      "align-items:center",
      "opacity:1",
      "transition:opacity 0.4s ease",
    ].join(";");
    document.documentElement.appendChild(early);

    // En cuanto el DOM esté listo, reemplazar por el overlay real y hacer fade-out
    document.addEventListener("DOMContentLoaded", function () {
      early.remove();

      const screen = document.getElementById("dashboard-loading-screen");
      if (screen) {
        // Asegurar que es visible
        screen.classList.remove("hidden", "fade-out");
        screen.classList.add("page-entering");
      }
    });
  }

  /* ── 2. Al hacer clic en el enlace del dashboard → mostrar overlay
          y redirigir de inmediato. ─────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", function () {

    // ── Enlace principal del dashboard (desde la home pública)
    const dashboardLink = document.getElementById("dashboard-link");
    if (dashboardLink) {
      dashboardLink.addEventListener("click", function (e) {
        e.preventDefault();
        _goTo(this.href);
      });
    }

    // ── Botón "home" dentro del nav del admin (nav-admin.html)
    const homeBtn = document.getElementById("home-page-btn");
    if (homeBtn) {
      homeBtn.addEventListener("click", function (e) {
        e.preventDefault();
        _goTo(this.dataset.url || this.getAttribute("data-url") || this.href);
      });
    }

  });

  /* ── Helper: muestra el overlay correspondiente y navega. ───────── */
  function _goTo(url) {
    if (!url) return;

    // Marca para que la página destino sepa que debe arrancarse cubierta
    sessionStorage.setItem(COVER_KEY, "1");

    // Mostrar el overlay del documento ACTUAL
    const screen =
      document.getElementById("dashboard-loading-screen") ||
      document.getElementById("home-loading-screen");

    if (screen) {
      screen.classList.remove("hidden", "fade-out", "page-entering");
      // forzar reflow para que la transición CSS aplique
      void screen.offsetWidth;
    }

    // Redirigir de inmediato — sin setTimeout
    window.location.href = url;
  }

})();