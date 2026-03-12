/**
 * searchbuilder-tooltips.js
 * Tooltips para DataTables SearchBuilder.
 * Se montan en el <body> para escapar de cualquier overflow:hidden padre.
 * Sin dependencias externas.
 */

(function () {
  "use strict";

  /* ── Textos de cada elemento ── */
  const TOOLTIPS = [
    {
      selector: ".dtsb-logicContainer .dtsb-logic",
      text: "Cambia entre Y (deben cumplirse TODAS las condiciones) y O (basta con UNA)",
      accent: "var(--color-dark)",
    },
    {
      selector: ".dtsb-clearGroup",
      text: "Eliminar este grupo de condiciones completo",
      accent: "var(--color-danger)",
    },
    {
      selector: ".dtsb-clearAll",
      text: "Eliminar todas las condiciones del filtro",
      accent: "var(--color-danger)",
    },
    {
      selector: ".dtsb-delete",
      text: "Eliminar esta condición",
      accent: "var(--color-danger)",
    },
    {
      selector: ".dtsb-add",
      text: "Agregar una nueva condición al grupo",
      accent: "var(--color-success)",
    },
    {
      selector: ".dtsb-right",
      text: "Mover dentro de un sub-grupo para combinar con otra lógica Y / O",
      accent: "var(--color-warning)",
    },
    {
      selector: "select.dtsb-data",
      text: "Dato — elige el atributo a evaluar (ej. Precio, Categoría)",
      accent: "var(--color-dark)",
    },
    {
      selector: "select.dtsb-condition",
      text: "Condición — tipo de comparación (ej. igual a, menor que, contiene…)",
      accent: "var(--color-success)",
    },
    {
      selector: ".dtsb-inputCont .dtsb-value, .dtsb-inputCont input",
      text: "Valor — referencia para la comparación (ej. 5000, Bebidas)",
      accent: "var(--color-info)",
    },
  ];

  /* ── Crear el elemento tooltip una sola vez ── */
  let tip = null;

  function createTipEl() {
    tip = document.createElement("div");
    tip.id = "dtsb-global-tooltip";
    Object.assign(tip.style, {
      position: "fixed",
      zIndex: "999999",
      pointerEvents: "none",
      opacity: "0",
      transition: "opacity 0.15s ease",
      background: "var(--color-secondary, #4a4a4a)",
      color: "var(--color-accent, #fff)",
      fontSize: "0.71rem",
      lineHeight: "1.45",
      padding: "5px 10px",
      borderRadius: "4px",
      maxWidth: "220px",
      boxShadow: "0 4px 14px rgba(0,0,0,0.18)",
      borderLeft: "3px solid transparent",
      whiteSpace: "normal",
      wordBreak: "break-word",
    });
    document.body.appendChild(tip);
  }

  /* ── Posicionar sobre el elemento disparador ── */
  function showTip(el, text, accent) {
    if (!tip) createTipEl();

    tip.textContent = text;
    tip.style.borderLeftColor = accent;
    tip.style.opacity = "0";
    tip.style.display = "block";

    // Primero mostramos invisible para medir el tamaño del tooltip
    const rect = el.getBoundingClientRect();
    const tipH = tip.offsetHeight || 36;
    const tipW = tip.offsetWidth || 180;

    let top = rect.top - tipH - 8;
    let left = rect.left;

    // Si no cabe arriba → mostrarlo abajo
    if (top < 6) {
      top = rect.bottom + 8;
    }

    // Si se sale por la derecha → ajustar
    if (left + tipW > window.innerWidth - 8) {
      left = window.innerWidth - tipW - 8;
    }

    // Si se sale por la izquierda
    if (left < 6) left = 6;

    tip.style.top = top + "px";
    tip.style.left = left + "px";
    tip.style.opacity = "1";
  }

  function hideTip() {
    if (tip) tip.style.opacity = "0";
  }

  /* ── Vincular eventos a los elementos ── */
  function bindTooltips(root) {
    root = root || document;

    TOOLTIPS.forEach(({ selector, text, accent }) => {
      root.querySelectorAll(selector).forEach((el) => {
        // Evitar duplicados
        if (el.__dtsb_tip_bound) return;
        el.__dtsb_tip_bound = true;

        el.addEventListener("mouseenter", () => showTip(el, text, accent));
        el.addEventListener("focus",      () => showTip(el, text, accent));
        el.addEventListener("mouseleave", hideTip);
        el.addEventListener("blur",       hideTip);
      });
    });
  }

  /* ── Inicializar cuando el DOM esté listo ── */
  function init() {
    createTipEl();
    bindTooltips();

    // Re-vincular cuando DataTables reconstruya el SearchBuilder (añadir condición, etc.)
    const observer = new MutationObserver(() => bindTooltips());
    const target = document.querySelector(".dtsb-searchBuilder") || document.body;
    observer.observe(target, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
