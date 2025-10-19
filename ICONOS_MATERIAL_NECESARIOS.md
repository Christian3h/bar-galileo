# Iconos de Material Icons Necesarios para el Módulo de Accesibilidad

## Lista de iconos que debes descargar

Para que el módulo de accesibilidad funcione completamente sin conexión a internet, necesitas descargar los siguientes iconos de Material Icons:

### Iconos de Ajustes (Settings):
1. **local_parking** - Para "Readable Font"
2. **link** - Para "Highlight Links"
3. **title** - Para "Highlight Title"
4. **record_voice_over** - Para "Read Page"
5. **subscriptions** - Para "Read Full Page"
6. **nightlight** - Para "Dark Mode" (modo oscuro)
7. **brightness_5** - Para "Light Mode" (modo claro)

### Iconos de Ajustes de Fuente:
8. **format_size** - Para el control de tamaño de fuente
9. **add** - Para aumentar tamaño
10. **remove** - Para reducir tamaño

### Iconos de Filtros de Color:
11. **filter_b_and_w** - Para "Monochrome"
12. **gradient** - Para "Low Saturation"
13. **filter_vintage** - Para "High Saturation"
14. **tonality** - Para "High Contrast"

### Iconos de Herramientas:
15. **mouse** - Para "Big Cursor"
16. **motion_photos_off** - Para "Stop Animations"
17. **local_library** - Para "Reading Guide"

### Iconos del Header (ya descargados):
- ✅ **reset.svg** - Ya lo tienes en `/static/img/icons/reset.svg`
- ✅ **close.svg** - Ya lo tienes en `/static/img/icons/close.svg`

## Cómo descargar los iconos

### Opción 1: Google Fonts (SVG individual)
Visita: https://fonts.google.com/icons

Para cada icono:
1. Busca el nombre del icono (ejemplo: "local_parking")
2. Haz clic en el icono
3. Descarga como SVG
4. Guarda en `/home/christian/Documents/bar-galileo/bar_galileo/static/img/icons/`

### Opción 2: Material Design Icons (paquete completo)
Descarga el paquete completo desde:
https://github.com/google/material-design-icons

O usando npm:
```bash
npm install @material-design-icons/svg
```

### Opción 3: Material Icons Font (archivo de fuente)
Descarga la fuente Material Icons completa:
https://github.com/google/material-design-icons/tree/master/font

Archivos necesarios:
- `MaterialIcons-Regular.ttf`
- `MaterialIcons-Regular.woff2`
- `MaterialIcons-Regular.woff`

Guardar en: `/home/christian/Documents/bar-galileo/bar_galileo/static/fonts/material-icons/`

## Estructura de carpetas recomendada

```
bar_galileo/static/
├── fonts/
│   └── material-icons/
│       ├── MaterialIcons-Regular.ttf
│       ├── MaterialIcons-Regular.woff2
│       └── MaterialIcons-Regular.woff
└── img/
    └── icons/
        ├── add.svg ✅ (ya existe)
        ├── close.svg ✅ (ya existe)
        ├── reset.svg ✅ (ya existe)
        ├── local_parking.svg (descargar)
        ├── link.svg (descargar)
        ├── title.svg (descargar)
        ├── record_voice_over.svg (descargar)
        ├── subscriptions.svg (descargar)
        ├── nightlight.svg (descargar)
        ├── brightness_5.svg (descargar)
        ├── format_size.svg (descargar)
        ├── remove.svg (descargar)
        ├── filter_b_and_w.svg (descargar)
        ├── gradient.svg (descargar)
        ├── filter_vintage.svg (descargar)
        ├── tonality.svg (descargar)
        ├── mouse.svg (descargar)
        ├── motion_photos_off.svg (descargar)
        └── local_library.svg (descargar)
```

## Después de descargar

Una vez que tengas todos los iconos descargados, necesitarás:

1. **Si usas SVG individuales**: Modificar `sienna.js` para reemplazar los `<span class="material-icons">` por `<img>` tags
2. **Si usas la fuente**: Crear un archivo CSS local para cargar la fuente Material Icons

---

**NOTA**: Actualmente eliminé la línea que carga Material Icons desde Google Fonts:
```html
<!-- ELIMINADO -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons&text=..." rel="stylesheet">
```

Ahora necesitas implementar una de las opciones anteriores para que los iconos funcionen localmente.
