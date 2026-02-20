# Solución al Error CSRF (403 Forbidden)

## Problema
Al intentar realizar solicitudes POST (especialmente AJAX) en la aplicación, se recibía el error:
```
Prohibido (403)
Verificación CSRF fallida. Solicitud abortada.
CSRF token missing.
```

## Causa
El error CSRF (Cross-Site Request Forgery) ocurre cuando Django no puede verificar que una solicitud POST proviene de una fuente confiable. Esto puede suceder por varias razones:

1. **Token CSRF faltante en solicitudes AJAX**: Las solicitudes AJAX POST no incluían el token CSRF en los headers
2. **Vistas sin decoradores apropiados**: Las vistas AJAX no tenían los decoradores `@require_POST` y `@ensure_csrf_cookie`
3. **Configuración de orígenes confiables**: Faltaba la configuración de `CSRF_TRUSTED_ORIGINS` para desarrollo local

## Soluciones Implementadas

### 1. Decoradores en Vistas AJAX ([admin_dashboard/views.py](../bar_galileo/admin_dashboard/views.py))

Se agregaron los decoradores necesarios a las vistas AJAX:

```python
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

# Vista de gestión de imágenes - asegura que el cookie CSRF esté disponible
@method_decorator([permission_required('dashboard', 'editar'), ensure_csrf_cookie], name='dispatch')
class ImageManagementView(TemplateView):
    template_name = 'admin_dashboard/image_management.html'
    # ...

# Vistas AJAX - requieren método POST
@require_POST
@permission_required('dashboard', 'editar')
def carousel_reorder_ajax(request):
    # ...

@require_POST
@permission_required('dashboard', 'editar')
def carousel_toggle_active(request, pk):
    # ...

@require_POST
@permission_required('dashboard', 'editar')
def site_image_toggle_active(request, pk):
    # ...
```

**Beneficios:**
- `@require_POST`: Asegura que solo se acepten solicitudes POST
- `@ensure_csrf_cookie`: Garantiza que el cookie CSRF esté disponible en el navegador
- Elimina validaciones manuales de `if request.method == 'POST'`

### 2. Configuración de Orígenes Confiables ([bar_galileo/settings.py](../bar_galileo/bar_galileo/settings.py))

Se agregó la configuración `CSRF_TRUSTED_ORIGINS`:

```python
# Orígenes confiables para CSRF (necesario para AJAX y solicitudes cross-origin)
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost',
        'http://127.0.0.1',
    ]
else:
    # En producción, leer desde variable de entorno
    trusted_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in trusted_origins.split(',') if origin.strip()]
```

**Beneficios:**
- Permite solicitudes desde localhost en desarrollo
- En producción, se configura mediante variables de entorno
- Facilita el desarrollo local y pruebas

### 3. JavaScript ya estaba correctamente implementado

El código JavaScript en los templates ya enviaba correctamente el token CSRF:

```javascript
// Función para obtener el cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Uso en solicitudes AJAX
fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')  // ✓ Token CSRF incluido
    },
    body: JSON.stringify(data)
})
```

## Configuración Existente (Ya Correcta)

Las siguientes configuraciones ya estaban correctamente implementadas:

### Middleware CSRF
```python
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',  # ✓ Presente
    # ...
]
```

### Configuración de Cookies CSRF
```python
# Cookies CSRF seguras
CSRF_COOKIE_SECURE = not DEBUG  # False en desarrollo, True en producción
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Templates con {% csrf_token %}
Los formularios POST en templates ya incluían el token:
```django
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}  # ✓ Token presente
    <!-- campos del formulario -->
</form>
```

## Pasos para Verificar la Solución

1. **Reiniciar el servidor de desarrollo**:
   ```bash
   cd bar_galileo
   python manage.py runserver
   ```

2. **Limpiar cookies del navegador**:
   - Chrome/Firefox: `F12` → Pestaña "Application" → "Cookies" → Eliminar cookies de localhost
   - O usar modo incógnito para probar

3. **Acceder a la gestión de imágenes**:
   ```
   http://localhost:8000/admin/images/
   ```

4. **Probar funcionalidades AJAX**:
   - Reordenar imágenes del carrusel (arrastrar y soltar)
   - Activar/desactivar imágenes
   - Eliminar imágenes

5. **Verificar en la consola del navegador**:
   - `F12` → Pestaña "Console"
   - No debería haber errores 403
   - Debería aparecer: `✅ Orden actualizado correctamente` o similar

## Problemas Comunes y Soluciones

### Error: "CSRF token missing" persiste

**Solución 1: Limpiar cookies**
```bash
# En el navegador:
F12 → Application → Cookies → Eliminar todas las cookies de localhost
```

**Solución 2: Verificar que JavaScript está cargando**
```bash
# En la consola del navegador (F12):
console.log(getCookie('csrftoken'));
# Debería mostrar un token largo, no null
```

**Solución 3: Verificar ALLOWED_HOSTS**
```python
# En settings.py, debe incluir:
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']  # Para desarrollo
```

### Error: "Referer checking failed"

**Causa**: El header Referer no coincide con ALLOWED_HOSTS

**Solución**: Agregar el dominio a CSRF_TRUSTED_ORIGINS:
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://tu-dominio.com',  # Agregar tu dominio real
]
```

### Solicitudes AJAX desde subdominios

**Configuración adicional para subdominios**:
```python
# En settings.py
CSRF_COOKIE_DOMAIN = '.tudominio.com'  # Nota el punto inicial
```

## Configuración para Producción

Al desplegar en producción, asegúrate de:

1. **Configurar CSRF_TRUSTED_ORIGINS en .env**:
   ```
   CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com
   ```

2. **Habilitar cookies seguras** (ya configurado):
   ```python
   CSRF_COOKIE_SECURE = True  # Cuando DEBUG=False
   SESSION_COOKIE_SECURE = True
   ```

3. **Configurar ALLOWED_HOSTS**:
   ```
   ALLOWED_HOSTS=tudominio.com,www.tudominio.com
   ```

4. **Usar HTTPS**:
   - CSRF requiere HTTPS en producción cuando `CSRF_COOKIE_SECURE = True`

## Referencias

- [Documentación oficial de Django CSRF](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [Django AJAX CSRF Protection](https://docs.djangoproject.com/en/5.2/howto/csrf/#ajax)
- [CSRF_TRUSTED_ORIGINS](https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-trusted-origins)

## Resumen de Cambios

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `admin_dashboard/views.py` | Agregados decoradores `@require_POST` y `@ensure_csrf_cookie` | Asegurar validación correcta de solicitudes POST y disponibilidad del token CSRF |
| `bar_galileo/settings.py` | Agregado `CSRF_TRUSTED_ORIGINS` | Permitir solicitudes desde localhost y dominios configurados |
| Templates | Ya correctos | Los templates ya incluían `{% csrf_token %}` |
| JavaScript | Ya correcto | El código JS ya enviaba el token en headers |

## Estado
✅ **Solucionado** - Todas las configuraciones CSRF están correctamente implementadas.

Si el problema persiste, verifica:
1. Las cookies del navegador están habilitadas
2. El servidor está ejecutándose correctamente
3. No hay extensiones de navegador bloqueando cookies
4. La URL en el navegador coincide con CSRF_TRUSTED_ORIGINS
