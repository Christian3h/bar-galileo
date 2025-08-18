/**
 * Lógica para la gestión de mesas y pedidos en el Bar Galileo.
 * Incluye edición de mesas, gestión de modales para pedidos, y comunicación con la API.
 */

// ===== VARIABLES GLOBALES =====
let mesaActualId = null;
let pedidoActual = {};
let listaCompletaProductos = []; // Almacena la lista de productos con todos sus datos (incluido stock)
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

// ===== MANEJO DE ERRORES Y PETICIONES API =====

/**
 * Realiza una petición fetch y maneja la respuesta, extrayendo errores de la API.
 * @param {string} url - La URL para la petición.
 * @param {object} options - Opciones para la petición fetch.
 * @returns {Promise<object>} - La respuesta JSON de la API.
 * @throws {Error} - Lanza un error con el mensaje de la API si la respuesta no es ok.
 */
async function apiFetch(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `Error del servidor: ${response.status}` }));
    throw new Error(errorData.error || 'Ocurrió un error inesperado.');
  }
  return response.json();
}

// ===== GESTIÓN DEL MODAL DE PEDIDO =====

/**
 * Abre el modal de gestión de pedidos para una mesa específica.
 * @param {number} mesaId - El ID de la mesa.
 */
async function gestionarPedido(mesaId) {
  mesaActualId = mesaId;
  try {
    const data = await apiFetch(`/api/mesas/${mesaId}/pedido/`);
    document.getElementById("mesaNombre").textContent = data.mesa.nombre;
    pedidoActual = data.pedido;
    listaCompletaProductos = data.productos; // Guardar lista de productos
    actualizarListaProductosUI();
    actualizarPedidoItemsUI();
    document.getElementById("pedidoModal").style.display = "block";
  } catch (error) {
    console.error("Error al obtener datos del pedido:", error);
    alert(error.message);
  }
}

/**
 * Actualiza la UI con la lista de productos disponibles.
 */
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

/**
 * Actualiza la UI con los items del pedido actual.
 */
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

/**
 * Agrega un nuevo producto o incrementa la cantidad de uno existente.
 * @param {number} productoId - El ID del producto a agregar.
 */
async function agregarOActualizarItem(productoId) {
  const itemExistente = pedidoActual.items.find(i => i.producto.id === productoId);
  if (itemExistente) {
    await cambiarCantidadItem(itemExistente.id, itemExistente.cantidad + 1);
  } else {
    const producto = listaCompletaProductos.find(p => p.id_producto === productoId);
    if (producto.stock < 1) {
      alert("No hay stock disponible para este producto.");
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
      alert(error.message);
    }
  }
}

/**
 * Cambia la cantidad de un item existente en el pedido.
 * @param {number} itemId - El ID del item del pedido.
 * @param {number} nuevaCantidad - La nueva cantidad para el item.
 */
async function cambiarCantidadItem(itemId, nuevaCantidad) {
  if (nuevaCantidad < 1) {
    await eliminarItem(itemId);
    return;
  }

  const item = pedidoActual.items.find(i => i.id === itemId);
  const producto = listaCompletaProductos.find(p => p.id_producto === item.producto.id);
  if (producto.stock < nuevaCantidad) {
    alert(`Stock insuficiente. Disponible: ${producto.stock}`);
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
    alert(error.message);
  }
}

/**
 * Elimina un item del pedido.
 * @param {number} itemId - El ID del item a eliminar.
 */
async function eliminarItem(itemId) {
  try {
    const data = await apiFetch(`/api/pedidos/eliminar-item/${itemId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
    });
    pedidoActual = data.pedido;
    actualizarPedidoItemsUI();
  } catch (error) {
    console.error('Error al eliminar item:', error);
    alert(error.message);
  }
}

// ===== FACTURACIÓN =====

async function facturarPedido() {
  if (!pedidoActual || !pedidoActual.items || !pedidoActual.items.length) {
    alert("No hay items en el pedido para facturar.");
    return;
  }

  if (confirm("¿Estás seguro de que deseas facturar este pedido? Esta acción actualizará el inventario.")) {
    try {
      const data = await apiFetch(`/api/pedidos/${pedidoActual.id}/facturar/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
      });
      if (data.success) {
        alert('Pedido facturado exitosamente');
        window.location.reload();
      }
    } catch (error) {
      console.error('Error al facturar:', error);
      alert(error.message);
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

// ===== LÓGICA DE EDICIÓN DE MESA (sin cambios) =====

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