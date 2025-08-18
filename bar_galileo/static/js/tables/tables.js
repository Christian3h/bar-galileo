/**
 * Lógica para la gestión de mesas y pedidos en el Bar Galileo.
 * Incluye edición de mesas, gestión de modales para pedidos, y comunicación con la API y WebSockets.
 */

// ===== VARIABLES GLOBALES =====
let mesaActualId = null;
let pedidoActual = {};
let listaCompletaProductos = [];
let virtualStock = {}; // Objeto para el stock virtual: { productoId: cantidad }
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
      // Si el modal de pedido está abierto, actualizar la UI
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
    const data = await apiFetch(`/api/mesas/${mesaId}/pedido/`);
    document.getElementById("mesaNombre").textContent = data.mesa.nombre;
    pedidoActual = data.pedido;
    listaCompletaProductos = data.productos;

    // Inicializar el stock virtual
    listaCompletaProductos.forEach(p => {
      virtualStock[p.id_producto] = p.stock - (data.reservas_stock[p.id_producto] || 0);
    });

    actualizarListaProductosUI();
    actualizarPedidoItemsUI();
    document.getElementById("pedidoModal").style.display = "block";
  } catch (error) {
    console.error("Error al obtener datos del pedido:", error);
    showToast(error.message);
  }
}

function actualizarListaProductosUI() {
  const lista = document.getElementById("productosLista");
  lista.innerHTML = listaCompletaProductos.map(p => {
    const stock = virtualStock[p.id_producto] || 0;
    return `
    <div class="producto-item ${stock <= 0 ? 'disabled' : ''}" onclick="agregarOActualizarItem(${p.id_producto})">
      <div class="producto-row">
        <div class="producto-main">
          ${p.imagen ? `<img src="${p.imagen}" alt="${p.nombre}" class="producto-thumb">` : `<div class="thumb-placeholder">Sin img</div>`}
          <div>
            <strong>${p.nombre}</strong>
            <small class="text-muted">Stock: ${stock}</small>
          </div>
        </div>
        <span class="precio">$${p.precio_venta}</span>
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
            <span class="subtotal">$${item.subtotal}</span>
            <button class="btn btn-sm btn-danger btn-eliminar" onclick="eliminarItem(${item.id})">×</button>
          </div>
        </div>
      `;
    }).join("");
    document.getElementById("pedidoTotal").textContent = Number(pedidoActual.total || 0).toFixed(2);
  } else {
    itemsContainer.innerHTML = '<p class="pedido-vacio">No hay items en el pedido</p>';
    document.getElementById("pedidoTotal").textContent = "0.00";
  }
}

// ===== ACCIONES DE ITEMS DEL PEDIDO =====

async function agregarOActualizarItem(productoId) {
  const stock = virtualStock[productoId] || 0;
  const itemExistente = pedidoActual.items.find(i => i.producto.id === productoId);
  const cantidadActualEnPedido = itemExistente ? itemExistente.cantidad : 0;

  if (stock <= cantidadActualEnPedido) {
    showToast("No hay más stock disponible para este producto.");
    return;
  }

  if (itemExistente) {
    await cambiarCantidadItem(itemExistente.id, itemExistente.cantidad + 1);
  } else {
    try {
      const data = await apiFetch("/api/pedidos/agregar-item/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ mesa_id: mesaActualId, producto_id: productoId, cantidad: 1 }),
      });
      pedidoActual = data.pedido;
      actualizarPedidoItemsUI();
    } catch (error) {
      console.error('Error al agregar producto:', error);
      showToast(error.message);
    }
  }
}

async function cambiarCantidadItem(itemId, nuevaCantidad) {
  if (nuevaCantidad < 1) { return await eliminarItem(itemId); }

  const item = pedidoActual.items.find(i => i.id === itemId);
  const stock = virtualStock[item.producto.id] || 0;

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
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
  } catch (error) {
    console.error('Error al actualizar cantidad:', error);
    showToast(error.message);
  }
}

async function eliminarItem(itemId) {
  const confirmado = await showConfirm('Eliminar Item', '¿Estás seguro de que deseas eliminar este item del pedido?');
  if (!confirmado) return;

  try {
    const data = await apiFetch(`/api/pedidos/eliminar-item/${itemId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
    });
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
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
        setTimeout(() => window.location.reload(), 1500);
      }
    } catch (error) {
      console.error('Error al facturar:', error);
      showToast(error.message);
    }
  }
}

// ===== INICIALIZACIÓN Y EVENTOS =====

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mesa-card').forEach(actualizarVisibilidadBotonPedido);
    setupWebSocket(); // Iniciar conexión WebSocket
});

document.addEventListener('change', (event) => {
    if (event.target.matches('select[name="estado"]')) {
        const select = event.target;
        const mesaCard = select.closest('.mesa-card');
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
