import { verificarSesion } from "./validarSesion.js";
verificarSesion();

import { formatoCOP } from "./formatoMoneda.js";

document.addEventListener("DOMContentLoaded", function () {
    const facturas = JSON.parse(localStorage.getItem("facturas")) || {};
    const fechaHoy = new Date().toISOString().split("T")[0]; // Obtener la fecha actual en formato YYYY-MM-DD

    if (!facturas[fechaHoy] || facturas[fechaHoy].length === 0) {
        document.getElementById("detalle-factura").innerHTML = "<p>No hay factura disponible.</p>";
        return;
    }

    // Obtener la última factura generada del día
    const factura = facturas[fechaHoy][facturas[fechaHoy].length - 1];

    if (!factura) {
        document.getElementById("detalle-factura").innerHTML = "<p>No hay factura disponible.</p>";
        return;
    }

    let facturaHTML = `
        <p><strong>Cliente:</strong> ${factura.cliente}</p>
        <p><strong>Fecha:</strong> ${factura.fecha}</p>
        <p><strong>Número de Mesa:</strong> ${factura.mesa}</p>
        <hr>
        <h3>Detalle de Venta</h3>
        <table>
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
    `;

    factura.ventas.forEach(venta => {
        const precioUnitario = obtenerPrecio(venta.productoNombre);
        const totalProducto = precioUnitario * venta.cantidad;
        facturaHTML += `
            <tr>
                <td>${venta.productoNombre}</td>
                <td>${venta.cantidad}</td>
                <td style="padding: 30px;">${formatoCOP.format(precioUnitario)}</td>
                <td>${formatoCOP.format(totalProducto)}</td>
            </tr>
        `;
    });

    facturaHTML += `
            </tbody>
        </table>
        <h2>Total a Pagar: ${formatoCOP.format(factura.total)}</h2>
        <button onclick="window.print()" style="margin-top: 30px;">🖨️ Imprimir</button>
    `;

    document.getElementById("detalle-factura").innerHTML = facturaHTML;
});

// Función para obtener el precio del producto
function obtenerPrecio(nombreProducto) {
    const productos = JSON.parse(localStorage.getItem("productos")) || [];
    const producto = productos.find(p => p.nombre === nombreProducto);
    return producto ? producto.precio : 0;
}
