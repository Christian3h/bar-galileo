document.addEventListener('DOMContentLoaded', function() {
    inicializarReportes();
});

function inicializarReportes() {
    cargarDatosResumen();
    inicializarGraficos();
    cargarTransacciones();
    configurarEventListeners();
}

function configurarEventListeners() {
    document.getElementById('periodoSelect').addEventListener('change', actualizarDatos);
    document.getElementById('aplicarFiltro').addEventListener('click', actualizarDatos);
    document.getElementById('exportarPDF').addEventListener('click', exportarReporte);
}

function cargarDatosResumen() {
    // Simulación de datos
    const datos = {
        ingresos: obtenerIngresos(),
        gastos: obtenerGastos(),
        productos: obtenerProductosVendidos()
    };

    actualizarTarjetasResumen(datos);
}

function actualizarTarjetasResumen(datos) {
    document.getElementById('totalIngresos').textContent = formatearMoneda(datos.ingresos);
    document.getElementById('totalGastos').textContent = formatearMoneda(datos.gastos);
    document.getElementById('balance').textContent = formatearMoneda(datos.ingresos - datos.gastos);
    document.getElementById('productosVendidos').textContent = datos.productos;
}

function inicializarGraficos() {
    // Gráfico de Ingresos vs Gastos
    new Chart(document.getElementById('ingresosGastosChart'), {
        type: 'bar',
        data: obtenerDatosIngresosGastos(),
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Gráfico de Productos
    new Chart(document.getElementById('productosChart'), {
        type: 'doughnut',
        data: obtenerDatosProductos(),
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // Gráfico de Distribución de Gastos
    new Chart(document.getElementById('gastosChart'), {
        type: 'pie',
        data: obtenerDatosGastos(),
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // Gráfico de Tendencia de Ventas
    new Chart(document.getElementById('ventasChart'), {
        type: 'line',
        data: obtenerDatosTendencia(),
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function obtenerIngresos() {
    const facturasObj = JSON.parse(localStorage.getItem('facturas')) || {};
    let totalIngresos = 0;

    Object.values(facturasObj).forEach(facturasDelDia => {
        facturasDelDia.forEach(factura => {
            totalIngresos += factura.total;
        });
    });

    return totalIngresos;
}

function obtenerGastos() {
    // Obtener datos de gastos del localStorage
    const gastos = JSON.parse(localStorage.getItem('gastos')) || [];
    return gastos.reduce((total, gasto) => total + gasto.monto, 0);
}

function obtenerProductosVendidos() {
    const facturasObj = JSON.parse(localStorage.getItem('facturas')) || {};
    const productosVendidos = {};

    // Recorrer todas las facturas de todos los días
    Object.values(facturasObj).forEach(facturasDelDia => {
        facturasDelDia.forEach(factura => {
            factura.ventas.forEach(venta => {
                const nombreProducto = venta.productoNombre;
                if (productosVendidos[nombreProducto]) {
                    productosVendidos[nombreProducto] += venta.cantidad;
                } else {
                    productosVendidos[nombreProducto] = venta.cantidad;
                }
            });
        });
    });

    return Object.values(productosVendidos).reduce((a, b) => a + b, 0);
}

// Función para obtener datos de ingresos vs gastos por mes
function obtenerDatosIngresosGastos() {
    const meses = obtenerUltimos6Meses();
    const ingresos = [];
    const gastos = [];

    meses.forEach(mes => {
        const ingresosDelMes = obtenerIngresosDelMes(mes);
        const gastosDelMes = obtenerGastosDelMes(mes);
        ingresos.push(ingresosDelMes);
        gastos.push(gastosDelMes);
    });

    return {
        labels: meses.map(mes => mes.toLocaleString('es-ES', { month: 'short' })),
        datasets: [
            {
                label: 'Ingresos',
                data: ingresos,
                backgroundColor: 'rgba(46, 204, 113, 0.5)',
                borderColor: 'rgb(46, 204, 113)',
                borderWidth: 1
            },
            {
                label: 'Gastos',
                data: gastos,
                backgroundColor: 'rgba(231, 76, 60, 0.5)',
                borderColor: 'rgb(231, 76, 60)',
                borderWidth: 1
            }
        ]
    };
}

// Función para obtener datos de productos más vendidos
function obtenerDatosProductos() {
    const facturasObj = JSON.parse(localStorage.getItem('facturas')) || {};
    const productosVendidos = {};

    // Recorrer todas las facturas de todos los días
    Object.values(facturasObj).forEach(facturasDelDia => {
        facturasDelDia.forEach(factura => {
            factura.ventas.forEach(venta => {
                const nombreProducto = venta.productoNombre;
                if (productosVendidos[nombreProducto]) {
                    productosVendidos[nombreProducto] += venta.cantidad;
                } else {
                    productosVendidos[nombreProducto] = venta.cantidad;
                }
            });
        });
    });

    // Ordenar y obtener top 5
    const top5Productos = Object.entries(productosVendidos)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5);

    return {
        labels: top5Productos.map(([producto]) => producto),
        datasets: [{
            data: top5Productos.map(([,cantidad]) => cantidad),
            backgroundColor: [
                '#2ecc71', '#3498db', '#f1c40f', '#e74c3c', '#9b59b6'
            ]
        }]
    };
}

// Función para obtener distribución de gastos
function obtenerDatosGastos() {
    const gastos = JSON.parse(localStorage.getItem('gastos')) || [];
    const gastosPorTipo = {};

    // Agrupar gastos por tipo
    gastos.forEach(gasto => {
        if (gastosPorTipo[gasto.tipo]) {
            gastosPorTipo[gasto.tipo] += gasto.monto;
        } else {
            gastosPorTipo[gasto.tipo] = gasto.monto;
        }
    });

    return {
        labels: Object.keys(gastosPorTipo),
        datasets: [{
            data: Object.values(gastosPorTipo),
            backgroundColor: [
                '#2ecc71', '#3498db', '#f1c40f', '#e74c3c', '#9b59b6'
            ]
        }]
    };
}

// Función para obtener tendencia de ventas
function obtenerDatosTendencia() {
    const facturasObj = JSON.parse(localStorage.getItem('facturas')) || {};
    const ventasPorDia = {};
    const ultimosDias = obtenerUltimos30Dias();

    // Inicializar todos los días con 0
    ultimosDias.forEach(dia => {
        ventasPorDia[dia.toISOString().split('T')[0]] = 0;
    });

    // Sumar ventas por día
    Object.entries(facturasObj).forEach(([fecha, facturas]) => {
        if (ventasPorDia.hasOwnProperty(fecha)) {
            ventasPorDia[fecha] = facturas.reduce((total, factura) => total + factura.total, 0);
        }
    });

    return {
        labels: Object.keys(ventasPorDia),
        datasets: [{
            label: 'Ventas diarias',
            data: Object.values(ventasPorDia),
            fill: false,
            borderColor: '#2ecc71',
            tension: 0.1
        }]
    };
}

// Funciones auxiliares
function obtenerUltimos6Meses() {
    const meses = [];
    const fecha = new Date();
    for (let i = 5; i >= 0; i--) {
        const mesAnterior = new Date(fecha.getFullYear(), fecha.getMonth() - i, 1);
        meses.push(mesAnterior);
    }
    return meses;
}

function obtenerUltimos30Dias() {
    const dias = [];
    const fecha = new Date();
    for (let i = 29; i >= 0; i--) {
        const dia = new Date(fecha);
        dia.setDate(fecha.getDate() - i);
        dias.push(dia);
    }
    return dias;
}

function obtenerIngresosDelMes(fecha) {
    const facturasObj = JSON.parse(localStorage.getItem('facturas')) || {};
    let totalMes = 0;

    Object.entries(facturasObj).forEach(([fechaStr, facturas]) => {
        const fechaFactura = new Date(fechaStr);
        if (fechaFactura.getMonth() === fecha.getMonth() && 
            fechaFactura.getFullYear() === fecha.getFullYear()) {
            facturas.forEach(factura => {
                totalMes += factura.total;
            });
        }
    });

    return totalMes;
}

function obtenerGastosDelMes(fecha) {
    const gastos = JSON.parse(localStorage.getItem('gastos')) || [];
    return gastos.reduce((total, gasto) => {
        const fechaGasto = new Date(gasto.fecha);
        if (fechaGasto.getMonth() === fecha.getMonth() && 
            fechaGasto.getFullYear() === fecha.getFullYear()) {
            return total + gasto.monto;
        }
        return total;
    }, 0);
}

function cargarTransacciones() {
    const tabla = document.getElementById('transaccionesTabla');
    // Implementar lógica para cargar transacciones
    // Ejemplo de datos
    const transacciones = [
        { fecha: '2024-04-01', tipo: 'Ingreso', descripcion: 'Ventas del día', monto: 15000, estado: 'Completado' },
        { fecha: '2024-04-01', tipo: 'Gasto', descripcion: 'Pago proveedores', monto: -5000, estado: 'Completado' },
    ];

    tabla.innerHTML = transacciones.map(t => `
        <tr>
            <td>${new Date(t.fecha).toLocaleDateString()}</td>
            <td>${t.tipo}</td>
            <td>${t.descripcion}</td>
            <td class="${t.monto >= 0 ? 'ingreso' : 'gasto'}">${formatearMoneda(t.monto)}</td>
            <td><span class="estado ${t.estado.toLowerCase()}">${t.estado}</span></td>
        </tr>
    `).join('');
}

function actualizarDatos() {
    const periodo = document.getElementById('periodoSelect').value;
    // Implementar lógica para actualizar datos según el período seleccionado
    cargarDatosResumen();
    // Actualizar gráficos...
}

async function exportarReporte() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'mm', 'a4');
    const dashboard = document.querySelector('.dashboard');
    
    try {
        // Mostrar mensaje de carga
        mostrarMensajeCarga('Generando PDF...');

        // Configuración inicial del PDF
        doc.setFont('helvetica');
        doc.setFontSize(20);
        doc.text('Reporte - Bar Galileo', 105, 15, { align: 'center' });
        doc.setFontSize(12);
        doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 105, 25, { align: 'center' });

        // Agregar resumen de datos
        let yPos = 40;
        doc.setFontSize(16);
        doc.text('Resumen General', 15, yPos);
        
        yPos += 10;
        doc.setFontSize(12);
        doc.text(`Ingresos Totales: ${document.getElementById('totalIngresos').textContent}`, 20, yPos);
        yPos += 8;
        doc.text(`Gastos Totales: ${document.getElementById('totalGastos').textContent}`, 20, yPos);
        yPos += 8;
        doc.text(`Balance: ${document.getElementById('balance').textContent}`, 20, yPos);
        yPos += 8;
        doc.text(`Productos Vendidos: ${document.getElementById('productosVendidos').textContent}`, 20, yPos);

        // Capturar y agregar gráficos
        const graficos = document.querySelectorAll('.chart-container');
        yPos += 15;

        for (let i = 0; i < graficos.length; i++) {
            const grafico = graficos[i];
            const titulo = grafico.querySelector('h3').textContent;
            const canvas = grafico.querySelector('canvas');

            // Agregar título del gráfico
            doc.setFontSize(14);
            yPos += 10;
            doc.text(titulo, 15, yPos);
            yPos += 5;

            // Capturar y agregar el gráfico
            const graficoImagen = await html2canvas(canvas);
            const imgData = graficoImagen.toDataURL('image/png');
            doc.addImage(imgData, 'PNG', 15, yPos, 180, 90);
            yPos += 100;

            // Nueva página si es necesario
            if (yPos > 250 && i < graficos.length - 1) {
                doc.addPage();
                yPos = 20;
            }
        }

        // Guardar PDF
        const fecha = new Date().toISOString().split('T')[0];
        doc.save(`Reporte_BarGalileo_${fecha}.pdf`);
        
        // Ocultar mensaje de carga y mostrar éxito
        ocultarMensajeCarga();
        mostrarMensaje('PDF generado exitosamente', 'exito');

    } catch (error) {
        console.error('Error al generar PDF:', error);
        ocultarMensajeCarga();
        mostrarMensaje('Error al generar PDF', 'error');
    }
}

function mostrarMensajeCarga(texto) {
    const mensaje = document.createElement('div');
    mensaje.id = 'mensajeCarga';
    mensaje.innerHTML = `
        <div class="mensaje-carga">
            <i class="fas fa-spinner fa-spin"></i>
            ${texto}
        </div>
    `;
    document.body.appendChild(mensaje);
}

function ocultarMensajeCarga() {
    const mensaje = document.getElementById('mensajeCarga');
    if (mensaje) {
        mensaje.remove();
    }
}

function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}