/**
 * NOMINAS - FORMULARIO DE EMPLEADOS
 * Gestión de opciones de usuario, autocomplete y validaciones
 */

document.addEventListener('DOMContentLoaded', function() {
    const radioButtons = document.querySelectorAll('input[name="opcion_usuario"]');
    const usuarioExistenteFields = document.getElementById('usuario-existente-fields');
    const usuarioNuevoFields = document.getElementById('usuario-nuevo-fields');
    const buscarUsuarioInput = document.getElementById('id_buscar_usuario');
    const suggestionBox = document.getElementById('usuario-suggestions');
    const usuarioExistenteHidden = document.getElementById('id_usuario_existente');
    const usuarioSeleccionado = document.getElementById('usuario-seleccionado');

    let timeoutId = null;

    /**
     * Actualiza la visibilidad de los campos según la opción seleccionada
     */
    function updateFieldsVisibility() {
        const selectedValue = document.querySelector('input[name="opcion_usuario"]:checked')?.value;

        // Ocultar todos los campos
        if (usuarioExistenteFields) usuarioExistenteFields.classList.remove('active');
        if (usuarioNuevoFields) usuarioNuevoFields.classList.remove('active');

        // Resetear estilos de todas las opciones
        document.querySelectorAll('.usuario-option').forEach(opt => {
            opt.style.borderColor = '';
            opt.style.background = '';
        });

        // Mostrar los campos correspondientes y resaltar la opción
        if (selectedValue === 'usuario_existente' && usuarioExistenteFields) {
            usuarioExistenteFields.classList.add('active');
            const opt = document.querySelector(`.usuario-option[data-option="${selectedValue}"]`);
            if (opt) {
                opt.style.borderColor = 'var(--color-primary)';
                opt.style.background = 'var(--color-accent)';
            }
        } else if (selectedValue === 'usuario_nuevo' && usuarioNuevoFields) {
            usuarioNuevoFields.classList.add('active');
            const opt = document.querySelector(`.usuario-option[data-option="${selectedValue}"]`);
            if (opt) {
                opt.style.borderColor = 'var(--color-primary)';
                opt.style.background = 'var(--color-accent)';
            }
        } else if (selectedValue === 'sin_usuario') {
            const opt = document.querySelector(`.usuario-option[data-option="${selectedValue}"]`);
            if (opt) {
                opt.style.borderColor = 'var(--color-primary)';
                opt.style.background = 'var(--color-accent)';
            }
        }
    }

    /**
     * Click en la caja de opción selecciona el radio button
     */
    document.querySelectorAll('.usuario-option').forEach(option => {
        option.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    updateFieldsVisibility();
                }
            }
        });
    });

    /**
     * Listener para cambios en los radio buttons
     */
    radioButtons.forEach(radio => {
        radio.addEventListener('change', updateFieldsVisibility);
    });

    /**
     * Autocomplete de usuarios
     */
    if (buscarUsuarioInput) {
        buscarUsuarioInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            const query = this.value.trim();

            if (query.length < 2) {
                suggestionBox.classList.remove('active');
                return;
            }

            // Debounce de 300ms
            timeoutId = setTimeout(() => {
                const url = buscarUsuarioInput.getAttribute('data-url') || '/nominas/api/buscar-usuarios/';

                fetch(`${url}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestionBox.innerHTML = '';

                        if (data.results.length === 0) {
                            suggestionBox.innerHTML = '<div class="usuario-suggestion" style="cursor: default; opacity: 0.6;">No se encontraron usuarios</div>';
                        } else {
                            data.results.forEach(usuario => {
                                const div = document.createElement('div');
                                div.className = 'usuario-suggestion';
                                div.innerHTML = `
                                    <div class="usuario-suggestion-name">${usuario.nombre_completo}</div>
                                    <div class="usuario-suggestion-details">
                                        ${usuario.username} - ${usuario.email}
                                        ${usuario.rol ? `<span style="margin-left: 10px; background: var(--color-primary); color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.75rem;">${usuario.rol}</span>` : ''}
                                    </div>
                                `;
                                div.addEventListener('click', () => seleccionarUsuario(usuario));
                                suggestionBox.appendChild(div);
                            });
                        }

                        suggestionBox.classList.add('active');
                    })
                    .catch(error => {
                        console.error('Error buscando usuarios:', error);
                    });
            }, 300);
        });

        /**
         * Cerrar sugerencias al hacer clic fuera
         */
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.usuario-autocomplete')) {
                suggestionBox.classList.remove('active');
            }
        });
    }

    /**
     * Selecciona un usuario del autocomplete
     */
    function seleccionarUsuario(usuario) {
        document.getElementById('usuario-sel-nombre').textContent = usuario.nombre_completo;
        document.getElementById('usuario-sel-detalles').innerHTML = `
            ${usuario.username} - ${usuario.email}
            ${usuario.rol ? `<span style="margin-left: 10px; background: var(--color-primary); color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.7rem;">${usuario.rol}</span>` : ''}
        `;

        usuarioSeleccionado.classList.add('active');
        buscarUsuarioInput.value = '';
        buscarUsuarioInput.style.display = 'none';
        suggestionBox.classList.remove('active');
        usuarioExistenteHidden.value = usuario.id;
    }

    /**
     * Limpia la selección de usuario
     */
    window.limpiarUsuarioSeleccionado = function() {
        usuarioSeleccionado.classList.remove('active');
        buscarUsuarioInput.style.display = 'block';
        buscarUsuarioInput.value = '';
        usuarioExistenteHidden.value = '';
    };

    // Inicializar visibilidad
    updateFieldsVisibility();
});
