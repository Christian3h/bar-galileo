from django.views import View
<<<<<<< HEAD
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from roles.decorators import permission_required
=======
from django.views.generic import ListView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a

from .models import Role, RolePermission, Module, Action
from .forms import RoleForm
from django import template
register = template.Library()

<<<<<<< HEAD
@method_decorator(permission_required('roles', 'ver'), name='dispatch')
=======
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
class RolListView(ListView):
    model = Role
    template_name = 'roles/rol_list.html'
    context_object_name = 'roles'

<<<<<<< HEAD
from notifications.utils import notificar_usuario

@method_decorator(permission_required('roles', 'crear'), name='dispatch')
class RolCreateView(LoginRequiredMixin, CreateView):
=======
class RolCreateView(CreateView):
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
    model = Role
    form_class = RoleForm
    template_name = 'roles/rol_form.html'

    def form_valid(self, form):
        role = form.save()
<<<<<<< HEAD
        mensaje = f"Se ha creado el nuevo rol: '{role.nombre}'."
        notificar_usuario(self.request.user, mensaje)
        return redirect('roles:rol_permisos', role.id)

@method_decorator(permission_required('roles', 'editar'), name='dispatch')
class RolUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/rol_form.html'
    success_url = reverse_lazy('roles:rol_list')

    def form_valid(self, form):
        role = form.save()
        mensaje = f"El rol '{role.nombre}' ha sido actualizado."
        notificar_usuario(self.request.user, mensaje)
        return redirect(self.success_url)

@method_decorator(permission_required('roles', 'eliminar'), name='dispatch')
class RolDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    template_name = 'roles/rol_confirm_delete.html'
    success_url = reverse_lazy('roles:rol_list')

    def form_valid(self, form):
        role = self.get_object()
        mensaje = f"El rol '{role.nombre}' ha sido eliminado."
        notificar_usuario(self.request.user, mensaje)
        return super().form_valid(form)

@method_decorator(permission_required('roles', 'editar'), name='dispatch')
class RolPermisosView(LoginRequiredMixin, View):
=======
        return redirect('roles:rol_permisos', role.id)


class RolPermisosView(View):
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
    def get(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        modulos = Module.objects.all()
        acciones = Action.objects.all()
        permisos = RolePermission.objects.filter(rol=role)
        
        return render(request, 'roles/rol_permisos.html', {
            'role': role,
            'modulos': modulos,
            'acciones': acciones,
            'permisos': permisos,  # Pasamos los permisos directamente
        })

    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        modulos = Module.objects.all()
        acciones = Action.objects.all()

        # Limpiar permisos existentes
        RolePermission.objects.filter(rol=role).delete()
        
        # Crear permisos nuevos marcados
        for modulo in modulos:
            for accion in acciones:
                if request.POST.get(f"perm_{modulo.id}_{accion.id}"):
                    RolePermission.objects.create(rol=role, modulo=modulo, accion=accion)

<<<<<<< HEAD
        mensaje = f"Los permisos para el rol '{role.nombre}' han sido actualizados."
        notificar_usuario(request.user, mensaje)
=======
        messages.success(request, 'Permisos actualizados correctamente.')
>>>>>>> f550aac13c0202e2f4652738b7d329dd256a899a
        return redirect('roles:rol_list')