# Guía de Implementación: Gestión de Clientes en Pedidos

Este documento describe los pasos necesarios para modificar el backend y añadir la funcionalidad de asociar múltiples clientes a un pedido. Al finalizar, tendrás una API lista para que puedas construir la interfaz de usuario (frontend).

---

### Paso 1: Modificar los Modelos (Base de Datos)

Primero, necesitamos enseñarle a nuestra base de datos qué es un "Cliente" y cómo se relaciona con un "Pedido".

**Acción:** Abre el archivo `bar_galileo/tables/models.py` y realiza los siguientes dos cambios:

1.  **Añade el modelo `Cliente`:** Pega este código al principio del archivo, después de las importaciones.

    ```python
    class Cliente(models.Model):
        """Representa a un cliente que puede estar asociado a un pedido."""
        nombre = models.CharField(max_length=100, unique=True)
        fecha_creacion = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.nombre
    ```

2.  **Actualiza el modelo `Pedido`:** Añade el campo `clientes` al modelo `Pedido` existente. La relación `ManyToManyField` permite que un pedido tenga muchos clientes y que un cliente pueda estar en muchos pedidos.

    ```python
    # Dentro de la clase Pedido:
    class Pedido(models.Model):
        # ... campos existentes ...
        mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, related_name='pedidos', null=True, blank=True)
        clientes = models.ManyToManyField(Cliente, related_name='pedidos', blank=True) # <--- AÑADE ESTA LÍNEA
        fecha_creacion = models.DateTimeField(auto_now_add=True)
        # ... resto de campos ...
    ```

---

### Paso 2: Aplicar los Cambios a la Base de Datos

Una vez guardados los cambios en `models.py`, necesitas que Django cree y aplique la nueva estructura en tu base de datos.

**Acción:** Abre tu terminal y ejecuta los siguientes dos comandos, en orden:

1.  **Crear el archivo de migración:**
    ```bash
    python manage.py makemigrations tables
    ```
    *Esto generará un nuevo archivo en la carpeta `migrations` de la app `tables` que describe los cambios que hicimos.*

2.  **Aplicar la migración:**
    ```bash
    python manage.py migrate
    ```
    *Esto leerá el archivo de migración y modificará tu base de datos para añadir la tabla `Cliente` y la relación con `Pedido`.*

---

### Paso 3: Crear la API para Gestionar Clientes

Ahora crearemos las funciones y URLs de la API para que el frontend pueda comunicarse con la base de datos.

1.  **Añade las funciones a `views_api.py`:**
    *   **Acción:** Abre `bar_galileo/tables/views_api.py` y pega el siguiente código al final del archivo.

    ```python
    from .models import Cliente # Asegúrate de importar el nuevo modelo al principio del archivo

    def cliente_list_create_api(request):
        """API para listar o crear clientes."""
        if request.method == 'GET':
            clientes = Cliente.objects.all().order_by('nombre')
            data = [{'id': cliente.id, 'nombre': cliente.nombre} for cliente in clientes]
            return JsonResponse(data, safe=False)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            nombre = data.get('nombre')
            if not nombre:
                return JsonResponse({'error': 'El nombre es requerido'}, status=400)
            cliente, created = Cliente.objects.get_or_create(nombre=nombre)
            if not created:
                return JsonResponse({'error': 'Un cliente con este nombre ya existe'}, status=400)
            return JsonResponse({'id': cliente.id, 'nombre': cliente.nombre}, status=201)

    def pedido_manage_cliente_api(request, pedido_id):
        """API para añadir o quitar un cliente de un pedido."""
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        pedido = get_object_or_404(Pedido, id=pedido_id)
        data = json.loads(request.body)
        cliente_id = data.get('cliente_id')
        action = data.get('action')

        if not cliente_id or action not in ['add', 'remove']:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)

        cliente = get_object_or_404(Cliente, id=cliente_id)

        if action == 'add':
            pedido.clientes.add(cliente)
        elif action == 'remove':
            pedido.clientes.remove(cliente)
            
        return JsonResponse({'success': True})
    ```

2.  **Añade las nuevas URLs a `urls.py`:**
    *   **Acción:** Abre `bar_galileo/tables/urls.py` y añade estas dos nuevas rutas dentro de la lista `urlpatterns`.

    ```python
    # Al final de la lista de urlpatterns, antes del ]
    path('api/clientes/', views_api.cliente_list_create_api, name='api_cliente_list_create'),
    path('api/pedidos/<int:pedido_id>/clientes/', views_api.pedido_manage_cliente_api, name='api_pedido_manage_cliente'),
    ```

---

### Paso 4: Actualizar la API de Pedidos Existente

Para que el frontend sepa qué clientes están en un pedido al abrir el modal, debemos modificar la respuesta de la API principal.

**Acción:** En `bar_galileo/tables/views_api.py`, busca la función `mesa_pedido_api` y modifícala para que incluya la información de los clientes.

```python
# En la función mesa_pedido_api, modifica el JsonResponse final

def mesa_pedido_api(request, mesa_id):
    # ... (código existente al principio de la función)

    # Modifica el diccionario que se retorna
    return JsonResponse({
        'mesa': {'id': mesa.id, 'nombre': mesa.nombre},
        'pedido': _serialize_pedido(pedido), # _serialize_pedido también necesita ser actualizado
        'productos': productos_data,
        'reservas_stock': reservas_stock
    })
```

**Acción:** Ahora, actualiza la función auxiliar `_serialize_pedido` para que incluya los clientes.

```python
# En la función _serialize_pedido
def _serialize_pedido(pedido):
    pedido.refresh_from_db()
    return {
        'id': pedido.id,
        'items': [ ... ], # sin cambios aquí
        'total': float(pedido.total()),
        'clientes': [ # <--- AÑADE ESTA SECCIÓN
            {'id': cliente.id, 'nombre': cliente.nombre}
            for cliente in pedido.clientes.all()
        ]
    }
```

---

### Paso 5: Guía de Uso de la Nueva API (Para tu Frontend)

¡Listo! El backend está preparado. Aquí tienes el manual para usarlo desde tu JavaScript:

#### Para Listar todos los Clientes
*   **Petición:** `GET /api/clientes/`
*   **Respuesta Exitosa (JSON):**
    ```json
    [
        {"id": 1, "nombre": "Carlos Rodriguez"},
        {"id": 2, "nombre": "Ana Gomez"}
    ]
    ```

#### Para Crear un Nuevo Cliente
*   **Petición:** `POST /api/clientes/`
*   **Cuerpo de la Petición (JSON):**
    ```json
    {"nombre": "Laura Pausini"}
    ```
*   **Respuesta Exitosa (JSON):**
    ```json
    {"id": 3, "nombre": "Laura Pausini"}
    ```

#### Para Añadir un Cliente a un Pedido
*   **Petición:** `POST /api/pedidos/123/clientes/` (donde `123` es el ID del pedido)
*   **Cuerpo de la Petición (JSON):**
    ```json
    {"cliente_id": 3, "action": "add"}
    ```

#### Para Quitar un Cliente de un Pedido
*   **Petición:** `POST /api/pedidos/123/clientes/` (donde `123` es el ID del pedido)
*   **Cuerpo de la Petición (JSON):**
    ```json
    {"cliente_id": 3, "action": "remove"}
    ```

---

Con estos pasos, tienes toda la infraestructura necesaria. Ahora puedes enfocarte en construir la interfaz de usuario para gestionar los clientes con la confianza de que el backend responderá como esperas.
