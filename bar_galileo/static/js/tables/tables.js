/**
 * Lógica para la gestión de mesas y pedidos en el Bar Galileo.
 * Incluye edición de mesas, gestión de modales para pedidos, y comunicación con la API y WebSockets.
 */

// Función de utilidad para formatear números como precios colombianos
function formatNumberForPrice(number) {
  if (number === null || number === undefined || number === '') {
    return '$0';
  }
  
  try {
    const num = parseInt(number);
    const formatted = new Intl.NumberFormat('de-DE', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
    return `$${formatted}`;
  } catch (error) {
    return '$0';
  }
}


// ===== VARIABLES GLOBALES =====
let mesaActualId = null;
let pedidoActual = {};
let listaCompletaProductos = [];
let listaCompletaUsuarios = [];
let virtualStock = {};
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

// ===== COMPONENTES DE UI (TOAST Y CONFIRM) =====

function showToast(message, type = 'error') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.remove(); }, 5000);
}

function showConfirm(title, message) {
  return new Promise(resolve => {
    const modal = document.getElementById('confirmModal');
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    const [confirmBtn, cancelBtn, closeBtn] = ['confirmOk', 'confirmCancel', 'confirmClose'].map(id => document.getElementById(id));
    const cleanup = () => {
      modal.style.display = 'none';
      confirmBtn.onclick = cancelBtn.onclick = closeBtn.onclick = null;
    };
    confirmBtn.onclick = () => { cleanup(); resolve(true); };
    cancelBtn.onclick = closeBtn.onclick = () => { cleanup(); resolve(false); };
    modal.style.display = 'flex';
  });
}

// ===== WEBSOCKETS PARA STOCK EN TIEMPO REAL =====

