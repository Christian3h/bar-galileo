from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, Count
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from .models import Empleado, Pago, Bonificacion
from .forms import EmpleadoForm, PagoForm, BonificacionForm, EmpleadoFilterForm

class EmpleadoListView(ListView):
    model = Empleado
    template_name = "nominas/empleado_list.html"
    context_object_name = "empleados"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estado si está en el request
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        # Filtrar por tipo_contrato si está en el request
        tipo_contrato = self.request.GET.get('tipo_contrato')
        if tipo_contrato:
            queryset = queryset.filter(tipo_contrato=tipo_contrato)
            
        # Buscar por nombre o cargo
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | 
                Q(cargo__icontains=busqueda)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_empleados'] = Empleado.objects.count()
        context['total_activos'] = Empleado.objects.filter(estado='activo').count()
        context['total_inactivos'] = Empleado.objects.filter(estado='inactivo').count()
        
        # Formulario de filtros
        context['filter_form'] = EmpleadoFilterForm(self.request.GET or None)
        
        # Sumatoria de salarios mensuales
        context['total_salarios'] = Empleado.objects.filter(estado='activo').aggregate(
            total=Sum('salario')
        )['total'] or 0
        
        return context

class EmpleadoCreateView(SuccessMessageMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "nominas/empleado_form.html"
    success_url = reverse_lazy("nominas:empleado_list")
    success_message = "Empleado creado exitosamente"

class EmpleadoUpdateView(SuccessMessageMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "nominas/empleado_form.html"
    success_url = reverse_lazy("nominas:empleado_list")
    success_message = "Datos del empleado actualizados exitosamente"

class EmpleadoDeleteView(SuccessMessageMixin, DeleteView):
    model = Empleado
    template_name = "nominas/empleado_confirm_delete.html"
    success_url = reverse_lazy("nominas:empleado_list")
    success_message = "Empleado eliminado exitosamente"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EmpleadoDeleteView, self).delete(request, *args, **kwargs)

class EmpleadoDetailView(DetailView):
    model = Empleado
    template_name = "nominas/empleado_detail.html"
    context_object_name = "empleado"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.get_object()
        
        # Historial de pagos
        context['pagos'] = Pago.objects.filter(empleado=empleado).order_by('-fecha_pago')
        
        # Bonificaciones activas
        context['bonificaciones'] = Bonificacion.objects.filter(
            empleado=empleado
        ).order_by('-fecha_inicio')
        
        # Total pagado al empleado
        context['total_pagado'] = Pago.objects.filter(empleado=empleado).aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        # Formularios para agregar pagos y bonificaciones
        context['pago_form'] = PagoForm(initial={'empleado': empleado})
        context['bonificacion_form'] = BonificacionForm(initial={'empleado': empleado})
        
        return context

class PagoCreateView(SuccessMessageMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = "nominas/pago_form.html"
    success_message = "Pago registrado exitosamente"
    
    def get_success_url(self):
        return reverse_lazy("nominas:empleado_detail", kwargs={'pk': self.object.empleado.pk})

class PagoListView(ListView):
    model = Pago
    template_name = "nominas/pago_list.html"
    context_object_name = "pagos"
    ordering = ['-fecha_pago']

class BonificacionCreateView(SuccessMessageMixin, CreateView):
    model = Bonificacion
    form_class = BonificacionForm
    template_name = "nominas/bonificacion_form.html"
    success_message = "Bonificación agregada exitosamente"
    
    def get_success_url(self):
        return reverse_lazy("nominas:empleado_detail", kwargs={'pk': self.object.empleado.pk})

# Vistas para crear pagos y bonificaciones desde la vista de detalle
def agregar_pago(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    if request.method == "POST":
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.empleado = empleado
            pago.save()
            messages.success(request, "Pago registrado exitosamente")
            return redirect('nominas:empleado_detail', pk=empleado.pk)
    else:
        form = PagoForm(initial={'empleado': empleado})
        
    return render(request, 'nominas/pago_form.html', {
        'form': form,
        'empleado': empleado
    })

def agregar_bonificacion(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    if request.method == "POST":
        form = BonificacionForm(request.POST)
        if form.is_valid():
            bonificacion = form.save(commit=False)
            bonificacion.empleado = empleado
            bonificacion.save()
            messages.success(request, "Bonificación agregada exitosamente")
            return redirect('nominas:empleado_detail', pk=empleado.pk)
    else:
        form = BonificacionForm(initial={'empleado': empleado})
        
    return render(request, 'nominas/bonificacion_form.html', {
        'form': form,
        'empleado': empleado
    })
