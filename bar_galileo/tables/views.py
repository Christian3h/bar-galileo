from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError
from .models import Mesa, Factura
from .forms import MesaForm
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from notifications.utils import notificar_usuario

from django.utils.decorators import method_decorator
from roles.decorators import permission_required

@method_decorator(permission_required('tables', 'ver'), name='dispatch')
class MesaListView(ListView):
    model = Mesa
    template_name = 'mesas/lista_mesas_native.html'
    context_object_name = 'mesas'

    def get_queryset(self):
        return Mesa.objects.all().order_by('nombre')

@method_decorator(permission_required('tables', 'crear'), name='dispatch')
class MesaCreateView(CreateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'mesas/crear_mesa.html'
    success_url = reverse_lazy('tables:mesas_lista')

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        if Mesa.objects.filter(nombre__iexact=nombre).exists():
            form.add_error('nombre', f"La mesa con nombre '{nombre}' ya existe.")
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        
        mensaje = f"Se ha creado la nueva mesa: '{self.object.nombre}'."
        notificar_usuario(self.request.user, mensaje)
            
        return response

@method_decorator(permission_required('tables', 'editar'), name='dispatch')
class MesaUpdateView(UpdateView):
    model = Mesa
    form_class = MesaForm
    template_name = 'mesas/editar_mesa.html'
    success_url = reverse_lazy('tables:mesas_lista')

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        if Mesa.objects.exclude(pk=self.object.pk).filter(nombre__iexact=nombre).exists():
            form.add_error('nombre', f"Ya existe una mesa con el nombre '{nombre}'.")
            return self.form_invalid(form)

        response = super().form_valid(form)

        mensaje = f"La mesa '{self.object.nombre}' ha sido actualizada."
        notificar_usuario(self.request.user, mensaje)

        return response

    def form_invalid(self, form):
        # Si el formulario es inválido, renderiza de nuevo la lista de mesas
        # con el formulario de edición visible y mostrando los errores.
        return render(self.request, 'mesas/lista_mesas_native.html', {
            'mesas': Mesa.objects.all().order_by('nombre'),
            'edit_form': form,
            'error_mesa_pk': self.object.pk,
        })

@method_decorator(permission_required('tables', 'eliminar'), name='dispatch')
class MesaDeleteView(DeleteView):
    model = Mesa
    template_name = 'mesas/confirmar_eliminar.html'
    success_url = reverse_lazy('tables:mesas_lista')

    def post(self, request, *args, **kwargs):
        mesa = self.get_object()
        mesa_nombre = mesa.nombre
        pedidos_sin_facturar = mesa.pedidos.filter(factura__isnull=True)

        if pedidos_sin_facturar.exists():
            return redirect('tables:mesas_lista')

        pedidos_facturados = mesa.pedidos.filter(factura__isnull=False)
        if pedidos_facturados.exists():
            pedidos_facturados.update(mesa=None)

        response = super().post(request, *args, **kwargs)

        mensaje = f"Mesa '{mesa_nombre}' eliminada correctamente."
        notificar_usuario(request.user, mensaje)
        
        return response

@permission_required('tables', 'editar')
def cambiar_estado(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    nuevo_estado = request.POST.get('estado')

    estados_validos = ['disponible', 'ocupada', 'reservada', 'fuera de servicio']
    if nuevo_estado in estados_validos:
        mesa.estado = nuevo_estado
        mesa.save()

        mensaje = f"La mesa '{mesa.nombre}' ha cambiado su estado a '{nuevo_estado}'."
        notificar_usuario(request.user, mensaje)

    return redirect('tables:mesas_lista')

def ver_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'pedidos/factura.html', {'factura': factura})

def confirmar_eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    pedidos = mesa.pedidos.all()
    pedidos_con_factura = [p for p in pedidos if hasattr(p, 'factura')]
    pedidos_sin_factura = [p for p in pedidos if not hasattr(p, 'factura')]
    
    context = {
        'mesa': mesa,
        'puede_eliminar': not pedidos_sin_factura,
        'pedidos_con_factura': pedidos_con_factura,
        'pedidos_sin_factura': pedidos_sin_factura,
        'total_pedidos': len(pedidos)
    }
    
    return render(request, 'mesas/confirmar_eliminar.html', context)

@require_POST
def liberar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    pedidos_sin_factura = mesa.pedidos.filter(factura__isnull=True)
    count = pedidos_sin_factura.count()
    
    if pedidos_sin_factura.exists():
        pedidos_sin_factura.delete()
        
        mesa.estado = 'disponible'
        mesa.save()
        
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        mensaje = f"Mesa '{mesa.nombre}' liberada. Se eliminaron {count} pedido(s) sin facturar."
        for user in staff_users:
            notificar_usuario(user, mensaje)
            
    return redirect('tables:mesas_lista')