function setupWebSocket() {
  const protocol = window.location.protocol === 'https' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/stock_updates/`);

  ws.onopen = () => console.log("[WebSocket] Conectado al canal de stock.");
  ws.onclose = () => console.log("[WebSocket] Desconectado del canal de stock.");
  ws.onerror = (err) => console.error("[WebSocket] Error:", err);

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'stock_update') {
      const { product_id, delta } = data.message;
      if (virtualStock[product_id] !== undefined) {
        virtualStock[product_id] += delta;
      }
      if (document.getElementById("pedidoModal").style.display === "block") {
        actualizarListaProductosUI();
        actualizarPedidoItemsUI();
      }
    }
  };
}

// ===== MANEJO DE ERRORES Y PETICIONES API =====

async function apiFetch(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `Error del servidor: ${response.status}` }));
    throw new Error(errorData.error || 'Ocurrió un error inesperado.');
  }
  return response.json();
}

// ===== LÓGICA DE VISIBILIDAD Y ESTADOS DE MESA =====

function actualizarVisibilidadBotonPedido(mesaCard) {
    const botonPedido = mesaCard.querySelector('button[onclick*="gestionarPedido"]');
    if (botonPedido) {
        botonPedido.style.display = mesaCard.classList.contains('ocupada') ? 'inline-block' : 'none';
    }
}

// ===== GESTIÓN DEL MODAL DE PEDIDO =====

async function gestionarPedido(mesaId) {
  mesaActualId = mesaId;
  try {
    const [pedidoData, usuariosData] = await Promise.all([
        apiFetch(`/api/mesas/${mesaId}/pedido/`),
        apiFetch(`/api/users/`)
    ]);

    document.getElementById("mesaNombre").textContent = pedidoData.mesa.nombre;
    pedidoActual = pedidoData.pedido;
    listaCompletaProductos = pedidoData.productos;
    listaCompletaUsuarios = usuariosData.users;

    listaCompletaProductos.forEach(p => {
      virtualStock[p.id_producto] = p.stock - (pedidoData.reservas_stock[p.id_producto] || 0);
    });

    actualizarListaProductosUI();
    actualizarPedidoItemsUI();
    actualizarUsuariosUI();

    document.getElementById("pedidoModal").style.display = "block";
  } catch (error) {
    console.error("Error al obtener datos del pedido o usuarios:", error);
    showToast(error.message);
  }
}

function actualizarListaProductosUI() {
  const lista = document.getElementById("productosLista");
  lista.innerHTML = listaCompletaProductos.map(p => {
    const stock = virtualStock[p.id_producto] || 0;
    return `
    <div class="producto-item ${stock <= 0 ? 'disabled' : ''}" onclick="mostrarControlCantidad(${p.id_producto})">
      <div class="producto-row">
        <div class="producto-main">
          ${p.imagen ? `<img src="${p.imagen}" alt="${p.nombre}" class="producto-thumb">` : `<div class="thumb-placeholder">Sin img</div>`}
          <div>
            <strong>${p.nombre}</strong>
            <small class="text-muted">Stock: ${stock}</small>
          </div>
        </div>
        <span class="precio">${formatNumberForPrice(p.precio_venta)}</span>
      </div>
    </div>
  `}).join("");
}

function actualizarPedidoItemsUI() {
  const itemsContainer = document.getElementById("pedidoItems");
  if (pedidoActual && pedidoActual.items && pedidoActual.items.length > 0) {
    itemsContainer.innerHTML = pedidoActual.items.map(item => {
      const stock = virtualStock[item.producto.id] || 0;
      const atascadoEnStock = item.cantidad >= stock;
      return `
        <div class="pedido-item">
          <div class="pedido-info"><strong>${item.producto.nombre}</strong></div>
          <div class="pedido-controles">
            <div class="cantidad">
              <button onclick="cambiarCantidadItem(${item.id}, ${item.cantidad - 1})" class="btn-cantidad">-</button>
              <span class="cantidad-valor">${item.cantidad}</span>
              <button onclick="cambiarCantidadItem(${item.id}, ${item.cantidad + 1})" class="btn-cantidad" ${atascadoEnStock ? 'disabled' : ''}>+</button>
            </div>
            <span class="subtotal">${formatNumberForPrice(item.subtotal)}</span>
            <button class="btn btn-sm btn-danger btn-eliminar" onclick="eliminarItem(${item.id})">×</button>
          </div>
        </div>
      `;
    }).join("");
    document.getElementById("pedidoTotal").textContent = formatNumberForPrice(pedidoActual.total || 0);
  } else {
    itemsContainer.innerHTML = '<p class="pedido-vacio">No hay items en el pedido</p>';
    document.getElementById("pedidoTotal").textContent = "$0";
  }
}

// ===== GESTIÓN DE USUARIOS EN PEDIDO =====

function actualizarUsuariosUI() {
    const assignedUsersList = document.getElementById('assignedUsersList');
    if (pedidoActual.usuarios && pedidoActual.usuarios.length > 0) {
        assignedUsersList.innerHTML = pedidoActual.usuarios.map(user => `
            <div class="assigned-user">
                <span>${user.username}</span>
                <button class="btn btn-sm btn-danger" onclick="gestionarUsuarioEnPedido(${user.id}, 'remove')">×</button>
            </div>
        `).join('');
    } else {
        assignedUsersList.innerHTML = '<p class="text-muted">No hay clientes en este pedido.</p>';
    }
}

function renderizarResultadosBusquedaUsuarios(terminoBusqueda) {
    const resultsContainer = document.getElementById('userSearchResults');
    if (!terminoBusqueda) {
        resultsContainer.innerHTML = '';
        return;
    }

    const idsUsuariosAsignados = new Set(pedidoActual.usuarios.map(u => u.id));
    const resultados = listaCompletaUsuarios.filter(user => 
        user.username.toLowerCase().includes(terminoBusqueda.toLowerCase()) && !idsUsuariosAsignados.has(user.id)
    );

    if (resultados.length > 0) {
        resultsContainer.innerHTML = resultados.map(user => `
            <div class="user-search-result" onclick="gestionarUsuarioEnPedido(${user.id}, 'add')">
                ${user.username}
            </div>
        `).join('');
    } else {
        resultsContainer.innerHTML = '<p class="text-muted">No se encontraron clientes.</p>';
    }
}

async function gestionarUsuarioEnPedido(userId, action) {
    try {
        await apiFetch(`/api/pedidos/${pedidoActual.id}/usuarios/`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
            body: JSON.stringify({ user_id: userId, action: action }),
        });

        const data = await apiFetch(`/api/mesas/${mesaActualId}/pedido/`);
        pedidoActual = data.pedido;
        
        actualizarUsuariosUI();
        
        const searchInput = document.getElementById('userSearchInput');
        searchInput.value = '';
        renderizarResultadosBusquedaUsuarios('');

    } catch (error) {
        console.error(`Error al ${action === 'add' ? 'agregar' : 'eliminar'} usuario:`, error);
        showToast(error.message);
    }
}

// ===== MODAL DE CANTIDAD =====

function mostrarControlCantidad(productoId) {
  const producto = listaCompletaProductos.find(p => p.id_producto === productoId);
  const stock = virtualStock[productoId] || 0;
  if (stock <= 0) {
    showToast("No hay stock disponible para este producto.");
    return;
  }

  cerrarModalCantidad();
  const modal = document.createElement('div');
  modal.id = 'modalCantidad';
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-box">
      <h4 class="modal-title">Agregar ${producto.nombre}</h4>
      <p class="modal-price">Precio: ${formatNumberForPrice(producto.precio_venta)} / Stock: ${stock}</p>
      <div class="modal-counter">
        <button type="button" onclick="cambiarCantidadEnModal(-1)" class="btn-cantidad btn-cantidad--lg">-</button>
        <input type="number" id="cantidadInput" value="1" min="1" max="${stock}" class="input-cantidad" />
        <button type="button" onclick="cambiarCantidadEnModal(1)" class="btn-cantidad btn-cantidad--lg">+</button>
      </div>
      <div class="modal-actions">
        <button onclick="cerrarModalCantidad()" class="btn btn-danger btn-sm">Cancelar</button>
        <button onclick="confirmarAgregarProducto(${productoId})" class="btn btn-success btn-sm">Agregar</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  document.getElementById('cantidadInput').focus();
}

function cambiarCantidadEnModal(delta) {
  const input = document.getElementById('cantidadInput');
  const max = parseInt(input.max, 10);
  let newValue = parseInt(input.value, 10) + delta;
  if (newValue < 1) newValue = 1;
  if (newValue > max) newValue = max;
  input.value = newValue;
}

function cerrarModalCantidad() {
  const modal = document.getElementById('modalCantidad');
  if (modal) modal.remove();
}

// ===== ACCIONES DE ITEMS DEL PEDIDO =====

async function confirmarAgregarProducto(productoId) {
  const cantidad = parseInt(document.getElementById('cantidadInput').value, 10);
  if (isNaN(cantidad) || cantidad < 1) return;

  const stock = virtualStock[productoId] || 0;
  const itemExistente = pedidoActual.items.find(i => i.producto.id === productoId);
  const cantidadPrevia = itemExistente ? itemExistente.cantidad : 0;

  if (stock < cantidadPrevia + cantidad) {
    showToast(`Stock insuficiente. Solo puedes agregar ${stock - cantidadPrevia} más.`);
    return;
  }

  try {
    const data = await apiFetch("/api/pedidos/agregar-item/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify({ mesa_id: mesaActualId, producto_id: productoId, cantidad: cantidad }),
    });
    virtualStock[productoId] -= cantidad;
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
    actualizarListaProductosUI();
    cerrarModalCantidad();
  } catch (error) {
    console.error('Error al agregar producto:', error);
    showToast(error.message);
  }
}

async function cambiarCantidadItem(itemId, nuevaCantidad) {
  const item = pedidoActual.items.find(i => i.id === itemId);
  const old_cantidad = item.cantidad;

  if (nuevaCantidad < 1) { return await eliminarItem(itemId); }

  const stock = virtualStock[item.producto.id] + old_cantidad;
  if (stock < nuevaCantidad) {
    showToast(`Stock insuficiente. Disponible: ${stock}`);
    return;
  }

  try {
    const data = await apiFetch(`/api/pedidos/actualizar-item/${itemId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify({ cantidad: nuevaCantidad }),
    });
    const delta = nuevaCantidad - old_cantidad;
    virtualStock[item.producto.id] -= delta;
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
    actualizarListaProductosUI();
  } catch (error) {
    console.error('Error al actualizar cantidad:', error);
    showToast(error.message);
  }
}

