from django.shortcuts import render, redirect, get_object_or_404
<<<<<<< HEAD
from django.db.models.deletion import ProtectedError
from .models import Mesa, Factura, Pedido
from .forms import MesaForm
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from notifications.utils import notificar_usuario
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef

from django.utils.decorators import method_decorator
from roles.decorators import permission_required

@method_decorator(permission_required('tables', 'ver'), name='dispatch')
class MesaListView(ListView):
    model = Mesa
    template_name = 'mesas/lista_mesas_native.html'
    context_object_name = 'mesas'

    def get_queryset(self):
        pedidos_en_proceso = Pedido.objects.filter(
            mesa=OuterRef('pk'),
            estado='en_proceso'
        )
        queryset = Mesa.objects.annotate(
            tiene_pedidos_en_proceso=Exists(pedidos_en_proceso)
        ).order_by('nombre')
        return queryset

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
    template_name = 'mesas/crear_mesa.html' # Usando crear_mesa.html temporalmente hasta que editar_mesa.html sea creado o definido.
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
            from django.contrib import messages
            messages.error(request, f"No se puede eliminar la mesa '{mesa_nombre}' porque tiene pedidos sin facturar.")
            return redirect('tables:mesas_lista')

        pedidos_facturados = mesa.pedidos.filter(factura__isnull=False)
        if pedidos_facturados.exists():
            pedidos_facturados.update(mesa=None)

        response = super().post(request, *args, **kwargs)

        mensaje = f"Mesa '{mesa_nombre}' eliminada correctamente."
        notificar_usuario(request.user, mensaje)
        
        return response

@method_decorator(permission_required('tables', 'editar'), name='dispatch')
class CambiarEstadoMesaView(View):
    def post(self, request, mesa_id):
        mesa = get_object_or_404(Mesa, id=mesa_id)
        nuevo_estado = request.POST.get('estado')

        estados_validos = ['disponible', 'ocupada', 'reservada', 'fuera de servicio']
        if nuevo_estado in estados_validos:
            if nuevo_estado in ['disponible', 'reservada'] and mesa.pedidos.filter(estado='en_proceso').exists():
                messages.error(request, f"No se puede cambiar el estado de la mesa '{mesa.nombre}' a '{nuevo_estado}' porque tiene pedidos activos.")
                return redirect('tables:mesas_lista')
            
            mesa.estado = nuevo_estado
            mesa.save()

            mensaje = f"La mesa '{mesa.nombre}' ha cambiado su estado a '{nuevo_estado}'."
            notificar_usuario(request.user, mensaje)

        return redirect('tables:mesas_lista')

class VerFacturaView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'pedidos/factura.html'
    context_object_name = 'factura'
    pk_url_kwarg = 'factura_id'

class ConfirmarEliminarMesaView(LoginRequiredMixin, View):
    def get(self, request, mesa_id):
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        pedidos = mesa.pedidos.all()
        pedidos_con_factura = []
        pedidos_sin_factura = []
        for p in pedidos:
            try:
                if hasattr(p, 'factura') and p.factura:
                    pedidos_con_factura.append(p)
                else:
                    pedidos_sin_factura.append(p)
            except Exception as e:
                print(f"Error al verificar factura para pedido {p.id}: {e}")
                pedidos_sin_factura.append(p)
        
        context = {
            'mesa': mesa,
            'puede_eliminar': not pedidos_sin_factura,
            'pedidos_con_factura': pedidos_con_factura,
            'pedidos_sin_factura': pedidos_sin_factura,
            'total_pedidos': len(pedidos)
        }
        
        return render(request, 'mesas/confirmar_eliminar.html', context)

class LiberarMesaView(LoginRequiredMixin, View):
    def post(self, request, mesa_id):
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
=======
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
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
