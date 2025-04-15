import  {formatoCOP}  from "./formatoMoneda.js";

import { verificarSesion } from "./validarSesion.js";
verificarSesion();

document.addEventListener("DOMContentLoaded", function () {
    const tablaFacturacion = document.getElementById("lista-facturacion");
    const inputBuscarCliente = document.getElementById("buscarCliente");

    if (!tablaFacturacion || !inputBuscarCliente) {
        console.error("Error: No se encontró la tabla o el input de búsqueda.");
        return;
    }

    // Cargar las mesas ocupadas al iniciar
    mostrarFacturacion();

    // Evento de búsqueda en tiempo real
    inputBuscarCliente.addEventListener("input", function () {
        mostrarFacturacion(inputBuscarCliente.value.trim().toLowerCase());
    });
});

// Función para mostrar la facturación por mesa
function mostrarFacturacion(filtro = "") {
    const tablaFacturacion = document.getElementById("lista-facturacion"); // Asegurar que el elemento existe
    if (!tablaFacturacion) return;

    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    const ventas = JSON.parse(localStorage.getItem("ventas")) || [];

    tablaFacturacion.innerHTML = ""; // Limpiar tabla

    // Agrupar ventas por mesa
    const mesasOcupadas = clientes
        .filter(cliente => cliente.NMesa) // Solo clientes con mesa asignada
        .map(cliente => {
            const ventasMesa = ventas.filter(venta => venta.clienteNombre === cliente.nombre);
            const total = ventasMesa.reduce((sum, venta) => sum + obtenerPrecio(venta.productoNombre) * venta.cantidad, 0);
            return { ...cliente, total };
        })
        .filter(cliente => cliente.total > 0) // Mostrar solo mesas con ventas
        .filter(cliente => cliente.nombre.toLowerCase().includes(filtro) || cliente.NMesa.includes(filtro)); // Aplicar filtro

    mesasOcupadas.forEach(mesa => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${mesa.nombre}</td>
            <td>${mesa.telefono}</td>
            <td>${mesa.fecha}</td>
            <td>${mesa.NMesa}</td>
            <td>${formatoCOP.format(mesa.total)}</td>
            <td>
                <button class="btn-facturar" onclick="generarFactura('${mesa.NMesa}')">🧾 Facturar</button>
            </td>
        `;
        tablaFacturacion.appendChild(row);
    });
}

// Función para obtener el precio del producto
function obtenerPrecio(nombreProducto) {
    const productos = JSON.parse(localStorage.getItem("productos")) || [];
    const producto = productos.find(p => p.nombre === nombreProducto);
    return producto ? producto.precio : 0;
}

// Función para generar factura y eliminar datos de la mesa
window.generarFactura = function (NMesa) {
    const clientes = JSON.parse(localStorage.getItem("clientes")) || [];
    const ventas = JSON.parse(localStorage.getItem("ventas")) || [];

    // Obtener datos del cliente y sus ventas
    const cliente = clientes.find(c => c.NMesa === NMesa);
    const ventasMesa = ventas.filter(v => v.clienteNombre === cliente?.nombre);

    if (!cliente || ventasMesa.length === 0) {
        alert("No hay ventas registradas para esta mesa.");
        return;
    }

    // Calcular total de la factura
    const total = ventasMesa.reduce((sum, venta) => sum + obtenerPrecio(venta.productoNombre) * venta.cantidad, 0);

    // Obtener la fecha actual (YYYY-MM-DD)
    const fechaHoy = new Date().toISOString().split("T")[0];

    // Obtener facturas guardadas o inicializar
    let facturasGuardadas = JSON.parse(localStorage.getItem("facturas")) || {};

    // Si no hay facturas para la fecha actual, crear un array vacío
    if (!facturasGuardadas[fechaHoy]) {
        facturasGuardadas[fechaHoy] = [];
    }

    // Agregar la nueva factura
    const nuevaFactura = {
        id: Date.now(), // ID único basado en la marca de tiempo
        cliente: cliente.nombre,
        mesa: NMesa,
        fecha: fechaHoy,
        ventas: ventasMesa,
        total
    };

    facturasGuardadas[fechaHoy].push(nuevaFactura);

    // Guardar en localStorage
    localStorage.setItem("facturas", JSON.stringify(facturasGuardadas));

    // Eliminar ventas y cliente de la mesa
    const nuevasVentas = ventas.filter(v => v.clienteNombre !== cliente.nombre);
    const nuevosClientes = clientes.filter(c => c.NMesa !== NMesa);

    localStorage.setItem("ventas", JSON.stringify(nuevasVentas));
    localStorage.setItem("clientes", JSON.stringify(nuevosClientes));

    // Redirigir a la página de facturación
    window.location.href = "factura.html";
};