async function eliminarItem(itemId) {
  const confirmado = await showConfirm('Eliminar Item', '¿Estás seguro de que deseas eliminar este item del pedido?');
  if (!confirmado) return;

  const item = pedidoActual.items.find(i => i.id === itemId);
  if (!item) {
    console.error("Intentando eliminar un item que no se encontró en el pedido actual.");
    return;
  }
  const productoId = item.producto.id;
  const cantidad = item.cantidad;

  try {
    const data = await apiFetch(`/api/pedidos/eliminar-item/${itemId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
    });
    virtualStock[productoId] += cantidad;
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
    actualizarListaProductosUI();
    showToast('Item eliminado correctamente', 'success');
  } catch (error) {
    console.error('Error al eliminar item:', error);
    showToast(error.message);
  }
}

// ===== FACTURACIÓN =====

async function facturarPedido() {
  if (!pedidoActual || !pedidoActual.items || !pedidoActual.items.length) {
    return showToast("No hay items en el pedido para facturar.");
  }
  const confirmado = await showConfirm('Facturar Pedido', '¿Estás seguro de que deseas facturar este pedido? Esta acción actualizará el inventario.');
  if (confirmado) {
    try {
      const data = await apiFetch(`/api/pedidos/${pedidoActual.id}/facturar/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
      });
      if (data.success) {
        showToast('Pedido facturado exitosamente', 'success');
        window.location.href = data.factura_url;
      }
    } catch (error) {
      console.error('Error al facturar:', error);
      showToast(error.message);
    }
  }
}

