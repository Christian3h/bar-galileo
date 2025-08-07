from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import Cast
from django.db.models.deletion import ProtectedError
from .models import Mesa, Factura
from .forms import MesaForm
from django.views.decorators.http import require_POST
from django.contrib import messages

def lista_mesas(request):
    mesas = Mesa.objects.all().order_by('nombre')
    return render(request, 'mesas/lista_mesas_native.html', {'mesas': mesas})

def crear_mesa(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            if Mesa.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"La mesa con nombre '{nombre}' ya existe.")
            else:
                form.save()
                messages.success(request, "Mesa creada exitosamente.")
                return redirect('tables:mesas_lista')
        else:
            messages.error(request, "Esta Mesa ya está registrada.")
    else:
        form = MesaForm()

    return render(request, 'mesas/crear_mesa.html', {'form': form})

@require_POST
def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa_nombre = mesa.nombre

    # Obtener pedidos asociados a la mesa
    pedidos_facturados = mesa.pedidos.filter(factura__isnull=False)
    pedidos_sin_facturar = mesa.pedidos.filter(factura__isnull=True)

    # Si hay pedidos sin facturar, no permitir eliminar y mostrar mensaje
    if pedidos_sin_facturar.exists():
        messages.error(request, "No se puede eliminar la mesa porque tiene pedidos sin facturar. Por favor, facture todos los pedidos antes de eliminar la mesa.")
        return redirect('tables:confirmar_eliminar_mesa', mesa_id=mesa.id)

    # Para pedidos facturados, solo quitamos la referencia a la mesa
    if pedidos_facturados.exists():
        pedidos_facturados.update(mesa=None)

    # Ahora podemos eliminar la mesa sin problemas
    mesa.delete()

    mensaje = f"Mesa '{mesa_nombre}' eliminada correctamente."
    if pedidos_facturados.exists():
        mensaje += f" Los pedidos facturados ({pedidos_facturados.count()}) se mantuvieron para registro contable."

    messages.success(request, mensaje)
    return redirect('tables:mesas_lista')

def cambiar_estado(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    nuevo_estado = request.POST.get('estado')

    estados_validos = ['disponible', 'ocupada', 'reservada', 'fuera de servicio']
    if nuevo_estado in estados_validos:
        mesa.estado = nuevo_estado
        mesa.save()
        messages.success(request, f"Estado de la mesa actualizado a '{nuevo_estado}'.")
    else:
        messages.error(request, "Estado inválido.")

    return redirect('tables:mesas_lista')

@require_POST
def editar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    nuevo_nombre = request.POST.get('nombre', '').strip()
    nueva_desc = request.POST.get('descripcion', '').strip()

    # Validar nombre vacío
    if not nuevo_nombre:
        messages.error(request, "El nombre de la mesa no puede estar vacío.")
        return redirect('tables:mesas_lista')

    # Validar nombre duplicado (excepto la misma mesa)
    if Mesa.objects.exclude(id=mesa_id).filter(nombre__iexact=nuevo_nombre).exists():
        messages.error(request, f"Ya existe una mesa con el nombre '{nuevo_nombre}'.")
        return redirect('tables:mesas_lista')

    mesa.nombre = nuevo_nombre
    mesa.descripcion = nueva_desc
    mesa.save()
    messages.success(request, "Mesa actualizada correctamente.")
    return redirect('tables:mesas_lista')

def ver_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'pedidos/factura.html', {'factura': factura})

def confirmar_eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Verificar si hay pedidos asociados
    pedidos = mesa.pedidos.all()
    pedidos_con_factura = []
    pedidos_sin_factura = []
    
    for pedido in pedidos:
        if hasattr(pedido, 'factura'):
            pedidos_con_factura.append(pedido)
        else:
            pedidos_sin_factura.append(pedido)
    
    # Ahora siempre se puede eliminar la mesa
    puede_eliminar = True
    
    context = {
        'mesa': mesa,
        'puede_eliminar': puede_eliminar,
        'pedidos_con_factura': pedidos_con_factura,
        'pedidos_sin_factura': pedidos_sin_factura,
        'total_pedidos': len(pedidos)
    }
    
    return render(request, 'mesas/confirmar_eliminar.html', context)

@require_POST
def liberar_mesa(request, mesa_id):
    """
    Libera una mesa eliminando solo los pedidos sin facturar,
    pero manteniendo la mesa y los pedidos facturados.
    """
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    # Obtener pedidos sin factura
    pedidos_sin_factura = mesa.pedidos.filter(factura__isnull=True)
    
    if pedidos_sin_factura.exists():
        count = pedidos_sin_factura.count()
        pedidos_sin_factura.delete()
        
        # Cambiar estado de la mesa a disponible
        mesa.estado = 'disponible'
        mesa.save()
        
        messages.success(
            request, 
            f"Mesa '{mesa.nombre}' liberada. Se eliminaron {count} pedido(s) sin facturar. "
            f"La mesa ahora está disponible."
        )
    else:
        messages.info(
            request, 
            f"La mesa '{mesa.nombre}' no tiene pedidos sin facturar que eliminar."
        )
    
    return redirect('tables:mesas_lista')
