/**
 * ====================================
 * ONLOAD.JS - BAR GALILEO
 * Funciones que se ejecutan al cargar las páginas
 * ====================================
 */

// Ejecutar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Bar Galileo - Sistema cargado correctamente');
    
    // Inicializar componentes principales
    initializeComponents();
    
    // Configurar eventos globales
    setupGlobalEvents();
    
    // Configurar formularios
    setupForms();
    
    // Mostrar mensajes de bienvenida si es necesario
    showWelcomeMessages();
});

/**
 * Inicializar componentes principales del sistema
 */
function initializeComponents() {
    // Inicializar tooltips si existen
    initializeTooltips();
    
    // Inicializar modales
    initializeModals();
    
    // Configurar navegación
    setupNavigation();
    
    // Configurar búsqueda
    setupSearch();
}

/**
 * Configurar eventos globales
 */
function setupGlobalEvents() {
    // Evento para cerrar alertas automáticamente
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            if (alert) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        });
    }, 5000);
    
    // Confirmar acciones peligrosas
    const dangerButtons = document.querySelectorAll('.btn-danger, .delete-btn');
    dangerButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Configurar formularios
 */
function setupForms() {
    // Validación en tiempo real
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        setupFormValidation(form);
    });
    
    // Auto-focus en primer campo
    const firstInput = document.querySelector('input:not([type="hidden"]), textarea, select');
    if (firstInput) {
        firstInput.focus();
    }
}

/**
 * Configurar validación de formularios
 */
function setupFormValidation(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(function(input) {
        // Validación en tiempo real
        input.addEventListener('blur', function() {
            validateField(input);
        });
        
        // Limpiar errores cuando el usuario empiece a escribir
        input.addEventListener('input', function() {
            clearFieldErrors(input);
        });
    });
    
    // Validación al enviar
    form.addEventListener('submit', function(e) {
        if (!validateForm(form)) {
            e.preventDefault();
            return false;
        }
        
        // Mostrar indicador de carga
        showFormLoading(form);
    });
}

/**
 * Validar un campo individual
 */
function validateField(field) {
    let isValid = true;
    let errorMessage = '';
    
    // Verificar si es requerido
    if (field.required && !field.value.trim()) {
        isValid = false;
        errorMessage = 'Este campo es requerido';
    }
    
    // Validaciones específicas por tipo
    if (field.type === 'email' && field.value) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(field.value)) {
            isValid = false;
            errorMessage = 'Ingresa una dirección de email válida';
        }
    }
    
    if (field.type === 'tel' && field.value) {
        const phonePattern = /^[\d\-\+\(\)\s]+$/;
        if (!phonePattern.test(field.value)) {
            isValid = false;
            errorMessage = 'Ingresa un número de teléfono válido';
        }
    }
    
    // Mostrar/ocultar errores
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldErrors(field);
    }
    
    return isValid;
}

/**
 * Mostrar error en un campo
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    // Buscar o crear elemento de error
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

/**
 * Limpiar errores de un campo
 */
function clearFieldErrors(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Validar formulario completo
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Mostrar indicador de carga en formulario
 */
function showFormLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent || submitBtn.value;
        submitBtn.textContent = 'Procesando...';
        submitBtn.setAttribute('data-original-text', originalText);
    }
}

/**
 * Inicializar tooltips
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-toggle="tooltip"]');
    // Si Bootstrap está disponible, inicializar tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipElements.forEach(function(element) {
            new bootstrap.Tooltip(element);
        });
    }
}

/**
 * Inicializar modales
 */
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-toggle="modal"]');
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetModal = document.querySelector(trigger.getAttribute('data-target'));
            if (targetModal) {
                showModal(targetModal);
            }
        });
    });
}

/**
 * Mostrar modal
 */
function showModal(modal) {
    modal.style.display = 'block';
    modal.classList.add('show');
    document.body.classList.add('modal-open');
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal(modal);
        }
    });
    
    // Cerrar modal con botón de cierre
    const closeButtons = modal.querySelectorAll('.close, .btn-close');
    closeButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            hideModal(modal);
        });
    });
}

/**
 * Ocultar modal
 */
function hideModal(modal) {
    modal.style.display = 'none';
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
}

/**
 * Configurar navegación
 */
function setupNavigation() {
    // Marcar elemento activo en navegación
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .navbar-nav a');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Navegación móvil
    const navToggle = document.querySelector('.navbar-toggle');
    const navMenu = document.querySelector('.navbar-collapse');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }
}

/**
 * Configurar búsqueda
 */
function setupSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Aquí se puede implementar búsqueda en tiempo real
                console.log('Buscando:', input.value);
            }, 300);
        });
    });
}

/**
 * Mostrar mensajes de bienvenida
 */
function showWelcomeMessages() {
    // Verificar si es la primera visita
    if (!localStorage.getItem('bar_galileo_visited')) {
        localStorage.setItem('bar_galileo_visited', 'true');
        
        // Mostrar mensaje de bienvenida si hay contenedor
        const welcomeContainer = document.querySelector('.welcome-message');
        if (welcomeContainer) {
            welcomeContainer.style.display = 'block';
        }
    }
}

/**
 * Utilidad para hacer peticiones AJAX
 */
function makeAjaxRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };
    
    const config = Object.assign(defaults, options);
    
    return fetch(url, config)
        .then(response => response.json())
        .catch(error => {
            console.error('Error en petición AJAX:', error);
            throw error;
        });
}

/**
 * Obtener cookie (útil para CSRF token)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Exportar funciones principales para uso global
window.BarGalileo = {
    validateField: validateField,
    makeAjaxRequest: makeAjaxRequest,
    showModal: showModal,
    hideModal: hideModal,
    getCookie: getCookie
};
