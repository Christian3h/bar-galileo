/**
 * JavaScript para el módulo de Gestión de Backups
 * Bar Galileo - Sistema de Backups Encriptados con GPG
 */

// Variables globales
let deleteType = '';
let deleteFilename = '';
let createBackupTipo = '';
let modoRestauracion = 'existente'; // 'existente' o 'subir'

// Inicializar DataTables y event listeners
$(document).ready(function() {
    initDataTables();
    initModalEventListeners();
});

/**
 * Inicializa las tablas de backups con DataTables
 */
function initDataTables() {
    // Tabla de backups DB
    const selDB = '#tabla-backups-db';
    if (document.querySelector(selDB)) {
        if ($.fn.dataTable.isDataTable(selDB)) {
            $(selDB).DataTable().destroy();
        }
        $(selDB).DataTable({
            language: { url: "/static/js/DataTables/es-ES.json" },
            responsive: true,
            pageLength: 10,
            lengthChange: true,
            ordering: true,
            order: [[2, 'desc']], // Ordenar por fecha descendente
            columnDefs: [{ targets: '_all', defaultContent: '' }]
        });
    }

    // Tabla de backups Media
    const selMedia = '#tabla-backups-media';
    if (document.querySelector(selMedia)) {
        if ($.fn.dataTable.isDataTable(selMedia)) {
            $(selMedia).DataTable().destroy();
        }
        $(selMedia).DataTable({
            language: { url: "/static/js/DataTables/es-ES.json" },
            responsive: true,
            pageLength: 10,
            lengthChange: true,
            ordering: true,
            order: [[2, 'desc']], // Ordenar por fecha descendente
            columnDefs: [{ targets: '_all', defaultContent: '' }]
        });
    }
}

/**
 * Inicializa los event listeners para cerrar modales al hacer clic fuera
 */
function initModalEventListeners() {
    const modals = ['deleteModal', 'createModal', 'restoreModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    if (modalId === 'deleteModal') cerrarModal();
                    else if (modalId === 'createModal') cerrarModalCrear();
                    else if (modalId === 'restoreModal') cerrarModalRestaurar();
                }
            });
        }
    });
}

/* ============================================================================
   FUNCIONES PARA CREAR BACKUP
   ============================================================================ */

/**
 * Muestra el modal de confirmación para crear backup
 * @param {string} tipo - Tipo de backup: 'completo', 'db', 'media'
 */
function crearBackup(tipo) {
    createBackupTipo = tipo;
    const tipoTexto = tipo === 'completo' ? 'Completo (Base de Datos + Archivos Media)' :
                      tipo === 'db' ? 'Solo Base de Datos' :
                      'Solo Archivos Media';
    document.getElementById('createBackupType').textContent = tipoTexto;
    document.getElementById('createModal').classList.add('active');
}

/**
 * Cierra el modal de creación de backup
 */
function cerrarModalCrear() {
    document.getElementById('createModal').classList.remove('active');
    createBackupTipo = '';
}

/**
 * Ejecuta la creación del backup después de la confirmación
 */
function confirmarCrearBackup() {
    const tipo = createBackupTipo;
    cerrarModalCrear();

    const btnCrear = document.querySelector(`button[onclick*="crearBackup('${tipo}')"]`);
    if (btnCrear) {
        btnCrear.disabled = true;
        btnCrear.textContent = 'Creando...';
    }

    fetch('/backups/crear/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `tipo=${tipo}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            console.error('Error al crear backup:', data.error);
            if (btnCrear) {
                btnCrear.disabled = false;
                btnCrear.textContent = 'Crear Backup';
            }
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error al crear backup:', error);
        if (btnCrear) {
            btnCrear.disabled = false;
            btnCrear.textContent = 'Crear Backup';
        }
        location.reload();
    });
}

/* ============================================================================
   FUNCIONES PARA ELIMINAR BACKUP
   ============================================================================ */

