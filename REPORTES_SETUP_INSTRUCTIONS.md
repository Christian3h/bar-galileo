# CONFIGURACIÓN DEL MÓDULO DE REPORTES - INSTRUCCIONES

## Estado Actual
✅ Módulo de reportes creado en `/bar_galileo/reportes/`
✅ Migración aplicada (`reportes.0001_initial`)
✅ URLs configuradas en el proyecto
✅ App agregada a `INSTALLED_APPS`
✅ Enlace agregado al menú con validación de permisos

## ⚠️ FALTA POR HACER

### Paso 1: Crear el módulo "reportes" en la base de datos

Ejecuta estos comandos en el terminal:

```bash
cd /Users/jorgealfredoarismendyzambrano/Documents/bar-galileo
.venv/bin/python setup_reportes.py
```

O alternativamente, usa el shell de Django:

```bash
cd /Users/jorgealfredoarismendyzambrano/Documents/bar-galileo/bar_galileo
.venv/bin/python manage.py shell
```

Y luego ejecuta:

```python
from roles.models import Module, Action

# Crear módulo de reportes
reportes = Module.objects.get_or_create(nombre='reportes')[0]
print(f"Módulo reportes: {reportes}")

# Verificar acciones
ver = Action.objects.get_or_create(nombre='ver')[0]
crear = Action.objects.get_or_create(nombre='crear')[0]
editar = Action.objects.get_or_create(nombre='editar')[0]
eliminar = Action.objects.get_or_create(nombre='eliminar')[0]
print("Acciones verificadas")

exit()
```

### Paso 2: Asignar permisos a los roles

Una vez creado el módulo "reportes", debes:

1. **Acceder al Dashboard** → Roles y Permisos → Lista de roles
2. **Seleccionar un rol** (por ejemplo, "Administrador")
3. **Editar el rol**
4. **Buscar el módulo "reportes"** en la lista de permisos
5. **Marcar las casillas** de los permisos que quieres dar:
   - ☑️ Ver (para que aparezca en el menú)
   - ☑️ Crear (para el botón "Crear Reporte")
   - ☑️ Editar (para editar reportes)
   - ☑️ Eliminar (para eliminar reportes)
6. **Guardar cambios**

### Paso 3: Verificar

1. Cierra sesión y vuelve a iniciar sesión (o refresca la página)
2. El módulo "Reportes" debería aparecer en el menú lateral
3. Solo los usuarios con el permiso "reportes,ver" verán este módulo

## Comportamiento Esperado

### Usuario CON permisos "reportes,ver":
- ✅ Ve el módulo "Reportes" en el menú
- ✅ Puede acceder a la lista de reportes

### Usuario SIN permisos "reportes,ver":
- ❌ NO ve el módulo "Reportes" en el menú
- ❌ Si intenta acceder directamente a la URL, será bloqueado

## Solución de Problemas

### El módulo no aparece en el menú
1. Verifica que el módulo "reportes" existe en la base de datos
2. Verifica que el rol del usuario tiene el permiso "reportes,ver"
3. Cierra sesión y vuelve a iniciar sesión
4. Limpia la caché del navegador (Ctrl+Shift+R o Cmd+Shift+R)

### Error al acceder a reportes
- Verifica que las migraciones están aplicadas: `python manage.py migrate`
- Verifica que no hay errores en los logs del servidor

## Archivos Modificados

- `/bar_galileo/bar_galileo/settings.py` - Agregada app 'reportes' a INSTALLED_APPS
- `/bar_galileo/bar_galileo/urls.py` - Agregada ruta de reportes
- `/bar_galileo/admin_dashboard/templates/components/nav-admin.html` - Agregado enlace con validación de permisos
- `/bar_galileo/reportes/` - Toda la estructura del módulo creada

## Sistema de Permisos

El sistema funciona de la siguiente manera:

```django
{% if request.user|has_perm:"reportes,ver" %}
    <!-- Mostrar módulo en el menú -->
{% endif %}
```

Este template tag verifica:
1. Usuario autenticado
2. Usuario tiene un `userprofile` con un `rol` asignado
3. Existe un `RolePermission` que conecta:
   - El rol del usuario
   - El módulo "reportes"
   - La acción "ver"
