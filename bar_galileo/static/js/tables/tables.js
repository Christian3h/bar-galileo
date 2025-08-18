/* ===== MODO EDICIÓN ===== */
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

/* ===== VISIBILIDAD BOTONES PEDIDO ===== */
function actualizarVisibilidadBotonesPedido() {
  const mesasCards = document.querySelectorAll('.mesa-card');

  mesasCards.forEach(card => {
    const botonPedido = card.querySelector('button[onclick*="gestionarPedido"]');
    if (botonPedido) {
      if (card.classList.contains('ocupada')) {
        botonPedido.style.display = 'inline-block';
      } else {
        botonPedido.style.display = 'none';
      }
    }
  });
}

/* ===== API: MESA TIENE PEDIDOS ===== */
async function mesaTienePedidos(mesaId) {
  try {
    const response = await fetch(`/api/mesas/${mesaId}/pedido/`);
    const data = await response.json();
    return data.pedido && data.pedido.items && data.pedido.items.length > 0;
  } catch (error) {
    console.error('Error al verificar pedidos:', error);
    return false;
  }
}

/* ===== INICIALIZACIÓN ===== */
document.addEventListener('DOMContentLoaded', function() {
  actualizarVisibilidadBotonesPedido();
  const selects = document.querySelectorAll('select[name="estado"]');
  selects.forEach(select => {
    select.dataset.estadoAnterior = select.value;
  });
});

/* ===== CAMBIO DE ESTADO MESA (con validación) ===== */
document.addEventListener('change', async function(event) {
  if (event.target.name === 'estado') {
    const mesaCard = event.target.closest('.mesa-card');
    const formulario = event.target.closest('form');
    const estadoSeleccionado = event.target.value;
    const estadoAnterior = event.target.dataset.estadoAnterior || 'disponible';

    // ID de mesa desde la URL del form
    const actionUrl = formulario.action;
    const mesaId = actionUrl.split('/').slice(-2, -1)[0];

    // Validación por pedidos activos
    const tienePedidos = await mesaTienePedidos(mesaId);

    if (tienePedidos) {
      if (estadoSeleccionado !== 'ocupada') {
        let mensaje = '';
        switch(estadoSeleccionado) {
          case 'disponible':
            mensaje = 'No se puede cambiar la mesa a disponible mientras tenga pedidos activos. Complete o cancele el pedido primero.';
            break;
          case 'reservada':
            mensaje = 'No se puede reservar una mesa que tiene pedidos activos. Complete el pedido primero.';
            break;
          case 'fuera de servicio':
            mensaje = 'No se puede poner fuera de servicio una mesa con pedidos activos. Complete el pedido primero.';
            break;
        }
        alert(mensaje);
        event.target.value = estadoAnterior; // revertir
        return;
      }
    }

    // Guardar estado actual
    event.target.dataset.estadoAnterior = estadoSeleccionado;

    // Actualizar clases CSS
    mesaCard.classList.remove('disponible', 'ocupada', 'reservada', 'fuera-de-servicio');
    const claseEstado = estadoSeleccionado.replace(/\s+/g, '-').toLowerCase();
    mesaCard.classList.add(claseEstado);

    // Mostrar u ocultar botón "gestionar pedido"
    const botonPedido = mesaCard.querySelector('button[onclick*="gestionarPedido"]');
    if (botonPedido) {
      botonPedido.style.display = (estadoSeleccionado === 'ocupada') ? 'inline-block' : 'none';
    }

    if (formulario) formulario.submit();
  }
});

/* ===== VARIABLES GLOBALES ===== */
let mesaActual = null;
let pedidoActual = null;
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")
  ? document.querySelector("[name=csrfmiddlewaretoken]").value
  : "";

/* ===== GESTIONAR PEDIDO (abrir modal principal) ===== */
function gestionarPedido(mesaId) {
  mesaActual = mesaId;
  fetch(`/api/mesas/${mesaId}/pedido/`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("mesaNombre").textContent = data.mesa.nombre;
      pedidoActual = data.pedido;
      actualizarListaProductos(data.productos);
      actualizarPedidoItems();
      document.getElementById("pedidoModal").style.display = "block";
    });
}