function liberarMesa(mesaId, tienePedidos) {
    const submitForm = () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/mesas/${mesaId}/liberar/`;
        const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').cloneNode(true);
        form.appendChild(csrf);
        document.body.appendChild(form);
        form.submit();
    };

    if (tienePedidos) {
        showConfirm(
            'Liberar Mesa',
            'Esta mesa tiene pedidos sin facturar. ¿Estás seguro de que deseas liberarla? Los pedidos serán eliminados.'
        ).then(confirmed => {
            if (confirmed) {
                submitForm();
            }
        });
    } else {
        submitForm();
    }
}

// ===== INICIALIZACIÓN Y EVENTOS =====

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mesa-card').forEach(actualizarVisibilidadBotonPedido);
    setupWebSocket();

    document.getElementById('userSearchInput').addEventListener('input', (e) => {
        renderizarResultadosBusquedaUsuarios(e.target.value);
    });
});

document.addEventListener('change', (event) => {
    if (event.target.matches('select[name="estado"]')) {
        select.closest('form').submit();
    }
});

function cerrarModal() {
  document.getElementById("pedidoModal").style.display = "none";
}

document.getElementById("buscarProducto").addEventListener("input", (e) => {
  const busqueda = e.target.value.toLowerCase();
  document.querySelectorAll(".producto-item").forEach(item => {
    const nombre = item.querySelector("strong").textContent.toLowerCase();
    item.style.display = nombre.includes(busqueda) ? "" : "none";
  });
});

window.onclick = (event) => {
  if (event.target == document.getElementById("pedidoModal")) {
    cerrarModal();
  }
};

// ===== LÓGICA DE EDICIÓN DE MESA =====

function habilitarEdicion(id) {
  document.getElementById("ver_nombre_" + id).style.display = "none";
  document.getElementById("ver_desc_" + id).style.display = "none";
  document.getElementById("form_edit_" + id).style.display = "block";
  document.getElementById("editar_btn_" + id).style.display = "none";
}

function cancelarEdicion(id) {
  document.getElementById("ver_nombre_" + id).style.display = "block";
  document.getElementById("ver_desc_" + id).style.display = "block";
  document.getElementById("form_edit_" + id).style.display = "none";
  document.getElementById("editar_btn_" + id).style.display = "inline-block";
}