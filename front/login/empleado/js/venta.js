import { verificarSesion } from "./validarSesion.js";
verificarSesion();

const formulario = document.querySelector("form");
const selectCliente = document.getElementById("cliente");
const selectProducto = document.getElementById("producto");
const inputCantidad = document.getElementById("cantidad");
const tablaVentas = document.getElementById("lista-ventas");
const inputBuscarVenta = document.getElementById("buscarVenta");
const btnLimpiar = document.getElementById("btn-limpiar");

import  {formatoCOP}  from "./formatoMoneda.js";


let ventaEditando = null; // Variable para editar ventas

// Cargar clientes y productos al iniciar
document.addEventListener("DOMContentLoaded", () => {
    cargarClientes();
    cargarProductos();
    mostrarVentas();
});

// Función para cargar clientes en el select
function cargarClientes() {
    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    selectCliente.innerHTML = clientes.map(cliente => 
        `<option value="${cliente.id}">${cliente.nombre}</option>`
    ).join("");
}

// Función para cargar productos en el select
function cargarProductos() {
    const productos = JSON.parse(localStorage.getItem("productos")) || [];
    selectProducto.innerHTML = productos.map(producto => 
        `<option value="${producto.id}">${producto.nombre} - $${producto.precio}</option>`
    ).join("");
}

// Evento para guardar o editar una venta
formulario.addEventListener("submit", function (event) {
    event.preventDefault();
    
    const clienteID = selectCliente.value;
    const productoID = selectProducto.value;
    const cantidad = parseInt(inputCantidad.value);

    if (!clienteID || !productoID || cantidad <= 0) {
        alert("Selecciona un cliente, un producto y una cantidad válida.");
        return;
    }

    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    const productos = JSON.parse(localStorage.getItem("productos")) || [];

    const cliente = clientes.find(c => c.id === clienteID);
    const producto = productos.find(p => p.id === productoID);

    if (!cliente || !producto) {
        alert("Error al encontrar cliente o producto.");
        return;
    }

    const nuevaVenta = {
        id: ventaEditando ? ventaEditando.id : crypto.randomUUID(),
        clienteNombre: cliente.nombre,
        productoNombre: producto.nombre,
        productoPrecio: producto.precio,
        cantidad,
    };

    let ventas = JSON.parse(localStorage.getItem("ventas")) || [];

    if (ventaEditando) {
        ventas = ventas.map(v => v.id === ventaEditando.id ? nuevaVenta : v);
        ventaEditando = null;
    } else {
        ventas.push(nuevaVenta);
    }

    localStorage.setItem("ventas", JSON.stringify(ventas));
    formulario.reset();
    mostrarVentas();
});

// Función para mostrar ventas en la tabla con filtro opcional
function mostrarVentas(filtro = "") {
    const ventas = JSON.parse(localStorage.getItem("ventas")) || [];
    tablaVentas.innerHTML = ""; 
    const ventasFiltradas = ventas.filter(venta => 
        venta.clienteNombre.toLowerCase().includes(filtro) || 
        venta.productoNombre.toLowerCase().includes(filtro)
    );
    
    ventasFiltradas.forEach(venta => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${venta.clienteNombre}</td>
            <td>${venta.productoNombre}</td>
            <td>${formatoCOP.format(parseInt(venta.productoPrecio) * parseInt(venta.cantidad))}</td>
            <td>${venta.cantidad}</td>
            <td>
                <button class="btn-editar" onclick="editarVenta('${venta.id}')">✏️</button>
                <button class="btn-eliminar" onclick="eliminarVenta('${venta.id}')">❌</button>
            </td>
        `;
        tablaVentas.appendChild(row);
    });
}

// Evento de búsqueda en tiempo real
inputBuscarVenta.addEventListener("input", function () {
    mostrarVentas(inputBuscarVenta.value.trim().toLowerCase());
});

// Función para eliminar una venta
window.eliminarVenta = function (id) {
    let ventas = JSON.parse(localStorage.getItem("ventas")) || [];
    ventas = ventas.filter(venta => venta.id !== id);
    localStorage.setItem("ventas", JSON.stringify(ventas));
    mostrarVentas();
};

// Función para editar una venta
window.editarVenta = function (id) {
    const ventas = JSON.parse(localStorage.getItem("ventas")) || [];
    ventaEditando = ventas.find(venta => venta.id === id);

    if (ventaEditando) {
        selectCliente.value = (JSON.parse(localStorage.getItem("clientes")) || []).find(c => c.nombre === ventaEditando.clienteNombre)?.id || "";
        selectProducto.value = (JSON.parse(localStorage.getItem("productos")) || []).find(p => p.nombre === ventaEditando.productoNombre)?.id || "";
        inputCantidad.value = ventaEditando.cantidad;
    }
};

// Evento para limpiar la lista de ventas
btnLimpiar.addEventListener("click", function () {
    localStorage.removeItem("ventas");
    mostrarVentas();
});