/* ===== LISTA DE PRODUCTOS (HTML con clases) ===== */
function actualizarListaProductos(productos) {
  const lista = document.getElementById("productosLista");
  lista.innerHTML = productos
    .map((producto) => `
      <div class="producto-item" onclick="mostrarControlCantidad(${producto.id_producto}, '${producto.nombre}', ${producto.precio_venta})">
        <div class="producto-row">
          <div class="producto-main">
            ${
              producto.imagen
                ? `<img src="${producto.imagen}" alt="${producto.nombre}" class="producto-thumb">`
                : `<div class="thumb-placeholder">Sin img</div>`
            }
            <strong>${producto.nombre}</strong>
          </div>
          <span class="precio">$${producto.precio_venta}</span>
        </div>
      </div>
    `)
    .join("");
}

/* ===== MODAL CANTIDAD (HTML con clases, sin estilos inline) ===== */
function mostrarControlCantidad(productoId, nombre, precio) {
  // Si ya existe, lo removemos para evitar duplicados
  cerrarModalCantidad();

  const modalCantidad = document.createElement('div');
  modalCantidad.id = 'modalCantidad';
  modalCantidad.className = 'modal-overlay';

  modalCantidad.innerHTML = `
    <div class="modal-box">
      <h4 class="modal-title">Agregar ${nombre}</h4>
      <p class="modal-price">Precio: $${precio}</p>

      <div class="modal-counter">
        <button type="button" onclick="cambiarCantidad(-1)" class="btn-cantidad btn-cantidad--lg">-</button>
        <input type="number" id="cantidadInput" value="1" min="1" max="99" class="input-cantidad" />
        <button type="button" onclick="cambiarCantidad(1)" class="btn-cantidad btn-cantidad--lg">+</button>
      </div>

      <div class="modal-actions">
        <button onclick="cerrarModalCantidad()" class="btn btn-danger btn-sm">Cancelar</button>
        <button onclick="confirmarAgregarProducto(${productoId}, '${nombre}', ${precio})" class="btn btn-success btn-sm">Agregar</button>
      </div>
    </div>
  `;

  document.body.appendChild(modalCantidad);

  const input = document.getElementById('cantidadInput');
  input.focus();
  input.select();
}

function cambiarCantidad(delta) {
  const input = document.getElementById('cantidadInput');
  if (!input) return;
  let cantidad = parseInt(input.value || '1', 10) + delta;
  if (isNaN(cantidad)) cantidad = 1;
  if (cantidad < 1) cantidad = 1;
  if (cantidad > 99) cantidad = 99;
  input.value = cantidad;
}

function cerrarModalCantidad() {
  const modal = document.getElementById('modalCantidad');
  if (modal) modal.remove();
}

function confirmarAgregarProducto(productoId, nombre, precio) {
  const cantidad = parseInt(document.getElementById('cantidadInput').value, 10);

  const data = {
    mesa_id: mesaActual,
    producto_id: productoId,
    cantidad: cantidad,
  };

  fetch("/api/pedidos/agregar-item/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      pedidoActual = data.pedido;
      actualizarPedidoItems();
      cerrarModalCantidad();
    })
    .catch((error) => {
      console.error('Error al agregar producto:', error);
      alert('Error al agregar el producto');
    });
}

/* ===== RENDER DE ITEMS DEL PEDIDO (HTML con clases) ===== */
function actualizarPedidoItems() {
  const itemsContainer = document.getElementById("pedidoItems");

  if (pedidoActual && pedidoActual.items) {
    itemsContainer.innerHTML = pedidoActual.items
      .map((item) => `
        <div class="pedido-item">
          <div class="pedido-info">
            <strong>${item.producto.nombre}</strong>
          </div>
          <div class="pedido-controles">
            <div class="cantidad">
              <button onclick="cambiarCantidadItem(${item.id}, ${item.cantidad - 1})" class="btn-cantidad" ${item.cantidad <= 1 ? 'disabled' : ''}>-</button>
              <span class="cantidad-valor">${item.cantidad}</span>
              <button onclick="cambiarCantidadItem(${item.id}, ${item.cantidad + 1})" class="btn-cantidad">+</button>
            </div>
            <span class="subtotal">$${item.subtotal}</span>
            <button class="btn btn-sm btn-danger btn-eliminar" onclick="eliminarItem(${item.id})">×</button>
          </div>
        </div>
      `)
      .join("");

    document.getElementById("pedidoTotal").textContent =
      Number(pedidoActual.total || 0).toFixed(2);
  } else {
    itemsContainer.innerHTML =
      '<p class="pedido-vacio">No hay items en el pedido</p>';
    document.getElementById("pedidoTotal").textContent = "0.00";
  }
}

