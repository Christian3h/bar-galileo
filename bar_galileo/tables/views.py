from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import Cast
from .models import Mesa
from .forms import MesaForm
from django.views.decorators.http import require_POST
from django.contrib import messages

def lista_mesas(request):
    mesas = Mesa.objects.all().order_by('nombre')
    return render(request, 'mesas/lista_mesas.html', {'mesas': mesas})

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
                return redirect('lista_mesas')
        else:
            messages.error(request, "Esta Mesa ya está registrada.")
    else:
        form = MesaForm()

    return render(request, 'mesas/crear_mesa.html', {'form': form})

def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.delete()
    messages.success(request, "Mesa eliminada correctamente.")
    return redirect('lista_mesas')

def cambiar_estado(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(Mesa.ESTADOS):
        mesa.estado = nuevo_estado
        mesa.save()
        messages.success(request, f"Estado de la mesa actualizado a '{nuevo_estado}'.")
    else:
        messages.error(request, "Estado inválido.")

    return redirect('lista_mesas')

@require_POST
def editar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    nuevo_nombre = request.POST.get('nombre', '').strip()
    nueva_desc = request.POST.get('descripcion', '').strip()

    # Validar nombre vacío
    if not nuevo_nombre:
        messages.error(request, "El nombre de la mesa no puede estar vacío.")
        return redirect('lista_mesas')

    # Validar nombre duplicado (excepto la misma mesa)
    if Mesa.objects.exclude(id=mesa_id).filter(nombre__iexact=nuevo_nombre).exists():
        messages.error(request, f"Ya existe una mesa con el nombre '{nuevo_nombre}'.")
        return redirect('lista_mesas')

    mesa.nombre = nuevo_nombre
    mesa.descripcion = nueva_desc
    mesa.save()
    messages.success(request, "Mesa actualizada correctamente.")
    return redirect('lista_mesas')
