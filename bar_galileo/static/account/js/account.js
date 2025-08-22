/**
 * ====================================
 * ACCOUNT.JS - BAR GALILEO
 * Funciones específicas para manejo de cuentas de usuario
 * ====================================
 */

/**
 * Funciones para autenticación y manejo de cuentas
 */
const AccountManager = {
    
    /**
     * Inicializar funciones de cuenta
     */
    init: function() {
        this.setupLoginForm();
        this.setupRegistrationForm();
        this.setupPasswordForms();
        this.setupProfileForms();
        this.setupSocialAuth();
    },
    
    /**
     * Configurar formulario de login
     */
    setupLoginForm: function() {
        const loginForm = document.querySelector('#login-form, .login-form, form[action*="login"]');
        
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                const username = loginForm.querySelector('input[name="login"], input[name="username"], input[name="email"]');
                const password = loginForm.querySelector('input[name="password"]');
                
                if (!AccountManager.validateLogin(username, password)) {
                    e.preventDefault();
                    return false;
                }
                
                AccountManager.showLoading(loginForm);
            });
            
            // Recordar usuario
            this.setupRememberMe(loginForm);
        }
    },
    
    /**
     * Configurar formulario de registro
     */
    setupRegistrationForm: function() {
        const signupForm = document.querySelector('#signup-form, .signup-form, form[action*="signup"]');
        
        if (signupForm) {
            signupForm.addEventListener('submit', function(e) {
                if (!AccountManager.validateSignup(signupForm)) {
                    e.preventDefault();
                    return false;
                }
                
                AccountManager.showLoading(signupForm);
            });
            
            // Validación de contraseña en tiempo real
            this.setupPasswordValidation(signupForm);
        }
    },
    
    /**
     * Configurar formularios de contraseña
     */
    setupPasswordForms: function() {
        // Cambio de contraseña
        const passwordChangeForm = document.querySelector('form[action*="password/change"]');
        if (passwordChangeForm) {
            this.setupPasswordValidation(passwordChangeForm);
        }
        
        // Reset de contraseña
        const passwordResetForm = document.querySelector('form[action*="password/reset"]');
        if (passwordResetForm) {
            passwordResetForm.addEventListener('submit', function(e) {
                const email = passwordResetForm.querySelector('input[type="email"]');
                if (!AccountManager.validateEmail(email.value)) {
                    e.preventDefault();
                    AccountManager.showError('Por favor ingresa un email válido');
                    return false;
                }
                
                AccountManager.showLoading(passwordResetForm);
            });
        }
    },
    
    /**
     * Configurar formularios de perfil
     */
    setupProfileForms: function() {
        const profileForm = document.querySelector('#profile-form, .profile-form');
        
        if (profileForm) {
            profileForm.addEventListener('submit', function(e) {
                AccountManager.showLoading(profileForm);
            });
            
            // Vista previa de imagen de perfil
            const imageInput = profileForm.querySelector('input[type="file"]');
            if (imageInput) {
                imageInput.addEventListener('change', function(e) {
                    AccountManager.previewProfileImage(e.target);
                });
            }
        }
    },
    
    /**
     * Configurar autenticación social
     */
    setupSocialAuth: function() {
        const socialButtons = document.querySelectorAll('.social-auth-btn, .btn-social');
        
        socialButtons.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                // Mostrar indicador de carga para auth social
                btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Conectando...';
                btn.disabled = true;
            });
        });
    },
    
    /**
     * Configurar "Recordarme"
     */
    setupRememberMe: function(form) {
        const rememberCheckbox = form.querySelector('input[name="remember"]');
        
        if (rememberCheckbox) {
            // Cargar preferencia guardada
            const savedPreference = localStorage.getItem('remember_me_preference');
            if (savedPreference === 'true') {
                rememberCheckbox.checked = true;
            }
            
            // Guardar preferencia
            rememberCheckbox.addEventListener('change', function() {
                localStorage.setItem('remember_me_preference', this.checked);
            });
        }
    },
    
    /**
     * Configurar validación de contraseña
     */
    setupPasswordValidation: function(form) {
        const passwordField = form.querySelector('input[name="password1"], input[name="new_password1"], input[name="password"]');
        const confirmField = form.querySelector('input[name="password2"], input[name="new_password2"]');
        
        if (passwordField) {
            passwordField.addEventListener('input', function() {
                AccountManager.validatePasswordStrength(passwordField);
            });
        }
        
        if (confirmField) {
            confirmField.addEventListener('input', function() {
                AccountManager.validatePasswordMatch(passwordField, confirmField);
            });
        }
    },
    
    /**
     * Validar formulario de login
     */
    validateLogin: function(usernameField, passwordField) {
        let isValid = true;
        
        if (!usernameField.value.trim()) {
            this.showFieldError(usernameField, 'El usuario/email es requerido');
            isValid = false;
        }
        
        if (!passwordField.value.trim()) {
            this.showFieldError(passwordField, 'La contraseña es requerida');
            isValid = false;
        }
        
        return isValid;
    },
    
    /**
     * Validar formulario de registro
     */
    validateSignup: function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('input[required]');
        
        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                AccountManager.showFieldError(field, 'Este campo es requerido');
                isValid = false;
            }
        });
        
        // Validaciones específicas
        const emailField = form.querySelector('input[type="email"]');
        if (emailField && !this.validateEmail(emailField.value)) {
            this.showFieldError(emailField, 'Ingresa un email válido');
            isValid = false;
        }
        
        const passwordField = form.querySelector('input[name="password1"]');
        const confirmField = form.querySelector('input[name="password2"]');
        
        if (passwordField && confirmField) {
            if (passwordField.value !== confirmField.value) {
                this.showFieldError(confirmField, 'Las contraseñas no coinciden');
                isValid = false;
            }
        }
        
        return isValid;
    },
    
    /**
     * Validar fuerza de contraseña
     */
    validatePasswordStrength: function(passwordField) {
        const password = passwordField.value;
        const strength = this.calculatePasswordStrength(password);
        
        // Mostrar indicador de fuerza
        this.showPasswordStrength(passwordField, strength);
        
        return strength.score >= 3; // Requerir al menos fuerza media
    },
    
    /**
     * Calcular fuerza de contraseña
     */
    calculatePasswordStrength: function(password) {
        let score = 0;
        let feedback = [];
        
        if (password.length >= 8) score++;
        else feedback.push('Al menos 8 caracteres');
        
        if (/[a-z]/.test(password)) score++;
        else feedback.push('Letras minúsculas');
        
        if (/[A-Z]/.test(password)) score++;
        else feedback.push('Letras mayúsculas');
        
        if (/[0-9]/.test(password)) score++;
        else feedback.push('Números');
        
        if (/[^A-Za-z0-9]/.test(password)) score++;
        else feedback.push('Caracteres especiales');
        
        const levels = ['Muy débil', 'Débil', 'Regular', 'Fuerte', 'Muy fuerte'];
        
        return {
            score: score,
            level: levels[score],
            feedback: feedback
        };
    },
    
    /**
     * Mostrar indicador de fuerza de contraseña
     */
    showPasswordStrength: function(passwordField, strength) {
        let strengthIndicator = passwordField.parentNode.querySelector('.password-strength');
        
        if (!strengthIndicator) {
            strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            passwordField.parentNode.appendChild(strengthIndicator);
        }
        
        const colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997'];
        const color = colors[strength.score];
        
        strengthIndicator.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${(strength.score / 5) * 100}%; background-color: ${color}"></div>
            </div>
            <div class="strength-text" style="color: ${color}">
                Fuerza: ${strength.level}
            </div>
        `;
        
        if (strength.feedback.length > 0 && strength.score < 3) {
            strengthIndicator.innerHTML += `
                <div class="strength-feedback">
                    <small>Incluye: ${strength.feedback.join(', ')}</small>
                </div>
            `;
        }
    },
    
    /**
     * Validar que las contraseñas coincidan
     */
    validatePasswordMatch: function(passwordField, confirmField) {
        if (passwordField.value !== confirmField.value) {
            this.showFieldError(confirmField, 'Las contraseñas no coinciden');
            return false;
        } else {
            this.clearFieldError(confirmField);
            return true;
        }
    },
    
    /**
     * Validar email
     */
    validateEmail: function(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    },
    
    /**
     * Vista previa de imagen de perfil
     */
    previewProfileImage: function(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                let preview = document.querySelector('.profile-image-preview');
                
                if (!preview) {
                    preview = document.createElement('img');
                    preview.className = 'profile-image-preview';
                    preview.style.cssText = 'max-width: 150px; max-height: 150px; border-radius: 50%; margin: 10px 0;';
                    input.parentNode.appendChild(preview);
                }
                
                preview.src = e.target.result;
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    },
    
    /**
     * Mostrar error en campo
     */
    showFieldError: function(field, message) {
        field.classList.add('is-invalid');
        
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    },
    
    /**
     * Limpiar error de campo
     */
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    },
    
    /**
     * Mostrar error general
     */
    showError: function(message) {
        const errorContainer = document.querySelector('.messages') || document.body;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        
        errorContainer.insertBefore(errorDiv, errorContainer.firstChild);
        
        // Auto-remover después de 5 segundos
        setTimeout(function() {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    },
    
    /**
     * Mostrar indicador de carga
     */
    showLoading: function(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.textContent || submitBtn.value;
            submitBtn.disabled = true;
            submitBtn.setAttribute('data-original-text', originalText);
            
            if (submitBtn.tagName === 'BUTTON') {
                submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Procesando...';
            } else {
                submitBtn.value = 'Procesando...';
            }
        }
    },
    
    /**
     * Logout con confirmación
     */
    logout: function(confirmMessage = '¿Estás seguro de que quieres cerrar sesión?') {
        if (confirm(confirmMessage)) {
            window.location.href = '/accounts/logout/';
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    AccountManager.init();
});

// Agregar estilos CSS para indicador de fuerza de contraseña
const style = document.createElement('style');
style.textContent = `
    .password-strength {
        margin-top: 8px;
    }
    
    .strength-bar {
        width: 100%;
        height: 4px;
        background-color: #e9ecef;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .strength-fill {
        height: 100%;
        transition: width 0.3s ease, background-color 0.3s ease;
    }
    
    .strength-text {
        font-size: 12px;
        margin-top: 4px;
        font-weight: 600;
    }
    
    .strength-feedback {
        font-size: 11px;
        color: #6c757d;
        margin-top: 2px;
    }
    
    .profile-image-preview {
        display: block;
        margin: 10px auto;
        border: 2px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .social-auth-btn {
        width: 100%;
        margin: 5px 0;
        padding: 10px;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        background: #fff;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .social-auth-btn:hover {
        background: #f8f9fa;
        transform: translateY(-1px);
    }
    
    .social-auth-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
`;

document.head.appendChild(style);

// Exponer AccountManager globalmente
window.AccountManager = AccountManager;
