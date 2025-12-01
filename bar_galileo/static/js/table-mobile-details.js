/**
 * Sistema de visualización de detalles de tabla en móvil
 * Muestra información oculta por CSS responsivo en un modal
 */

(function() {
    'use strict';

    // Crear el modal una sola vez al cargar la página
    function createModal() {
        if (document.getElementById('table-details-modal')) {
            return; // Ya existe
        }

        const modalHTML = `
            <div id="table-details-modal" class="table-details-modal">
                <div class="table-details-modal-content">
                    <div class="table-details-modal-header">
                        <h3 id="table-details-modal-title">Detalles</h3>
                        <button class="table-details-modal-close" aria-label="Cerrar">&times;</button>
                    </div>
                    <div class="table-details-modal-body" id="table-details-modal-body">
                        <!-- Contenido dinámico -->
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Event listeners para cerrar el modal
        const modal = document.getElementById('table-details-modal');
        const closeBtn = modal.querySelector('.table-details-modal-close');

        closeBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    function openModal(title, content) {
        const modal = document.getElementById('table-details-modal');
        const modalTitle = document.getElementById('table-details-modal-title');
        const modalBody = document.getElementById('table-details-modal-body');

        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevenir scroll del body
    }

    function closeModal() {
        const modal = document.getElementById('table-details-modal');
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restaurar scroll
    }

    // Función para extraer datos de una fila
    function extractRowData(row) {
        const cells = row.querySelectorAll('td');
        const headers = row.closest('table').querySelectorAll('th');
        const data = [];

        cells.forEach((cell, index) => {
            if (index < headers.length - 1) { // Excluir columna de acciones
                const headerText = headers[index].textContent.trim();
                const cellContent = cell.innerHTML.trim();

                // Solo agregar si la celda tiene contenido
                if (cellContent && headerText.toLowerCase() !== 'acciones') {
                    data.push({
                        label: headerText,
                        value: cellContent,
                        isHidden: window.getComputedStyle(cell).display === 'none'
                    });
                }
            }
        });

        return data;
    }

    // Función para generar HTML del modal
    function generateModalContent(data) {
        let html = '<div class="table-details-list">';

        data.forEach(item => {
            const hiddenClass = item.isHidden ? ' hidden-field' : '';
            html += `
                <div class="table-details-item${hiddenClass}">
                    <div class="table-details-label">${item.label}:</div>
                    <div class="table-details-value">${item.value}</div>
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    // Agregar botones de "Ver detalles" a las tablas
    function addDetailsButtons(tableSelector) {
        const tables = document.querySelectorAll(tableSelector);

        tables.forEach(table => {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            const rows = tbody.querySelectorAll('tr');

            rows.forEach(row => {
                // Verificar si ya tiene botón de detalles
                if (row.querySelector('.btn-view-details')) return;

                // Verificar si es una fila vacía (con colspan que indica "No hay datos")
                const cellWithColspan = row.querySelector('td[colspan]');
                if (cellWithColspan) {
                    // Es una fila de mensaje vacío, no agregar botón
                    return;
                }

                // Verificar si la fila solo tiene una celda (probablemente mensaje vacío)
                const cells = row.querySelectorAll('td');
                if (cells.length === 1) {
                    return;
                }

                // Buscar la celda de acciones
                const actionCell = row.querySelector('td:last-child, .actions-cell');
                if (!actionCell) return;

                // Crear botón de ver detalles
                const detailsBtn = document.createElement('button');
                detailsBtn.className = 'btn btn-sm btn-secondary btn-view-details';
                detailsBtn.innerHTML = '<img src="/static/img/icons/info.svg" alt="Info" style="width:16px; height:16px;"><span class="btn-text-mobile"> Info</span>';
                detailsBtn.title = 'Ver todos los detalles';
                detailsBtn.type = 'button';

                // Event listener para mostrar detalles
                detailsBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const rowData = extractRowData(row);
                    const title = rowData.length > 0 ? rowData[0].value.replace(/<[^>]*>/g, '').substring(0, 50) : 'Detalles';
                    const content = generateModalContent(rowData);

                    openModal(title, content);
                });

                // Insertar el botón al inicio del contenedor de acciones
                const actionsDiv = actionCell.querySelector('.actions-cell, div, .btn-group');
                if (actionsDiv) {
                    actionsDiv.insertBefore(detailsBtn, actionsDiv.firstChild);
                } else {
                    actionCell.insertBefore(detailsBtn, actionCell.firstChild);
                }
            });
        });
    }

    // Inicializar cuando el DOM esté listo
    function init() {
        createModal();

        // Agregar botones a las tablas existentes
        addDetailsButtons('table.table');

        // Observar cambios en el DOM para tablas dinámicas (DataTables, AJAX, etc.)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    addDetailsButtons('table.table');
                }
            });
        });

        // Observar cambios en el body
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Exportar funciones para uso manual si es necesario
    window.TableMobileDetails = {
        init: init,
        addDetailsButtons: addDetailsButtons,
        openModal: openModal,
        closeModal: closeModal
    };

    // Auto-inicializar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
