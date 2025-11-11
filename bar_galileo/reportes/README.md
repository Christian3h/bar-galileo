# Módulo de Reportes - Bar Galileo

## Descripción General

El módulo de reportes permite generar reportes detallados de todos los módulos del sistema Bar Galileo, con exportación a PDF, Excel y CSV.

## Características

### Tipos de Reportes

1. **Reportes de Ventas**
   - Total de ventas en el periodo
   - Cantidad de facturas generadas
   - Promedio por factura
   - Detalles de cada factura (número, fecha, mesa, items, total)
   - Totales consolidados

2. **Reportes de Gastos**
   - Total de gastos en el periodo
   - Cantidad de gastos registrados
   - Promedio por gasto
   - Gastos por categoría (top 5)
   - Detalles de cada gasto (fecha, categoría, descripción, usuario, monto)

3. **Reportes de Nóminas**
   - Total de empleados activos
   - Total en salarios
   - Promedio salarial
   - Distribución por tipo de contrato
   - Detalles de cada empleado (nombre, cargo, tipo, salario, años de servicio)

4. **Reportes de Inventario**
   - Total de productos
   - Valor del inventario
   - Productos con stock bajo
   - Productos sin stock
   - Detalles de cada producto (nombre, categoría, proveedor, stock, precios, valor)

5. **Reportes de Productos**
   - Total de productos activos
   - Productos por categoría
   - Stock por categoría
   - Detalles de cada producto (nombre, categoría, marca, stock, precios, margen)

6. **Reportes de Mesas y Pedidos**
   - Total de mesas
   - Total de pedidos
   - Pedidos facturados y cancelados
   - Total facturado
   - Promedio por pedido
   - Detalles de cada pedido (número, mesa, fecha, estado, items, total)

7. **Reportes Generales**
   - Total ventas vs gastos
   - Utilidad bruta
   - Margen de ganancia
   - Facturas y gastos del periodo
   - Productos y empleados activos
   - Resumen diario de ventas y gastos

## Estructura de Datos

Cada reporte generado contiene tres secciones principales:

```python
{
    'resumen': {
        # Datos agregados y estadísticas principales
        'Total de Ventas': '$10,000.00',
        'Cantidad de Facturas': 150,
        # ...
    },
    'detalles': [
        # Lista de registros individuales
        {
            'Factura #': '00000123',
            'Fecha': '10/11/2025 14:30',
            'Total': '$150.00',
            # ...
        },
        # ...
    ],
    'totales': {
        # Totales consolidados
        'TOTAL VENTAS': '$10,000.00',
        # ...
    }
}
```

## Formatos de Exportación

### PDF
- Diseño profesional con colores corporativos
- Tablas formateadas con encabezados resaltados
- Incluye toda la información del reporte
- Logo y marca de agua de Bar Galileo
- Pie de página con fecha de generación

### Excel (XLSX)
- Hojas de cálculo formateadas
- Encabezados con colores y estilos
- Columnas auto-ajustadas
- Bordes y formato de tabla
- Fácil de editar y analizar

### CSV
- Formato universal compatible
- UTF-8 con BOM para Excel
- Estructura clara con secciones separadas
- Fácil importación en otros sistemas

## Uso del Módulo

### Crear un Reporte

1. Ir a **Reportes > Nuevo Reporte**
2. Completar el formulario:
   - **Nombre**: Nombre descriptivo del reporte
   - **Tipo**: Seleccionar el tipo de reporte
   - **Periodo**: Seleccionar periodo predefinido o personalizado
   - **Fechas**: Fecha inicio y fin del periodo
   - **Formato**: PDF, Excel o CSV (predeterminado)
   - **Descripción**: Descripción opcional

3. Guardar el reporte

### Generar Datos del Reporte

1. En la vista de detalle del reporte
2. Hacer clic en **"Generar Reporte"**
3. El sistema procesará los datos según el tipo de reporte
4. Los datos se guardan en el reporte para futuras consultas

### Exportar el Reporte

1. En la vista de detalle del reporte
2. Seleccionar formato de exportación (PDF, Excel o CSV)
3. El archivo se descargará automáticamente

## Permisos Necesarios

- **Ver reportes**: `reportes.ver`
- **Crear reportes**: `reportes.crear`
- **Editar reportes**: `reportes.editar`
- **Eliminar reportes**: `reportes.eliminar`
- **Exportar reportes**: `reportes.exportar`
- **Generar reportes**: `reportes.generar`

## Dependencias

### Python Packages
- **openpyxl**: Para exportación a Excel
- **reportlab**: Para exportación a PDF

Instalar con:
```bash
pip install openpyxl reportlab
```

### Módulos Django
- tables (Facturas, Pedidos, Mesas)
- expenses (Gastos)
- nominas (Empleados)
- products (Productos, Inventario)

## API de Utilidades

### `obtener_datos_reporte_detallado(reporte)`
Función principal que obtiene todos los datos del reporte según su tipo.

**Parámetros:**
- `reporte`: Instancia del modelo Reporte

**Retorna:**
```python
{
    'resumen': dict,
    'detalles': list,
    'totales': dict
}
```

### Funciones Específicas por Tipo

- `obtener_datos_ventas(reporte)`
- `obtener_datos_gastos(reporte)`
- `obtener_datos_nominas(reporte)`
- `obtener_datos_inventario(reporte)`
- `obtener_datos_productos(reporte)`
- `obtener_datos_mesas(reporte)`
- `obtener_datos_general(reporte)`

### Funciones de Exportación

- `generar_pdf_reporte(reporte, datos)`
- `generar_excel_reporte(reporte, datos)`
- `generar_csv_reporte(reporte, datos)`

## Ejemplo de Uso Programático

```python
from reportes.models import Reporte
from reportes.utils import obtener_datos_reporte_detallado, generar_pdf_reporte
from datetime import date, timedelta

# Crear reporte
reporte = Reporte.objects.create(
    nombre="Reporte de Ventas Mensual",
    tipo="ventas",
    periodo="mensual",
    fecha_inicio=date.today() - timedelta(days=30),
    fecha_fin=date.today(),
    creado_por=request.user
)

# Generar datos
datos = obtener_datos_reporte_detallado(reporte)
reporte.set_datos(datos)
reporte.generado = True
reporte.save()

# Exportar a PDF
response = generar_pdf_reporte(reporte, datos)
```

## Solución de Problemas

### Error: "openpyxl no está disponible"
```bash
pip install openpyxl
```

### Error: "reportlab no está disponible"
```bash
pip install reportlab
```

### Reporte sin datos
- Verificar que existan datos en el periodo seleccionado
- Verificar que los módulos necesarios estén instalados
- Regenerar el reporte haciendo clic en "Generar Reporte"

### Exportación lenta
- Los reportes con muchos registros pueden tardar
- Considerar reducir el periodo o filtrar datos
- Los datos se cachean después de la primera generación

## Mejoras Futuras

- [ ] Programación de reportes automáticos
- [ ] Envío por email
- [ ] Gráficos y visualizaciones
- [ ] Comparativas entre periodos
- [ ] Filtros avanzados por categorías/productos
- [ ] Reportes personalizados por usuario
- [ ] Dashboard de reportes
- [ ] Exportación a otros formatos (JSON, XML)

## Soporte

Para problemas o sugerencias, contactar al equipo de desarrollo de Bar Galileo.
