/**
 * Security.js - Validación de seguridad en frontend para prevenir SSTI/XSS
 * 
 * Este archivo proporciona funciones para:
 * 1. Bloquear caracteres peligrosos en tiempo real
 * 2. Validar campos antes del submit
 * 3. Mostrar feedback visual al usuario
 * 
 * Uso básico:
 *   <input type="text" data-validate="name">
 *   <script>Seguridad.init()</script>
 * 
 * Tipos de validación disponibles:
 *   - name: Nombres (solo letras, espacios, guiones)
 *   - email: Emails (formato válido)
 *   - product: Nombres de productos
 *   - description: Descripciones
 *   - phone: Teléfonos
 *   - password: Contraseñas (solo longitud)
 *   - any: Campo genérico (bloquea caracteres peligrosos)
 */

const Seguridad = (function() {
    'use strict';

    // =========================================================================
    // CONFIGURACIÓN
    // =========================================================================
    
    const CONFIG = {
        // Regex para validación en tiempo real
        patterns: {
            // Emails: regex estricta
            email: /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/,
            
            // Nombres: solo letras, espacios, guiones, apóstrofos
            name: /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/,
            
            // Productos: alfanumérico + símbolos seguros
            product: /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-_.,()]+$/,
            
            // Descripciones: excluye caracteres peligrosos
            description: /^[^{}<>%`$;|&]+$/,
            
            // Teléfonos: solo números y símbolos de teléfono
            phone: /^[0-9\s\-\(\)\+]+$/,
            
            // Genérico: excluye lo peligroso
            any: /^[^{}<>%`$;|&]+$/
        },
        
        // Mensajes de error
        messages: {
            email: 'Ingresa un correo electrónico válido',
            name: 'Solo se permiten letras, espacios, guiones y apóstrofos',
            product: 'El nombre contiene caracteres no permitidos',
            description: 'La descripción contiene caracteres no permitidos',
            phone: 'El teléfono contiene caracteres no válidos',
            password: 'La contraseña debe tener entre 8 y 128 caracteres',
            any: 'Este campo contiene caracteres no permitidos'
        },
        
        // Longitudes
        limits: {
            name: { min: 1, max: 100 },
            product: { min: 1, max: 200 },
            description: { min: 0, max: 2000 },
            phone: { min: 1, max: 20 },
            password: { min: 8, max: 128 }
        }
    };

    // =========================================================================
    // FUNCIONES PRIVADAS
    // =========================================================================
    
    /**
     * Obtiene la configuración para un tipo de campo
     */
    function getConfig(type) {
        return CONFIG.patterns[type] || CONFIG.patterns.any;
    }
    
    /**
     * Muestra error en un campo
     */
    function showError(input, message) {
        const formGroup = input.closest('.mb-3, .form-group, .input-group');
        if (!formGroup) return;
        
        // Remover error previo
        removeError(input);
        
        // Agregar clase de error
        input.classList.add('is-invalid');
        
        // Crear mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Insertar después del input
        if (input.nextElementSibling && input.nextElementSibling.classList.contains('input-group')) {
            input.parentElement.parentElement.appendChild(errorDiv);
        } else {
            formGroup.appendChild(errorDiv);
        }
    }
    
    /**
     * Remueve error de un campo
     */
    function removeError(input) {
        input.classList.remove('is-invalid');
        const formGroup = input.closest('.mb-3, .form-group, .input-group');
        if (!formGroup) return;
        
        const existingError = formGroup.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
    
    /**
     * Valida un campo específico
     */
    function validateField(input) {
        const type = input.dataset.validate;
        if (!type) return true;
        
        const value = input.value.trim();
        const pattern = getConfig(type);
        
        // Campo vacío es válido (usar required para obligar)
        if (!value) {
            removeError(input);
            return true;
        }
        
        // Validar longitud si aplica
        if (CONFIG.limits[type]) {
            const { min, max } = CONFIG.limits[type];
            if (value.length < min || value.length > max) {
                showError(input, CONFIG.messages[type]);
                return false;
            }
        }
        
        // Validar regex
        if (!pattern.test(value)) {
            showError(input, CONFIG.messages[type]);
            return false;
        }
        
        // Validar contra patrones SSTI
        if (containsSSTI(value)) {
            showError(input, 'Caracteres no permitidos detectados');
            return false;
        }
        
        removeError(input);
        return true;
    }
    
    /**
     * Detecta patrones SSTI/XSS en el valor
     */
    function containsSSTI(value) {
        const sstiPatterns = [
            /\{\{/, /\}\}/,           // Django templates
            /\{%/, /%}/,              // Django tags
            /<\s*script/i,            // Script tags
            /javascript:/i,           // JS protocol
            /on\w+\s*=/i,             // Event handlers
            /`/,                      // Backticks
            /\$\(/, /\$\{/,           // Command substitution
            /<%/                      // ERB
        ];
        
        return sstiPatterns.some(pattern => pattern.test(value));
    }
    
    /**
     * Manejador de eventos para typing
     */
    function handleInput(event) {
        const input = event.target;
        const type = input.dataset.validate;
        
        if (!type) return;
        
        // Para passwords, solo validar longitud
        if (type === 'password') {
            const value = input.value;
            if (value.length < 8 || value.length > 128) {
                showError(input, CONFIG.messages.password);
            } else {
                removeError(input);
            }
            return;
        }
        
        // Para otros campos, validación completa
        validateField(input);
    }
    
    /**
     * Previene caracteres peligrosos en tiempo real
     */
    function handleKeyDown(event) {
        const input = event.target;
        const type = input.dataset.validate;
        
        if (!type) return;
        
        // Lista de teclas permitidas (no bloquear)
        const allowedKeys = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'PageUp', 'PageDown'
        ];
        
        if (allowedKeys.includes(event.key)) return;
        
        // Para passwords, permitir todo
        if (type === 'password') return;
        
        // Obtener el carácter
        const char = event.key;
        
        // Patrones de caracteres peligrosos según el tipo
        let dangerousPatterns = [
            '{', '}', '%', '<', '>', '`', '$', ';', '|', '&'
        ];
        
        // Para nombres, bloquear más cosas
        if (type === 'name') {
            dangerousPatterns = dangerousPatterns.concat([
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                '!', '@', '#', '=', '+', '*', '/', '\\', '_',
                '.', ',', '(', ')', '[', ']', '"', "'", '~'
            ]);
        }
        
        // Para emails, permitir @ y .
        if (type === 'email') {
            dangerousPatterns = dangerousPatterns.filter(p => p !== '@' && p !== '.');
        }
        
        // Bloquear
        if (dangerousPatterns.includes(char)) {
            event.preventDefault();
            showError(input, 'Carácter no permitido');
            
            // Auto-ocultar error después de 2 segundos
            setTimeout(() => removeError(input), 2000);
        }
    }

    // =========================================================================
    // API PÚBLICA
    // =========================================================================
    
    return {
        /**
         * Inicializa la validación en todos los campos con data-validate
         */
        init: function() {
            const inputs = document.querySelectorAll('[data-validate]');
            
            inputs.forEach(input => {
                // Eventos para validación en tiempo real
                input.addEventListener('input', handleInput);
                input.addEventListener('blur', handleInput);
                
                // Prevenir caracteres peligrosos
                input.addEventListener('keydown', handleKeyDown);
            });
            
            console.log('[Seguridad] Inicializado correctamente');
        },
        
        /**
         * Valida un campo específico
         */
        validate: function(input) {
            return validateField(input);
        },
        
        /**
         * Valida todo el formulario
         */
        validateForm: function(formId) {
            const form = document.getElementById(formId);
            if (!form) return false;
            
            const inputs = form.querySelectorAll('[data-validate]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            return isValid;
        },
        
        /**
         * Valida un valor directamente (sin input)
         */
        validateValue: function(value, type) {
            if (!value || !type) return true;
            
            const pattern = getConfig(type);
            if (!pattern.test(value)) return false;
            
            if (containsSSTI(value)) return false;
            
            return true;
        },
        
        /**
         * Escanea un valor y retorna true si es seguro
         */
        isSecure: function(value) {
            if (!value) return true;
            return !containsSSTI(value) && /^[^{}<>%`$;|&]+$/.test(value);
        },
        
        /**
         * Versión del módulo
         */
        version: '1.0.0'
    };
})();

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Seguridad.init());
} else {
    Seguridad.init();
}