/**
 * Muestra el modal de confirmación para eliminar backup
 * @param {string} tipo - Tipo de backup: 'db' o 'media'
 * @param {string} filename - Nombre del archivo a eliminar
 */
function confirmarEliminar(tipo, filename) {
    deleteType = tipo;
    deleteFilename = filename;
    document.getElementById('deleteFileName').textContent = filename;
    document.getElementById('deleteModal').classList.add('active');
}

/**
 * Cierra el modal de eliminación
 */
function cerrarModal() {
    document.getElementById('deleteModal').classList.remove('active');
    deleteType = '';
    deleteFilename = '';
}

/**
 * Ejecuta la eliminación del backup después de la confirmación
 */
function eliminarBackup() {
    fetch('/backups/eliminar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `tipo=${deleteType}&filename=${deleteFilename}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            console.error('Error al eliminar backup:', data.error);
        }
        cerrarModal();
    })
    .catch(error => {
        console.error('Error al eliminar backup:', error);
        cerrarModal();
    });
}

/* ============================================================================
   FUNCIONES PARA RESTAURAR BACKUP
   ============================================================================ */

/**
 * Muestra el modal de restauración de backup
 */
function mostrarModalRestaurar() {
    document.getElementById('restoreModal').classList.add('active');
    modoRestauracion = 'existente';
    cambiarTab('existente');
}

/**
 * Cierra el modal de restauración
 */
function cerrarModalRestaurar() {
    document.getElementById('restoreModal').classList.remove('active');
    document.getElementById('restoreTipo').value = '';
    document.getElementById('restoreFile').value = '';
    document.getElementById('uploadFile').value = '';
    document.getElementById('restoreFileGroup').style.display = 'none';
    document.getElementById('uploadInfo').style.display = 'none';
    document.getElementById('btnRestaurar').disabled = true;
    modoRestauracion = 'existente';
}

/**
 * Cambia entre las pestañas del modal de restauración
 * @param {string} tab - 'existente' o 'subir'
 */
function cambiarTab(tab) {
    modoRestauracion = tab;

    // Actualizar clases de tabs
    document.getElementById('tabExistente').className = tab === 'existente' ? 'tab-btn active' : 'tab-btn';
    document.getElementById('tabSubir').className = tab === 'subir' ? 'tab-btn active' : 'tab-btn';

    // Mostrar/ocultar contenido
    document.getElementById('contenidoExistente').style.display = tab === 'existente' ? 'block' : 'none';
    document.getElementById('contenidoSubir').style.display = tab === 'subir' ? 'block' : 'none';

    // Reset botón restaurar
    document.getElementById('btnRestaurar').disabled = true;
}

/**
 * Valida el archivo subido por el usuario
 */
