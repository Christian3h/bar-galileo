/**
 * Lógica para la gestión de mesas y pedidos en el Bar Galileo.
 * Incluye edición de mesas, gestión de modales para pedidos, y comunicación con la API.
 */

// ===== VARIABLES GLOBALES =====
let mesaActualId = null;
let pedidoActual = {};
let listaCompletaProductos = [];
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

// ===== COMPONENTES DE UI (TOAST Y CONFIRM) =====

function showToast(message, type = 'error') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 5000);
}

function showConfirm(title, message) {
  return new Promise(resolve => {
    const modal = document.getElementById('confirmModal');
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;

    const confirmBtn = document.getElementById('confirmOk');
    const cancelBtn = document.getElementById('confirmCancel');
    const closeBtn = document.getElementById('confirmClose');

    const cleanup = () => {
      modal.style.display = 'none';
      confirmBtn.onclick = null;
      cancelBtn.onclick = null;
      closeBtn.onclick = null;
    };

    confirmBtn.onclick = () => { cleanup(); resolve(true); };
    cancelBtn.onclick = () => { cleanup(); resolve(false); };
    closeBtn.onclick = () => { cleanup(); resolve(false); };

    modal.style.display = 'flex';
  });
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
        const estado = mesaCard.classList.contains('ocupada');
        botonPedido.style.display = estado ? 'inline-block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mesa-card').forEach(actualizarVisibilidadBotonPedido);
});

document.addEventListener('change', async (event) => {
    if (event.target.matches('select[name="estado"]')) {
        const select = event.target;
        const mesaCard = select.closest('.mesa-card');
        const formulario = select.closest('form');
        const estadoSeleccionado = select.value;

        // Actualizar clase de la tarjeta para reflejar el nuevo estado visualmente
        mesaCard.classList.remove('disponible', 'ocupada', 'reservada', 'fuera-de-servicio');
        mesaCard.classList.add(estadoSeleccionado.replace(/\s+/g, '-').toLowerCase());

        // Actualizar visibilidad del botón de pedido inmediatamente
        actualizarVisibilidadBotonPedido(mesaCard);

        // Enviar el formulario para guardar el cambio en el backend
        formulario.submit();
    }
});


// ===== GESTIÓN DEL MODAL DE PEDIDO =====

async function gestionarPedido(mesaId) {
  mesaActualId = mesaId;
  try {
    const data = await apiFetch(`/api/mesas/${mesaId}/pedido/`);
    document.getElementById("mesaNombre").textContent = data.mesa.nombre;
    pedidoActual = data.pedido;
    listaCompletaProductos = data.productos;
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
  lista.innerHTML = listaCompletaProductos.map(p => `
    <div class="producto-item" data-producto-id="${p.id_producto}" onclick="agregarOActualizarItem(${p.id_producto})">
      <div class="producto-row">
        <div class="producto-main">
          ${p.imagen ? `<img src="${p.imagen}" alt="${p.nombre}" class="producto-thumb">` : `<div class="thumb-placeholder">Sin img</div>`}
          <div>
            <strong>${p.nombre}</strong>
            <small class="text-muted">Stock: ${p.stock}</small>
          </div>
        </div>
        <span class="precio">$${p.precio_venta}</span>
      </div>
    </div>
  `).join("");
}

function actualizarPedidoItemsUI() {
  const itemsContainer = document.getElementById("pedidoItems");
  if (pedidoActual && pedidoActual.items && pedidoActual.items.length > 0) {
    itemsContainer.innerHTML = pedidoActual.items.map(item => {
      const producto = listaCompletaProductos.find(p => p.id_producto === item.producto.id);
      const stock = producto ? producto.stock : 0;
      const atascadoEnStock = item.cantidad >= stock;
      return `
        <div class="pedido-item">
          <div class="pedido-info">
            <strong>${item.producto.nombre}</strong>
          </div>
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
  const itemExistente = pedidoActual.items.find(i => i.producto.id === productoId);
  if (itemExistente) {
    await cambiarCantidadItem(itemExistente.id, itemExistente.cantidad + 1);
  } else {
    const producto = listaCompletaProductos.find(p => p.id_producto === productoId);
    if (producto.stock < 1) {
      showToast("No hay stock disponible para este producto.");
      return;
    }
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
  if (nuevaCantidad < 1) {
    await eliminarItem(itemId);
    return;
  }

  const item = pedidoActual.items.find(i => i.id === itemId);
  const producto = listaCompletaProductos.find(p => p.id_producto === item.producto.id);
  if (producto.stock < nuevaCantidad) {
    showToast(`Stock insuficiente. Disponible: ${producto.stock}`);
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
    showToast("No hay items en el pedido para facturar.");
    return;
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

// ===== BÚSQUEDA Y CIERRE DE MODALES =====

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