# 🖼️ Sistema de Gestión de Imágenes

## Descripción

Sistema completo de gestión de imágenes para el panel de administración que permite cambiar dinámicamente todas las imágenes de la página web (carrusel, banners, iconos, etc.) sin necesidad de acceder al código.

## 📋 Características

### ✨ Funcionalidades Principales

1. **Gestión del Carrusel Principal**
   - Agregar, editar y eliminar imágenes del carrusel
   - Reordenar imágenes mediante arrastrar y soltar
   - Activar/desactivar imágenes sin eliminarlas
   - Vista previa en miniatura

2. **Gestión de Imágenes por Secciones**
   - Crear secciones personalizadas para organizar imágenes
   - Asignar imágenes a diferentes partes del sitio
   - Secciones predefinidas: Carrusel, About, Banners, Headers, Footers, etc.

3. **Optimización Automática**
   - Compresión automática de imágenes al subir
   - Redimensionamiento inteligente según el tipo de imagen
   - Soporte para JPG, PNG y WebP
   - Conversión automática de RGBA a RGB cuando sea necesario

4. **Interfaz Intuitiva**
   - Panel visual con miniaturas de todas las imágenes
   - Información en tiempo real del tamaño y dimensiones
   - Sistema drag-and-drop para reordenar
   - Confirmación antes de eliminar

5. **Validaciones**
   - Validación de formato de imagen (cliente y servidor)
   - Límite de tamaño de archivo (5MB para imágenes generales, 10MB para carrusel)
   - Validación de dimensiones
   - Mensajes de error claros y específicos

## 🚀 Uso

### Acceso al Panel

1. Inicia sesión como administrador
2. En el menú lateral, busca la sección **🖼️ Imágenes**
3. Haz clic en **Gestión de imágenes**

### Gestionar el Carrusel Principal

#### Agregar una imagen al carrusel

1. Ve a **🖼️ Imágenes** → **Agregar al carrusel**
2. Completa el formulario:
   - **Título**: Nombre descriptivo de la imagen
   - **Imagen**: Selecciona el archivo (JPG, PNG o WebP)
   - **Texto alternativo**: Descripción para accesibilidad
   - **Texto descriptivo** (opcional): Texto que se mostrará sobre la imagen
   - **URL de enlace** (opcional): Dirección a la que llevará la imagen
   - **Orden**: Posición en el carrusel (puedes cambiarlo después)
   - **Activa**: Marca si quieres que se muestre inmediatamente

3. Haz clic en **➕ Agregar Imagen**

#### Reordenar imágenes del carrusel

1. Ve a **Gestión de imágenes**
2. En la sección **🎠 Carrusel Principal**, arrastra las imágenes usando el ícono **⋮⋮**
3. El orden se guarda automáticamente

#### Editar una imagen del carrusel

1. En la tarjeta de la imagen, haz clic en **✏️ Editar**
2. Modifica los campos necesarios
3. Haz clic en **💾 Guardar Cambios**

#### Activar/Desactivar una imagen

1. En la tarjeta de la imagen, haz clic en **👁️ Ocultar** o **👁️ Mostrar**
2. El cambio se aplica inmediatamente sin eliminar la imagen

#### Eliminar una imagen

1. En la tarjeta de la imagen, haz clic en **🗑️ Eliminar**
2. Confirma la acción en el diálogo que aparece
3. La imagen se elimina permanentemente

### Gestionar Secciones de Imágenes

#### Crear una nueva sección

1. Ve a **🖼️ Imágenes** → **Nueva sección**
2. Completa:
   - **Nombre**: Identificador único de la sección
   - **Tipo**: Selecciona el tipo (Carrusel, About, Banner, etc.)
   - **Descripción** (opcional): Breve descripción del uso

3. Haz clic en **➕ Crear**

#### Agregar imagen a una sección

1. Ve a **🖼️ Imágenes** → **Agregar imagen**
2. Selecciona la **Sección** donde quieres agregar la imagen
3. Completa el resto del formulario similar al carrusel
4. Haz clic en **➕ Agregar**

### Secciones Predefinidas

El sistema incluye estas secciones por defecto:

- **Carrusel Principal - Hero**: Imágenes del carrusel principal
- **Sección Acerca de**: Imagen de la sección "Acerca de"
- **Banner Promocional**: Banners promocionales
- **Iconos de Servicios**: Iconos para servicios
- **Fondo de Página**: Imágenes de fondo
- **Logo y Header**: Logos y elementos del encabezado
- **Pie de Página**: Imágenes del footer

## 📐 Especificaciones Técnicas

### Formatos Soportados

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

### Límites de Tamaño

- **Imágenes del carrusel**: 10 MB máximo
- **Imágenes del sitio**: 5 MB máximo

### Optimización Automática

