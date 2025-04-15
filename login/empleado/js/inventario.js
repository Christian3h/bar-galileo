import { verificarSesion } from "./validarSesion.js";
verificarSesion();

import { formatoCOP } from "./formatoMoneda.js";
const inputBuscarCliente = document.getElementById("buscarVenta");

mostrarClientesTabla(); 

// Evento para la búsqueda en tiempo real
inputBuscarCliente.addEventListener("input", function () {
    const filtro = inputBuscarCliente.value.trim().toLowerCase();
    mostrarClientesTabla(filtro);
});

// Función para mostrar productos en la tabla (con filtro opcional)
function mostrarClientesTabla(filtro = "") {
    const productos = JSON.parse(localStorage.getItem("productos")) || [];
    const tablaProductos = document.getElementById("lista-productos"); // Corregido el ID
    tablaProductos.innerHTML = ""; 

    // Filtrar productos por nombre o ID
    const productosFiltrados = productos.filter(producto => 
        producto.nombre?.toLowerCase().includes(filtro) || 
        producto.id?.includes(filtro)
    );

    productosFiltrados.forEach(producto => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${producto.nombre || "Sin nombre"}</td>
            <td>${producto.id || "Sin ID"}</td>
            <td>${formatoCOP.format(producto.precio) || "Sin precio"}</td>
            <td>${producto.categoria || "Sin categoría"}</td>
        `;
        tablaProductos.appendChild(row); // Corregido el nombre de la variable
    });
}
