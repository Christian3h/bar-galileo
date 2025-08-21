from django.views import View
from django.views.generic import ListView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from .models import Role, RolePermission, Module, Action
from .forms import RoleForm
from django import template
register = template.Library()

class RolListView(ListView):
    model = Role
    template_name = 'roles/rol_list.html'
    context_object_name = 'roles'

from notifications.utils import notificar_usuario

class RolCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'roles/rol_form.html'

    def form_valid(self, form):
        role = form.save()
        mensaje = f"Se ha creado el nuevo rol: '{role.name}'."
        notificar_usuario(self.request.user, mensaje)
        return redirect('roles:rol_permisos', role.id)


class RolPermisosView(View):
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

        mensaje = f"Los permisos para el rol '{role.nombre}' han sido actualizados."
        notificar_usuario(request.user, mensaje)
        return redirect('roles:rol_list')