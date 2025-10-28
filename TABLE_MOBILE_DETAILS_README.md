# Sistema de Visualización de Detalles de Tablas en Móvil

## 📱 Descripción

Este sistema agrega automáticamente botones de "Ver detalles" en todas las tablas del panel de administración. Cuando un usuario está en móvil o tablet, puede hacer clic en este botón para ver toda la información de la fila en un modal, incluyendo las columnas que están ocultas por el diseño responsivo.

## ✨ Características

- **Automático**: Se aplica automáticamente a todas las tablas con clase `.table`
- **Responsivo**: El botón solo se muestra en pantallas menores a 992px
- **Modal elegante**: Diseño oscuro consistente con el tema del sitio
- **Resalta campos ocultos**: Los campos que estaban ocultos se destacan en el modal
- **Compatible con DataTables**: Funciona con tablas estáticas y dinámicas
- **Zero-config**: No requiere configuración adicional

## 🚀 Uso

El sistema se activa automáticamente en todas las páginas que extienden `base_admin.html`.

### Uso Automático

Simplemente crea tu tabla con la clase `table`:

```html
<table class="table">
    <thead>
        <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Acciones</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Juan Pérez</td>
            <td>juan@example.com</td>
            <td>123-456-7890</td>
            <td>
                <a href="#" class="btn btn-primary">Editar</a>
                <!-- El botón de detalles se agregará aquí automáticamente -->
            </td>
        </tr>
    </tbody>
</table>
```

### Uso Manual

Si necesitas agregar los botones manualmente o a tablas específicas:

```javascript
// Agregar a una tabla específica
TableMobileDetails.addDetailsButtons('#mi-tabla');

// Abrir modal manualmente
TableMobileDetails.openModal('Título', '<div>Contenido HTML</div>');

// Cerrar modal
TableMobileDetails.closeModal();
```

## 🎨 Personalización

### CSS

Puedes personalizar los estilos en `/static/css/table-mobile-details.css`:

- `.btn-view-details`: Estilos del botón
- `.table-details-modal`: Estilos del modal
- `.table-details-item.hidden-field`: Resaltado de campos ocultos

### JavaScript

El script está en `/static/js/table-mobile-details.js` y se puede extender según necesidades.

## 📋 Requisitos

- jQuery (ya incluido en base_admin.html)
- Font Awesome para iconos (ya incluido)
- CSS responsivo que oculte columnas con `display: none`

## 🔧 Archivos Involucrados

1. `/static/js/table-mobile-details.js` - Lógica principal
2. `/static/css/table-mobile-details.css` - Estilos del modal y botón
3. `/admin_dashboard/templates/base_admin.html` - Integración en la plantilla base

## 📱 Breakpoints

- **Desktop** (>992px): Botón oculto
- **Tablet** (768px-992px): Botón visible
- **Mobile** (<768px): Botón visible + modal optimizado

## ✅ Compatibilidad

- ✅ Tablas estáticas HTML
- ✅ DataTables
- ✅ Tablas cargadas con AJAX
- ✅ Tablas con contenido dinámico (badges, iconos, imágenes)

## 🎯 Ejemplo de Aplicación

Este sistema está aplicado en:
- ✅ Gestión de Nóminas (`/nominas/`)
- ✅ Lista de Empleados
- ✅ Historial de Pagos
- ✅ Y se puede aplicar a cualquier tabla existente

## 🐛 Troubleshooting

**El botón no aparece:**
- Verifica que la tabla tenga la clase `table`
- Verifica que exista una celda de "Acciones" en cada fila
- Revisa la consola del navegador para errores

**El modal no muestra datos:**
- Verifica que las celdas `<td>` tengan contenido
- Verifica que los headers `<th>` tengan texto
- Asegúrate que el número de `<th>` coincida con `<td>`

**Los estilos no se aplican:**
- Ejecuta `python manage.py collectstatic`
- Verifica que el archivo CSS esté en `/staticfiles/css/table-mobile-details.css`
- Limpia la caché del navegador

## 📝 Notas

- La columna de "Acciones" se excluye automáticamente del modal
- Los campos ocultos se resaltan con un borde dorado
- El modal se cierra al hacer clic fuera de él o en el botón X
- Compatible con teclado (ESC para cerrar en próximas versiones)
