/**
 * RAG Chat JavaScript
 * Maneja la interacción del chat con la API RAG
 */

// Estado global
let currentCollectionId = null;
let isProcessing = false;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    loadCollections();
    setupEventListeners();
});

/**
 * Configura los event listeners
 */
function setupEventListeners() {
    const collectionSelect = document.getElementById('collection-select');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadForm = document.getElementById('upload-form');
    const pdfFile = document.getElementById('pdf-file');

    // Cambio de colección
    collectionSelect.addEventListener('change', (e) => {
        currentCollectionId = e.target.value;
        if (currentCollectionId) {
            enableChat();
            clearMessages();
            addSystemMessage(`Has seleccionado: ${e.target.options[e.target.selectedIndex].text}`);
        } else {
            disableChat();
        }
    });

    // Input auto-resize
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = chatInput.scrollHeight + 'px';
    });

    // Enter para enviar (Shift+Enter para nueva línea)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Botón enviar
    sendBtn.addEventListener('click', sendMessage);

    // Upload form
    uploadForm.addEventListener('submit', handleUpload);

    // File input change
    pdfFile.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || 'Ningún archivo seleccionado';
        document.querySelector('.file-name').textContent = fileName;

        // Auto-populate title
        const titleInput = document.getElementById('pdf-title');
        if (!titleInput.value && fileName !== 'Ningún archivo seleccionado') {
            titleInput.value = fileName.replace('.pdf', '');
        }
    });
}

/**
 * Carga las colecciones disponibles
 */
async function loadCollections() {
    try {
        const response = await fetch('/rag-chat/api/documents/');
        const data = await response.json();

        const select = document.getElementById('collection-select');
        select.innerHTML = '<option value="">Selecciona un manual...</option>';

        let manualUsuarioId = null;

        if (data.documents && data.documents.length > 0) {
            data.documents.forEach(doc => {
                if (doc.status === 'indexed') {
                    const option = document.createElement('option');
                    option.value = doc.id;
                    option.textContent = `${doc.title} (${doc.page_count} páginas)`;
                    select.appendChild(option);
                    
                    // Detectar el Manual de Usuario
                    if (doc.title.toLowerCase().includes('manual de usuario')) {
                        manualUsuarioId = doc.id;
                    }
                }
            });
            
            // Seleccionar automáticamente el Manual de Usuario
            if (manualUsuarioId) {
                select.value = manualUsuarioId;
                currentCollectionId = manualUsuarioId;
                enableChat();
                clearMessages();
                addSystemMessage('📖 Manual de Usuario cargado. ¡Pregúntame lo que necesites!');
            }
        } else {
            select.innerHTML = '<option value="">No hay manuales disponibles</option>';
            addSystemMessage('⚠️ No hay documentos indexados. Sube el Manual de Usuario para comenzar.', 'warning');
        }
    } catch (error) {
        console.error('Error cargando colecciones:', error);
        showNotification('Error al cargar documentos', 'error');
    }
}

/**
 * Envía un mensaje
 */
async function sendMessage() {
    if (isProcessing || !currentCollectionId) return;

    const input = document.getElementById('chat-input');
    const query = input.value.trim();

    if (!query) return;

    // Agregar mensaje del usuario
    addUserMessage(query);
    input.value = '';
    input.style.height = 'auto';

    // Agregar indicador de carga
    const loadingId = addLoadingMessage();
    isProcessing = true;

    try {
        const response = await fetch('/rag-chat/api/query/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                collection_id: currentCollectionId,
                query: query,
                top_k: 3
            })
        });

        const data = await response.json();

        // Remover loading
        removeMessage(loadingId);

        if (response.ok) {
            addAssistantMessage(data.answer, data.sources);
        } else {
            addErrorMessage(data.error || 'Error desconocido');
        }
    } catch (error) {
        removeMessage(loadingId);
        addErrorMessage('Error de conexión. Por favor intenta de nuevo.');
        console.error('Error:', error);
    } finally {
        isProcessing = false;
    }
}

/**
 * Agrega mensaje del usuario
 */
