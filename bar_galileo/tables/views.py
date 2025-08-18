from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import Cast
from django.db.models.deletion import ProtectedError
from .models import Mesa, Factura
from .forms import MesaForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

class MesaListView(ListView):
    model = Mesa
    template_name = 'mesas/lista_mesas_native.html'
    context_object_name = 'mesas'

    def get_queryset(self):
        return Mesa.objects.all().order_by('nombre')

class MesaCreateView(SuccessMessageMixin, CreateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'mesas/crear_mesa.html'
    success_url = reverse_lazy('tables:mesas_lista')
    success_message = "Mesa creada exitosamente."

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        if Mesa.objects.filter(nombre__iexact=nombre).exists():
            messages.error(self.request, f"La mesa con nombre '{nombre}' ya existe.")
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrige los errores en el formulario.")
        return super().form_invalid(form)

class MesaUpdateView(SuccessMessageMixin, UpdateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'mesas/editar_mesa.html' # You might need to create this template
    success_url = reverse_lazy('tables:mesas_lista')
    success_message = "Mesa actualizada correctamente."

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        if Mesa.objects.exclude(pk=self.object.pk).filter(nombre__iexact=nombre).exists():
            messages.error(self.request, f"Ya existe una mesa con el nombre '{nombre}'.")
            return self.form_invalid(form)
        return super().form_valid(form)

class MesaDeleteView(DeleteView):
    model = Mesa
    template_name = 'mesas/confirmar_eliminar.html' # Assumes this is the confirmation page
    success_url = reverse_lazy('tables:mesas_lista')

    def post(self, request, *args, **kwargs):
        mesa = self.get_object()
        mesa_nombre = mesa.nombre
        pedidos_sin_facturar = mesa.pedidos.filter(factura__isnull=True)

        if pedidos_sin_facturar.exists():
            messages.error(request, f"No se puede eliminar la mesa '{mesa_nombre}' porque tiene pedidos sin facturar.")
            return redirect('tables:mesas_lista')

        pedidos_facturados = mesa.pedidos.filter(factura__isnull=False)
        if pedidos_facturados.exists():
            pedidos_facturados.update(mesa=None)

        messages.success(request, f"Mesa '{mesa_nombre}' eliminada correctamente.")
        return super().post(request, *args, **kwargs)


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
