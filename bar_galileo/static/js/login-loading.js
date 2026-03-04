/**
 * login-loading.js
 * ─────────────────────────────────────────────────────────────────
 * Pantalla de carga para el flujo de login.
 *
 * FLUJO:
 *  1. Usuario envía el formulario.
 *  2. Si no hay errores visibles → mostrar overlay y enviar el form
 *     DE INMEDIATO (sin setTimeout).
 *  3. La página destino (dashboard) arranca cubierta gracias al
 *     flag de sessionStorage que gestiona dashboard-loading.js.
 *  4. Si hay errores de validación → no mostrar overlay, dejar que
 *     el formulario se envíe normalmente para ver los errores.
 * ─────────────────────────────────────────────────────────────────
 */
document.addEventListener("DOMContentLoaded", function () {
  const loginForm    = document.querySelector("form");
  const loadingScreen = document.getElementById("login-loading-screen");

  if (!loginForm || !loadingScreen) return;

  // Si la página cargó con errores asegurarse de que el overlay esté oculto
  const _hasVisibleErrors = function () {
    return document.querySelectorAll(".errorlist, .alert-danger, .alert-error").length > 0;
  };

  if (_hasVisibleErrors()) {
    loadingScreen.classList.add("hidden");
    document.body.style.overflow = "";
    return;
  }

  loginForm.addEventListener("submit", function (e) {
    // Si hay errores de validación del lado cliente, dejar pasar normalmente
    if (_hasVisibleErrors()) return;

    // Prevenir envío para mostrar el overlay primero
    e.preventDefault();

    // Marcar para que la página destino sepa que debe arrancar cubierta
    try {
      sessionStorage.setItem("bg_cover_next_page", "1");
    } catch (_) {}

    // Mostrar el overlay
    loadingScreen.classList.remove("hidden", "fade-out", "page-entering");
    document.body.style.overflow = "hidden";

    // Enviar el formulario de inmediato — sin espera artificial
    loginForm.submit();
  });
});