/* ===== ACTUALIZAR / ELIMINAR ITEM ===== */
function cambiarCantidadItem(itemId, nuevaCantidad) {
  if (nuevaCantidad < 1) {
    eliminarItem(itemId);
    return;
  }

  fetch(`/api/pedidos/actualizar-item/${itemId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ cantidad: nuevaCantidad }),
  })
    .then((response) => response.json())
    .then((data) => {
      pedidoActual = data.pedido;
      actualizarPedidoItems();
    })
    .catch((error) => {
      console.error('Error al actualizar cantidad:', error);
      alert('Error al actualizar la cantidad');
    });
}

function eliminarItem(itemId) {
  if (confirm('¿Estás seguro de que deseas eliminar este item del pedido?')) {
    fetch(`/api/pedidos/eliminar-item/${itemId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
    })
      .then((response) => response.json())
      .then((data) => {
        pedidoActual = data.pedido;
        actualizarPedidoItems();
      })
      .catch((error) => {
        console.error('Error al eliminar item:', error);
        alert('Error al eliminar el item');
      });
  }
}

/* ===== FACTURAR ===== */
function facturarPedido() {
  if (!pedidoActual || !pedidoActual.items || !pedidoActual.items.length) {
    alert("No hay items en el pedido");
    return;
  }

  const validarStock = async () => {
    return true;
    // Aquí tu validación real si la activas
  };

  const procederFacturacion = async () => {
    const stockValido = await validarStock();
    if (!stockValido) return;

    if (confirm("¿Estás seguro de que deseas facturar este pedido? Esta acción actualizará el inventario.")) {
      try {
        const response = await fetch(`/api/pedidos/${pedidoActual.id}/facturar/`, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
        });

        const data = await response.json();

        if (data.error) {
          alert(`Error al facturar: ${data.error}`);
          return;
        }

        if (data.success) {
          alert('Pedido facturado exitosamente');
          cerrarModal();

          const mesaCard = document.querySelector(`.mesa-card`);
          if (mesaCard) {
            const selectEstado = mesaCard.querySelector('select[name="estado"]');
            if (selectEstado) {
              selectEstado.value = 'disponible';
              selectEstado.dataset.estadoAnterior = 'disponible';
            }
          }
          window.location.reload();
        }
      } catch (error) {
        console.error('Error al facturar:', error);
        alert('Error al procesar la factura. Intente nuevamente.');
      }
    }
  };

  procederFacturacion();
}

/* ===== CIERRE MODALES ===== */
function cerrarModal() {
  document.getElementById("pedidoModal").style.display = "none";
  cerrarModalCantidad();
}

window.onclick = function (event) {
  const modal = document.getElementById("pedidoModal");
  const modalCantidad = document.getElementById("modalCantidad");
  if (event.target === modal) modal.style.display = "none";
  if (event.target === modalCantidad) cerrarModalCantidad();
};

/* ===== BÚSQUEDA ===== */
document.getElementById("buscarProducto")
  .addEventListener("input", function (e) {
    const busqueda = e.target.value.toLowerCase();
    const productos = document.querySelectorAll(".producto-item");
    productos.forEach((producto) => {
      const nombre = producto.querySelector("strong").textContent.toLowerCase();
      producto.style.display = nombre.includes(busqueda) ? "block" : "none";
    });
  });

/* ===== ATAJOS TECLADO EN MODAL CANTIDAD ===== */
document.addEventListener('keydown', function(e) {
  const modalCantidad = document.getElementById('modalCantidad');
  if (modalCantidad) {
    if (e.key === 'Escape') {
      cerrarModalCantidad();
    } else if (e.key === 'Enter') {
      const btnAgregar = modalCantidad.querySelector('button[onclick*="confirmarAgregarProducto"]');
      if (btnAgregar) btnAgregar.click();
    }
  }
});
