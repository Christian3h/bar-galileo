# 🔄 Actualización del Módulo de Nóminas

## 📋 Cambios Realizados

### 1. ✅ **Interfaz Visual Mejorada**
- Diseño moderno y consistente con el módulo de reportes
- Eliminados conflictos de merge (<<<<<<< HEAD)
- Colores sencillos: negro, gris, blanco y dorado
- Layout responsive para todos los dispositivos
- Sin elementos superpuestos

### 2. 🔗 **Conexión con Sistema de Usuarios**
Se agregó un nuevo campo `usuario` al modelo `Empleado` que permite:
- Conectar empleados de nómina con usuarios del sistema
- Sincronizar automáticamente información (nombre, email, teléfono, dirección)
- Mantener la relación opcional (un empleado puede existir sin usuario)
- Solo un usuario puede estar asignado a un empleado

### 3. 📊 **Sincronización de Datos**
Cuando se conecta un empleado con un usuario:
- **Nombre**: Se toma de `first_name` y `last_name` del User
- **Email**: Se toma del User.email
- **Teléfono**: Se toma del PerfilUsuario (si existe)
- **Dirección**: Se toma del PerfilUsuario (si existe)

---

## 🚀 Pasos para Aplicar los Cambios

### 1️⃣ Crear la Migración

```bash
cd c:\Users\felip\Documents\bar-galileo\bar_galileo
python manage.py makemigrations nominas
```

**Salida esperada:**
```
Migrations for 'nominas':
  nominas/migrations/0XXX_add_usuario_field.py
    - Add field usuario to empleado
```

### 2️⃣ Aplicar la Migración

```bash
python manage.py migrate nominas
```

**Salida esperada:**
```
Running migrations:
  Applying nominas.0XXX_add_usuario_field... OK
```

### 3️⃣ Verificar que Todo Funciona

```bash
python manage.py check
```

**Salida esperada:**
```
System check identified no issues (0 silenced).
```

### 4️⃣ Ejecutar el Servidor

```bash
python manage.py runserver
```

Ir a: http://127.0.0.1:8000/nominas/

---

## 📝 Cómo Usar la Nueva Funcionalidad

### Crear un Empleado Conectado a un Usuario

1. **Ir a Nóminas** → Crear Empleado
2. **Seleccionar un usuario** del sistema (dropdown)
3. Los campos se prellenarán automáticamente con la info del usuario
4. **Completar** los datos adicionales (cargo, salario, etc.)
5. **Guardar**

### Características Importantes:

✅ **Opcional**: Un empleado puede existir sin usuario
✅ **Único**: Cada usuario solo puede estar asignado a un empleado
✅ **Automático**: Los datos se sincronizan automáticamente
✅ **Actualizable**: Se puede cambiar el usuario asignado después

---

## 🎨 Mejoras Visuales Aplicadas

### Antes:
- ❌ Conflictos de merge visibles en el código
- ❌ Diseño inconsistente
- ❌ Múltiples archivos CSS externos
- ❌ Colores desordenados

### Ahora:
- ✅ Código limpio sin conflictos
- ✅ Diseño igual al de reportes
- ✅ CSS inline organizado
- ✅ Paleta de colores simple:
  - Fondos: `#262626`, `#1a1a1a`
  - Bordes: `#444`, `#555`
  - Primario: `#d4af37` (dorado)
  - Texto: `#ddd`, `#fff`

---

## 🔍 Verificar la Conexión

### Ver Empleados Conectados

En el admin de Django o en tu vista personalizada:

```python
# En Python shell
python manage.py shell

# Verificar empleados con usuario
from nominas.models import Empleado
empleados_conectados = Empleado.objects.filter(usuario__isnull=False)
for emp in empleados_conectados:
    print(f"{emp.nombre} → {emp.usuario.username}")

# Verificar usuarios con empleado
from django.contrib.auth.models import User
usuarios_con_empleado = User.objects.filter(empleado_nomina__isnull=False)
for user in usuarios_con_empleado:
    print(f"{user.username} → {user.empleado_nomina.cargo}")
```

---

## 📊 Estructura del Modelo Actualizado

```python
class Empleado(models.Model):
    # NUEVO CAMPO
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleado_nomina'
    )
    
    # Campos existentes
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    # ... más campos ...
    
    # NUEVO MÉTODO
    def sincronizar_con_usuario(self):
        """Sincroniza datos del empleado con su usuario"""
        if self.usuario:
            # Actualiza nombre, email, teléfono, dirección
            # desde User y PerfilUsuario
```

---

## ⚠️ Consideraciones Importantes

### 1. **Datos Existentes**
Los empleados existentes NO se verán afectados. El campo `usuario` será `NULL` para ellos hasta que manualmente los conectes con un usuario.

### 2. **Usuarios Disponibles**
Solo aparecerán en el dropdown los usuarios que:
- No estén ya asignados a otro empleado
- Estén activos en el sistema

### 3. **Sincronización**
La sincronización ocurre:
- Al guardar un empleado con usuario seleccionado
- Al cambiar el usuario asignado
- Manualmente llamando a `empleado.sincronizar_con_usuario()`

### 4. **Eliminación**
Si se elimina un usuario del sistema:
- El empleado NO se elimina
- El campo `usuario` se establece en `NULL` (SET_NULL)
- Los datos del empleado se mantienen intactos

---

## 🐛 Solución de Problemas

### Error: "No module named 'nominas.migrations'"
```bash
# Crear carpeta de migraciones si no existe
mkdir c:\Users\felip\Documents\bar-galileo\bar_galileo\nominas\migrations
cd c:\Users\felip\Documents\bar-galileo\bar_galileo\nominas\migrations
type nul > __init__.py
```

### Error: "already exists"
```bash
# Ver migraciones aplicadas
python manage.py showmigrations nominas

# Si hay problemas, hacer un reset (¡CUIDADO EN PRODUCCIÓN!)
python manage.py migrate nominas zero
python manage.py migrate nominas
```

### Error en la vista
```bash
# Limpiar cache de Python
find c:\Users\felip\Documents\bar-galileo -name "*.pyc" -delete
find c:\Users\felip\Documents\bar-galileo -name "__pycache__" -type d -exec rm -rf {} +
```

---

## ✅ Checklist de Verificación

- [ ] Crear migración: `python manage.py makemigrations nominas`
- [ ] Aplicar migración: `python manage.py migrate nominas`
- [ ] Verificar: `python manage.py check`
- [ ] Ejecutar servidor: `python manage.py runserver`
- [ ] Probar crear empleado con usuario
- [ ] Probar crear empleado sin usuario
- [ ] Verificar que la interfaz se ve bien
- [ ] Verificar filtros y búsqueda
- [ ] Verificar acciones (ver, editar, eliminar)

---

## 🎯 Resultado Final

- ✅ Módulo de nóminas conectado con usuarios del sistema
- ✅ Sincronización automática de datos
- ✅ Interfaz visual mejorada y moderna
- ✅ Sin conflictos de merge
- ✅ Código limpio y mantenible
- ✅ Experiencia de usuario consistente

---

**¡Listo para usar!** 🎉
