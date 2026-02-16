(function () {
  'use strict';

  const VARIANT_ALIAS = {
    danger: 'error',
    error: 'error',
    warning: 'warning',
    warn: 'warning',
    success: 'success',
    ok: 'success',
    info: 'info',
    information: 'info',
    changed: 'changed',
    saved: 'changed',
    default: 'info'
  };

  const stackEl = ensureStack();
  const toastLimit = 5;
  const activeTimers = new WeakMap();
  let confirmOverlay;
  let confirmTitle;
  let confirmMessage;
  let confirmPrimary;
  let confirmSecondary;
  let confirmCloseBtn;
  let lastFocusedElement = null;
  let confirmResolver = null;

  function ensureStack() {
    const existing = document.querySelector('[data-feedback-stack]');
    if (existing) {
      return existing;
    }

    const div = document.createElement('div');
    div.className = 'container-messages';
    div.dataset.feedbackStack = 'true';
    div.setAttribute('aria-live', 'polite');
    div.setAttribute('aria-atomic', 'false');
    document.body.appendChild(div);
    return div;
  }

  function normalizeVariant(value) {
    if (!value) {
      return 'info';
    }
    const key = String(value).split(' ')[0].toLowerCase();
    return VARIANT_ALIAS[key] || 'info';
  }

  function show(message, options = {}) {
    if (!message) {
      return null;
    }

    const variant = normalizeVariant(options.variant);
    const title = options.title;
    const dismissible = options.dismissible !== false;
    const sticky = options.sticky === true;
    const duration = sticky ? null : Number(options.duration || 6000);

    const toast = document.createElement('div');
    toast.className = 'alert-message is-toast';
    toast.dataset.variant = variant;
    toast.setAttribute('role', variant === 'error' || variant === 'warning' ? 'alert' : 'status');

    const content = document.createElement('div');
    content.className = 'alert-message__content';

    if (title) {
      const titleEl = document.createElement('p');
      titleEl.className = 'alert-message__title';
      titleEl.textContent = title;
      content.appendChild(titleEl);
    }

    const body = document.createElement('p');
    body.className = 'alert-message__body';
    body.textContent = message;
    content.appendChild(body);

    toast.appendChild(content);

    if (dismissible) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'alert-message__close';
      closeBtn.type = 'button';
      closeBtn.setAttribute('aria-label', 'Cerrar notificación');
      closeBtn.innerHTML = '&times;';
      closeBtn.addEventListener('click', () => dismissToast(toast));
      toast.appendChild(closeBtn);
    }

    stackEl.prepend(toast);
    requestAnimationFrame(() => toast.classList.add('is-visible'));

    while (stackEl.children.length > toastLimit) {
      const last = stackEl.lastElementChild;
      if (last) {
        dismissToast(last);
      } else {
        break;
      }
    }

    if (duration) {
      const timeoutId = window.setTimeout(() => dismissToast(toast), duration);
      activeTimers.set(toast, timeoutId);

      toast.addEventListener('mouseenter', () => {
        const timer = activeTimers.get(toast);
        if (timer) {
          window.clearTimeout(timer);
          activeTimers.delete(toast);
        }
      });

      toast.addEventListener('mouseleave', () => {
        if (!activeTimers.has(toast)) {
          const timerId = window.setTimeout(() => dismissToast(toast), 1800);
          activeTimers.set(toast, timerId);
        }
      });
    }

    return {
      element: toast,
      dismiss: () => dismissToast(toast)
    };
  }

  function dismissToast(toast) {
    if (!toast || toast.dataset.dismissed === 'true') {
      return;
    }

    toast.dataset.dismissed = 'true';
    toast.classList.add('is-leaving');

    const timer = activeTimers.get(toast);
    if (timer) {
      window.clearTimeout(timer);
      activeTimers.delete(toast);
    }

    window.setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 250);
  }

  function ensureConfirmOverlay() {
    if (confirmOverlay) {
      return confirmOverlay;
    }

    const overlay = document.createElement('div');
    overlay.setAttribute('data-feedback-confirm-overlay', 'true');

    const dialog = document.createElement('div');
    dialog.className = 'app-confirm';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');

    const header = document.createElement('div');
    header.className = 'app-confirm__header';

    confirmTitle = document.createElement('h3');
    confirmTitle.className = 'app-confirm__title';
    confirmTitle.id = 'app-confirm-title';

    confirmCloseBtn = document.createElement('button');
    confirmCloseBtn.type = 'button';
    confirmCloseBtn.className = 'alert-message__close';
    confirmCloseBtn.setAttribute('aria-label', 'Cerrar confirmación');
    confirmCloseBtn.innerHTML = '&times;';

    header.appendChild(confirmTitle);
    header.appendChild(confirmCloseBtn);

    confirmMessage = document.createElement('p');
    confirmMessage.className = 'app-confirm__message';
    confirmMessage.id = 'app-confirm-message';

    const actions = document.createElement('div');
    actions.className = 'app-confirm__actions';

    confirmSecondary = document.createElement('button');
    confirmSecondary.type = 'button';
    confirmSecondary.className = 'app-confirm__btn app-confirm__btn--ghost';

    confirmPrimary = document.createElement('button');
    confirmPrimary.type = 'button';
    confirmPrimary.className = 'app-confirm__btn app-confirm__btn--primary';

    actions.appendChild(confirmSecondary);
    actions.appendChild(confirmPrimary);

    dialog.appendChild(header);
    dialog.appendChild(confirmMessage);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    confirmOverlay = overlay;

    const closeHandler = () => resolveConfirm(false);
    confirmSecondary.addEventListener('click', closeHandler);
    confirmCloseBtn.addEventListener('click', closeHandler);

    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        resolveConfirm(false);
      }
    });

    confirmPrimary.addEventListener('click', () => resolveConfirm(true));

    document.addEventListener('keydown', (event) => {
      if (!confirmOverlay || !confirmOverlay.classList.contains('is-open')) {
        return;
      }
      if (event.key === 'Escape') {
        event.preventDefault();
        resolveConfirm(false);
      }
      if (event.key === 'Tab') {
        const focusable = [confirmPrimary, confirmSecondary, confirmCloseBtn].filter(Boolean);
        const index = focusable.indexOf(document.activeElement);
        if (index === -1) {
          focusable[0].focus();
          event.preventDefault();
          return;
        }
        const nextIndex = event.shiftKey ? (index - 1 + focusable.length) % focusable.length : (index + 1) % focusable.length;
        focusable[nextIndex].focus();
        event.preventDefault();
      }
    });

    return overlay;
  }

  function confirm(options = {}) {
    const overlay = ensureConfirmOverlay();
    const title = options.title || 'Confirmar acción';
    const message = options.message || '¿Deseas continuar con esta acción?';
    const confirmLabel = options.confirmLabel || 'Confirmar';
    const cancelLabel = options.cancelLabel || 'Cancelar';

    confirmTitle.textContent = title;
    confirmMessage.textContent = message;
    confirmPrimary.textContent = confirmLabel;
    confirmSecondary.textContent = cancelLabel;

    overlay.classList.add('is-open');
    lastFocusedElement = document.activeElement;
    confirmPrimary.focus();

    return new Promise((resolve) => {
      confirmResolver = resolve;
    });
  }

  function resolveConfirm(result) {
    if (!confirmOverlay || !confirmOverlay.classList.contains('is-open')) {
      return;
    }

    confirmOverlay.classList.remove('is-open');
    if (typeof confirmResolver === 'function') {
      confirmResolver(result);
    }
    confirmResolver = null;

    window.setTimeout(() => {
      if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
        lastFocusedElement.focus();
      }
      lastFocusedElement = null;
    }, 50);
  }

  function handleDeclarativeConfirm(event) {
    const trigger = event.currentTarget;
    if (!trigger) {
      return;
    }
    event.preventDefault();

    const message = trigger.getAttribute('data-feedback-confirm');
    if (!message) {
      return;
    }

    const title = trigger.getAttribute('data-feedback-confirm-title');
    const variant = trigger.getAttribute('data-feedback-confirm-variant');
    const confirmLabel = trigger.getAttribute('data-feedback-confirm-ok');
    const cancelLabel = trigger.getAttribute('data-feedback-confirm-cancel');
    const action = (trigger.getAttribute('data-feedback-confirm-action') || '').toLowerCase();
    const callbackName = trigger.getAttribute('data-feedback-confirm-callback');

    confirm({
      title,
      message,
      confirmLabel,
      cancelLabel,
      variant
    }).then((accepted) => {
      if (!accepted) {
        return;
      }

      if (action === 'navigate' && trigger.href) {
        window.location.href = trigger.href;
        return;
      }

      if (action === 'custom' && callbackName && typeof window[callbackName] === 'function') {
        window[callbackName].call(trigger, event);
        return;
      }

      const form = trigger.closest('form');
      if (form) {
        if (typeof form.requestSubmit === 'function') {
          form.requestSubmit(trigger.matches('button, input[type="submit"]') ? trigger : undefined);
        } else {
          form.submit();
        }
        return;
      }

      if (trigger.tagName === 'A' && trigger.href) {
        window.location.href = trigger.href;
      }
    });
  }

  function bindDeclarativeConfirms(root = document) {
    const elements = root.querySelectorAll('[data-feedback-confirm]:not([data-feedback-confirm-bound])');
    elements.forEach((el) => {
      el.dataset.feedbackConfirmBound = 'true';
      el.addEventListener('click', handleDeclarativeConfirm);
    });
  }

  function hydrateServerMessages() {
    const script = document.getElementById('django-messages-data');
    if (!script || !script.textContent.trim()) {
      return;
    }

    try {
      const payload = JSON.parse(script.textContent);
      if (Array.isArray(payload)) {
        payload.forEach((entry) => {
          if (!entry || !entry.message) {
            return;
          }
          show(entry.message, { variant: entry.level });
        });
      }
    } catch (error) {
      console.warn('[Feedback] No se pudo parsear los mensajes del servidor.', error);
    } finally {
      script.parentNode?.removeChild(script);
    }
  }

  function dismissAll() {
    Array.from(stackEl.children).forEach((child) => dismissToast(child));
  }

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node instanceof HTMLElement) {
          bindDeclarativeConfirms(node);
        }
      });
    });
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });

  document.addEventListener('DOMContentLoaded', () => {
    hydrateServerMessages();
    bindDeclarativeConfirms();
  });

  window.AppFeedback = {
    show,
    success: (message, options = {}) => show(message, { ...options, variant: 'success' }),
    error: (message, options = {}) => show(message, { ...options, variant: 'error' }),
    warning: (message, options = {}) => show(message, { ...options, variant: 'warning' }),
    info: (message, options = {}) => show(message, { ...options, variant: 'info' }),
    changed: (message, options = {}) => show(message, { ...options, variant: 'changed' }),
    confirm,
    dismissAll
  };
})();