- **Carrusel**: Redimensionamiento máximo a 1920x1080px
- **Sitio general**: Redimensionamiento máximo a 2000x2000px
- **Compresión JPEG**: Calidad 85%
- **Optimización PNG**: Compresión automática
- **WebP**: Calidad 85%

### Dimensiones Recomendadas

- **Carrusel**: 1920x1080px (16:9)
- **About**: 800x600px o superior
- **Banners**: Variable según ubicación
- **Iconos**: 256x256px o 512x512px

## 🔧 Comandos de Gestión

### Inicializar Secciones Predefinidas

```bash
python manage.py init_image_sections
```

Este comando crea las secciones predefinidas si no existen.

## 📱 Acceso desde el Admin de Django

También puedes gestionar las imágenes desde el panel de administración de Django:

1. Ve a `/admin/`
2. Busca:
   - **Site Image Sections** para gestionar secciones
   - **Site Images** para gestionar imágenes del sitio
   - **Carousel Images** para gestionar el carrusel

## 🎨 Personalización

### Agregar Nuevas Secciones Personalizadas

Puedes crear secciones personalizadas desde el panel de administración seleccionando el tipo "Personalizado" y definiendo un nombre único.

### Integrar Imágenes en Templates

Para usar las imágenes de una sección en tus templates:

```django
{% load static %}

<!-- Obtener imágenes de una sección específica -->
{% for image in site_images %}
  {% if image.section.name == "Tu Sección" and image.is_active %}
    <img src="{{ image.image.url }}" alt="{{ image.alt_text }}">
  {% endif %}
{% endfor %}

<!-- Carrusel -->
{% for image in carousel_images %}
  <div class="slide">
    <img src="{{ image.image.url }}" alt="{{ image.alt_text }}">
    {% if image.caption %}
      <p>{{ image.caption }}</p>
    {% endif %}
  </div>
{% endfor %}
```

## 🔒 Permisos Requeridos

Para acceder y gestionar imágenes, el usuario debe tener los siguientes permisos:

- **Ver dashboard**: `dashboard.ver`
- **Editar dashboard**: `dashboard.editar` (para gestionar imágenes)
- **Crear dashboard**: `dashboard.crear` (para agregar nuevas imágenes)
- **Eliminar dashboard**: `dashboard.eliminar` (para eliminar imágenes)

## 🐛 Solución de Problemas

### La imagen no se sube

1. Verifica que el formato sea JPG, PNG o WebP
2. Comprueba que el tamaño no exceda el límite
3. Revisa que el servidor tenga permisos de escritura en `/media/`

### Las imágenes no aparecen en el sitio

1. Verifica que la imagen esté marcada como **Activa**
2. Comprueba que la sección esté correctamente asignada
3. Revisa que el template esté usando el contexto correcto

### Error al reordenar

1. Asegúrate de arrastrar desde el ícono **⋮⋮**
2. Intenta refrescar la página
3. Verifica tu conexión a internet

## 📊 Modelos de la Base de Datos

### SiteImageSection
- `name`: Nombre de la sección
- `section_type`: Tipo de sección (choices)
- `description`: Descripción
- `created_at`, `updated_at`: Timestamps

### SiteImage
- `section`: Relación con SiteImageSection
- `title`: Título de la imagen
- `image`: Archivo de imagen
- `alt_text`: Texto alternativo
- `order`: Orden de visualización
- `is_active`: Activa/Inactiva
- `width`, `height`: Dimensiones
- `file_size`: Tamaño del archivo
- `created_at`, `updated_at`: Timestamps

### CarouselImage
- `title`: Título
- `image`: Archivo de imagen
- `alt_text`: Texto alternativo
- `caption`: Texto descriptivo
- `link_url`: URL de enlace
- `order`: Orden en el carrusel
- `is_active`: Activa/Inactiva
- `width`, `height`: Dimensiones
- `file_size`: Tamaño del archivo
- `created_at`, `updated_at`: Timestamps

## 🎯 Mejores Prácticas

1. **Nombra descriptivamente**: Usa títulos claros para identificar fácilmente cada imagen
2. **Optimiza antes de subir**: Aunque hay optimización automática, subir imágenes pre-optimizadas mejora el rendimiento
3. **Usa texto alternativo**: Importante para SEO y accesibilidad
4. **Organiza por secciones**: Facilita la gestión y mantenimiento
5. **Revisa antes de eliminar**: La eliminación es permanente
6. **Mantén un orden lógico**: Numera o nombra coherentemente para facilitar el reordenamiento

## 📝 Notas Importantes

- Los cambios se reflejan **inmediatamente** en el sitio web
- Las imágenes se almacenan en `/media/site_images/` y `/media/carousel/`
- Se recomienda hacer backups periódicos de la carpeta `/media/`
- El sistema soporta un número ilimitado de imágenes (sujeto al espacio en disco)

## 🆘 Soporte

Si encuentras algún problema o tienes sugerencias, contacta al administrador del sistema.

---

**Última actualización**: Febrero 2026
**Versión**: 1.0