function addUserMessage(text) {
    const messagesContainer = document.getElementById('chat-messages');

    // Remover welcome message si existe
    const welcome = messagesContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-avatar">TÚ</div>
        <div class="message-content">
            <p class="message-text">${escapeHtml(text)}</p>
            <span class="message-timestamp">${formatTime(new Date())}</span>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Agrega mensaje del asistente
 */
function addAssistantMessage(text, sources = []) {
    const messagesContainer = document.getElementById('chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <div class="sources-title">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    Fuentes consultadas:
                </div>
                ${sources.map(source => `
                    <div class="source-item">
                        <div class="source-page">📄 Página ${source.page.join(', ')}</div>
                        <p class="source-text">${escapeHtml(source.content)}</p>
                        <div class="source-similarity">Relevancia: ${Math.round(source.similarity * 100)}%</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <p class="message-text">${escapeHtml(text)}</p>
            ${sourcesHtml}
            <span class="message-timestamp">${formatTime(new Date())}</span>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Agrega mensaje del sistema
 */
function addSystemMessage(text) {
    const messagesContainer = document.getElementById('chat-messages');

    const welcome = messagesContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <div class="message-avatar">ℹ️</div>
        <div class="message-content">
            <p class="message-text">${escapeHtml(text)}</p>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Agrega indicador de carga
 */
function addLoadingMessage() {
    const messagesContainer = document.getElementById('chat-messages');
    const loadingId = 'loading-' + Date.now();

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant loading';
    messageDiv.id = loadingId;
    messageDiv.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    return loadingId;
}

/**
 * Agrega mensaje de error
 */
function addErrorMessage(text) {
    const messagesContainer = document.getElementById('chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-avatar">⚠️</div>
        <div class="message-content">
            <p class="message-text" style="color: var(--color-dark);">Error: ${escapeHtml(text)}</p>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Remueve un mensaje
 */
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) message.remove();
}

/**
 * Limpia todos los mensajes
 */
function clearMessages() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = '';
}

/**
 * Habilita el chat
 */
function enableChat() {
    document.getElementById('chat-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    document.getElementById('chat-input').placeholder = 'Escribe tu pregunta aquí...';
}

/**
 * Deshabilita el chat
 */
function disableChat() {
    document.getElementById('chat-input').disabled = true;
    document.getElementById('send-btn').disabled = true;
    document.getElementById('chat-input').placeholder = 'Selecciona un manual primero...';
}

/**
 * Scroll al final
 */
function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Modal de upload
 */
function showUploadModal() {
    document.getElementById('upload-modal').style.display = 'flex';
}

function closeUploadModal() {
    document.getElementById('upload-modal').style.display = 'none';
    document.getElementById('upload-form').reset();
    document.querySelector('.file-name').textContent = 'Ningún archivo seleccionado';
    document.getElementById('upload-progress').style.display = 'none';
}

/**
 * Maneja el upload de PDF
 */
async function handleUpload(e) {
    e.preventDefault();

    const fileInput = document.getElementById('pdf-file');
    const titleInput = document.getElementById('pdf-title');
    const file = fileInput.files[0];

    if (!file) {
        showNotification('Por favor selecciona un archivo', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', titleInput.value);

    // Mostrar progreso
    const progressContainer = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const submitBtn = document.getElementById('submit-upload');

    progressContainer.style.display = 'block';
    submitBtn.disabled = true;

    try {
        progressText.textContent = 'Subiendo archivo...';
        progressFill.style.width = '30%';

        const response = await fetch('/rag-chat/api/upload/', {
            method: 'POST',
            body: formData
        });

        progressFill.style.width = '60%';
        progressText.textContent = 'Procesando documento...';

        const data = await response.json();

        if (response.ok) {
            progressFill.style.width = '100%';
            progressText.textContent = '¡Documento procesado exitosamente!';

            showNotification(`Documento "${data.title}" indexado con ${data.chunk_count} fragmentos`, 'success');

            // Recargar colecciones
            await loadCollections();

            // Cerrar modal después de un momento
            setTimeout(() => {
                closeUploadModal();
            }, 1500);
        } else {
            throw new Error(data.error || 'Error al procesar documento');
        }
    } catch (error) {
        console.error('Error en upload:', error);
        progressText.textContent = 'Error: ' + error.message;
        progressText.style.color = 'var(--color-dark)';
        showNotification('Error al subir documento: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
    }
}

/**
 * Muestra notificación
 */
function showNotification(message, type = 'info') {
    // Si existe un sistema de notificaciones del dashboard, úsalo
    // Si no, mostrar un alert simple
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
        new Notification('RAG Chat', { body: message });
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

/**
 * Escapa HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Formatea hora
 */
function formatTime(date) {
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}
