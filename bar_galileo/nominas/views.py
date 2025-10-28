from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, Count
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from roles.models import Role, UserProfile
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

    def form_valid(self, form):
        # Obtener el rol seleccionado
        rol_cargo = form.cleaned_data.get('rol_cargo')

        # Si se especificó un rol, usarlo como cargo
        if rol_cargo:
            form.instance.cargo = rol_cargo.nombre

        # Guardar el empleado primero
        response = super().form_valid(form)

        opcion_usuario = form.cleaned_data.get('opcion_usuario')

        if opcion_usuario == 'usuario_existente':
            # Asignar usuario existente
            usuario_seleccionado = form.cleaned_data.get('usuario_existente')
            if usuario_seleccionado:
                self.object.user = usuario_seleccionado
                self.object.save()

                # Asignar o actualizar rol
                if rol_cargo:
                    UserProfile.objects.update_or_create(
                        user=usuario_seleccionado,
                        defaults={'rol': rol_cargo}
                    )
                elif not hasattr(usuario_seleccionado, 'userprofile') or not usuario_seleccionado.userprofile.rol:
                    # Si no se especificó rol, usar "Empleado" por defecto
                    rol_empleado = Role.objects.filter(nombre__iexact='Empleado').first()
                    if rol_empleado:
                        UserProfile.objects.update_or_create(
                            user=usuario_seleccionado,
                            defaults={'rol': rol_empleado}
                        )

                messages.success(self.request, f"Usuario '{usuario_seleccionado.username}' vinculado al empleado")

        elif opcion_usuario == 'usuario_nuevo':
            # Crear nuevo usuario
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email_usuario = form.cleaned_data.get('email_usuario') or self.object.email

            if username and password:
                # Crear el usuario
                nuevo_usuario = User.objects.create_user(
                    username=username,
                    email=email_usuario,
                    password=password,
                    first_name=self.object.nombre.split()[0] if self.object.nombre else '',
                    last_name=' '.join(self.object.nombre.split()[1:]) if len(self.object.nombre.split()) > 1 else ''
                )

                # Asignar usuario al empleado
                self.object.user = nuevo_usuario
                self.object.save()

                # Asignar rol
                if rol_cargo:
                    UserProfile.objects.create(user=nuevo_usuario, rol=rol_cargo)
                else:
                    # Si no se especificó rol, usar "Empleado" por defecto
                    rol_empleado = Role.objects.filter(nombre__iexact='Empleado').first()
                    if rol_empleado:
                        UserProfile.objects.create(user=nuevo_usuario, rol=rol_empleado)

                messages.success(self.request, f"Usuario '{username}' creado y vinculado al empleado")

        return response

class EmpleadoUpdateView(SuccessMessageMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "nominas/empleado_form.html"
    success_url = reverse_lazy("nominas:empleado_list")
    success_message = "Datos del empleado actualizados exitosamente"

    def form_valid(self, form):
        # Obtener el rol seleccionado
        rol_cargo = form.cleaned_data.get('rol_cargo')

        # Si se especificó un rol, usarlo como cargo
        if rol_cargo:
            form.instance.cargo = rol_cargo.nombre

            # Actualizar el rol del usuario si existe
            if self.object.user:
                UserProfile.objects.update_or_create(
                    user=self.object.user,
                    defaults={'rol': rol_cargo}
                )

        # Solo permitir vincular usuario si no tiene uno asignado
        if not self.object.user:
            opcion_usuario = form.cleaned_data.get('opcion_usuario')

            if opcion_usuario == 'usuario_existente':
                # Asignar usuario existente
                usuario_seleccionado = form.cleaned_data.get('usuario_existente')
                if usuario_seleccionado:
                    self.object.user = usuario_seleccionado

                    # Asignar o actualizar rol
                    if rol_cargo:
                        UserProfile.objects.update_or_create(
                            user=usuario_seleccionado,
                            defaults={'rol': rol_cargo}
                        )
                    elif not hasattr(usuario_seleccionado, 'userprofile') or not usuario_seleccionado.userprofile.rol:
                        rol_empleado = Role.objects.filter(nombre__iexact='Empleado').first()
                        if rol_empleado:
                            UserProfile.objects.update_or_create(
                                user=usuario_seleccionado,
                                defaults={'rol': rol_empleado}
                            )

                    messages.success(self.request, f"Usuario '{usuario_seleccionado.username}' vinculado al empleado")

            elif opcion_usuario == 'usuario_nuevo':
                # Crear nuevo usuario
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                email_usuario = form.cleaned_data.get('email_usuario') or self.object.email

                if username and password:
                    # Crear el usuario
                    nuevo_usuario = User.objects.create_user(
                        username=username,
                        email=email_usuario,
                        password=password,
                        first_name=self.object.nombre.split()[0] if self.object.nombre else '',
                        last_name=' '.join(self.object.nombre.split()[1:]) if len(self.object.nombre.split()) > 1 else ''
                    )

                    # Asignar usuario al empleado
                    self.object.user = nuevo_usuario

                    # Asignar rol
                    if rol_cargo:
                        UserProfile.objects.create(user=nuevo_usuario, rol=rol_cargo)
                    else:
                        rol_empleado = Role.objects.filter(nombre__iexact='Empleado').first()
                        if rol_empleado:
                            UserProfile.objects.create(user=nuevo_usuario, rol=rol_empleado)

                    messages.success(self.request, f"Usuario '{username}' creado y vinculado al empleado")

        return super().form_valid(form)

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

    def form_valid(self, form):
        # Asignar el usuario que crea el pago
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)

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

    def form_valid(self, form):
        # Asignar el usuario que crea la bonificación
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)

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
            pago.created_by = request.user
            pago.modified_by = request.user
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
            bonificacion.created_by = request.user
            bonificacion.modified_by = request.user
            bonificacion.save()
            messages.success(request, "Bonificación agregada exitosamente")
            return redirect('nominas:empleado_detail', pk=empleado.pk)
    else:
        form = BonificacionForm(initial={'empleado': empleado})

    return render(request, 'nominas/bonificacion_form.html', {
        'form': form,
        'empleado': empleado
    })

# Vista API para buscar usuarios disponibles
def buscar_usuarios_disponibles(request):
    """
    API endpoint para buscar usuarios sin empleado asignado
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    # Buscar usuarios sin empleado asignado
    usuarios = User.objects.filter(
        empleado__isnull=True
    ).filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]  # Limitar a 10 resultados

    resultados = []
    for usuario in usuarios:
        rol_nombre = ""
        if hasattr(usuario, 'userprofile') and usuario.userprofile.rol:
            rol_nombre = usuario.userprofile.rol.nombre

        resultados.append({
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'nombre_completo': f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username,
            'rol': rol_nombre,
            'text': f"{usuario.username} - {usuario.email}" + (f" ({rol_nombre})" if rol_nombre else "")
        })

    return JsonResponse({'results': resultados})
