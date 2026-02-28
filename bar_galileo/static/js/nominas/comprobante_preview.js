document.addEventListener('DOMContentLoaded', function () {
    // Seleccionar todos los botones de previsualización de comprobantes
    const buttons = document.querySelectorAll('.preview-comprobante');
    const modal = document.getElementById('comprobanteModal');
    const modalBody = document.getElementById('comprobanteModalBody');
    const modalTitle = document.getElementById('comprobanteModalTitle');
    const closeBtn = document.querySelector('.close-modal-preview');

    // Validar que los elementos del modal existan
    if (!modal || !modalBody || !modalTitle || !closeBtn) {
        console.error('Modal elements not found in the DOM.');
        return;
    }

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const url = this.dataset.url;
            const name = this.dataset.name || 'Comprobante';
            const extension = url.split('.').pop().toLowerCase();

            modal.style.display = 'block';

            if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension)) {
                modalTitle.textContent = 'Vista Previa de la Imagen';
                modalBody.innerHTML = `<img src="${url}" alt="${name}" style="max-width: 100%; max-height: 500px; border-radius: 8px; border: 2px solid var(--color-secondary);">`;

                const img = modalBody.querySelector('img');
                img.onerror = function () {
                    modalBody.innerHTML = '<p style="color: red;">Error al cargar la imagen.</p>';
                };
            } else if (extension === 'pdf') {
                modalTitle.textContent = 'Vista Previa del PDF';
                modalBody.innerHTML = `<embed src="${url}" type="application/pdf" style="width: 100%; height: 500px; border: 2px solid var(--color-secondary); border-radius: 8px;">`;
            } else {
                modalTitle.textContent = 'Formato no soportado';
                modalBody.innerHTML = '<p style="color: red;">No se puede previsualizar este tipo de archivo.</p>';
            }
        });
    });

    // Cerrar el modal al hacer clic en el botón de cerrar
    closeBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    // Cerrar el modal al hacer clic fuera del contenido
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