function validarArchivoSubida() {
    const fileInput = document.getElementById('uploadFile');
    const uploadInfo = document.getElementById('uploadInfo');
    const btnRestaurar = document.getElementById('btnRestaurar');

    if (fileInput.files.length === 0) {
        uploadInfo.style.display = 'none';
        btnRestaurar.disabled = true;
        return;
    }

    const file = fileInput.files[0];
    const filename = file.name;

    // Validar extensión
    if (!filename.endsWith('.psql.gpg') && !filename.endsWith('.media.zip.gpg')) {
        fileInput.value = '';
        uploadInfo.style.display = 'none';
        btnRestaurar.disabled = true;

        // Mostrar error en el uploadInfo
        document.getElementById('uploadFileName').textContent = '❌ Archivo no válido';
        document.getElementById('uploadFileSize').textContent = 'Debe ser .psql.gpg o .media.zip.gpg';
        uploadInfo.style.display = 'block';
        uploadInfo.style.backgroundColor = 'rgba(231, 76, 60, 0.1)';
        uploadInfo.style.borderLeft = '4px solid #e74c3c';
        return;
    }

    // Mostrar información del archivo
    document.getElementById('uploadFileName').textContent = filename;
    document.getElementById('uploadFileSize').textContent = `Tamaño: ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    uploadInfo.style.display = 'block';
    uploadInfo.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
    uploadInfo.style.borderLeft = '';
    btnRestaurar.disabled = false;
}

/**
 * Carga los backups disponibles en el servidor según el tipo seleccionado
 * Esta función será poblada dinámicamente por el template Django
 */
function cargarBackupsDisponibles() {
    const tipo = document.getElementById('restoreTipo').value;
    const selectFile = document.getElementById('restoreFile');
    const fileGroup = document.getElementById('restoreFileGroup');

    // Limpiar opciones
    selectFile.innerHTML = '<option value="">-- Seleccione un archivo --</option>';

    if (!tipo) {
        fileGroup.style.display = 'none';
        document.getElementById('btnRestaurar').disabled = true;
        return;
    }

    // Los backups se cargarán dinámicamente desde el template
    // Ver backup_list.html para la implementación con Django template tags

    fileGroup.style.display = 'block';

    // Habilitar botón cuando se seleccione archivo
    selectFile.onchange = function() {
        document.getElementById('btnRestaurar').disabled = !this.value;
    };
}

/**
 * Ejecuta la restauración del backup
 */
function ejecutarRestauracion() {
    const btnRestaurar = document.getElementById('btnRestaurar');
    btnRestaurar.disabled = true;
    btnRestaurar.textContent = 'Procesando...';

    if (modoRestauracion === 'subir') {
        ejecutarRestauracionDesdeArchivo(btnRestaurar);
    } else {
        ejecutarRestauracionDesdeServidor(btnRestaurar);
    }
}

/**
 * Restaura desde un archivo subido por el usuario
 * @param {HTMLElement} btnRestaurar - Botón de restaurar
 */
function ejecutarRestauracionDesdeArchivo(btnRestaurar) {
    const fileInput = document.getElementById('uploadFile');

    if (fileInput.files.length === 0) {
        btnRestaurar.disabled = false;
        btnRestaurar.textContent = 'Restaurar';
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('backup_file', file);

    btnRestaurar.textContent = 'Subiendo...';

    // Primero subir el archivo
    fetch('/backups/subir/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Archivo subido, ahora restaurar
            btnRestaurar.textContent = 'Restaurando...';
            return fetch('/backups/restaurar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: `tipo=${data.tipo}&filename=${data.filename}`
            });
        } else {
            throw new Error(data.error || 'Error al subir archivo');
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            throw new Error(data.error || 'Error al restaurar');
        }
    })
    .catch(error => {
        console.error('Error durante la restauración:', error.message);
        btnRestaurar.disabled = false;
        btnRestaurar.textContent = 'Restaurar';
        location.reload();
    });
}

/**
 * Restaura desde un backup existente en el servidor
 * @param {HTMLElement} btnRestaurar - Botón de restaurar
 */
function ejecutarRestauracionDesdeServidor(btnRestaurar) {
    const tipo = document.getElementById('restoreTipo').value;
    const filename = document.getElementById('restoreFile').value;

    if (!tipo || !filename) {
        btnRestaurar.disabled = false;
        btnRestaurar.textContent = 'Restaurar';
        return;
    }

    btnRestaurar.textContent = 'Restaurando...';

    fetch('/backups/restaurar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `tipo=${tipo}&filename=${filename}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            console.error('Error al restaurar:', data.error);
            btnRestaurar.disabled = false;
            btnRestaurar.textContent = 'Restaurar';
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error al restaurar backup:', error);
        btnRestaurar.disabled = false;
        btnRestaurar.textContent = 'Restaurar';
        location.reload();
    });
}

/* ============================================================================
   FUNCIONES AUXILIARES
   ============================================================================ */

/**
 * Obtiene el token CSRF de las cookies
 * @returns {string} Token CSRF
 */
function getCsrfToken() {
    const name = 'csrftoken';
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
