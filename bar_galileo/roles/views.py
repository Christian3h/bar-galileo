from django.shortcuts import render, redirect, get_object_or_404
from .models import Role, RolePermission, Module, Action
from .forms import RoleForm, RolePermissionFormSet
from django.urls import reverse
from django.contrib import messages

def rol_list(request):
    roles = Role.objects.all()
    return render(request, 'roles/rol_list.html', {'roles': roles})

def rol_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            return redirect('roles:rol_permisos', role.id)
    else:
        form = RoleForm()
    return render(request, 'roles/rol_form.html', {'form': form})

def rol_permisos(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    modulos = Module.objects.all()
    acciones = Action.objects.all()
    permisos = RolePermission.objects.filter(rol=role)
    permisos_dict = {f'{p.modulo_id}_{p.accion_id}': p for p in permisos}

    if request.method == 'POST':
        # Limpiar permisos existentes
        RolePermission.objects.filter(rol=role).delete()
        for modulo in modulos:
            for accion in acciones:
                if request.POST.get(f"perm_{modulo.id}_{accion.id}"):
                    RolePermission.objects.create(rol=role, modulo=modulo, accion=accion)
        messages.success(request, 'Permisos actualizados')
        return redirect('roles:rol_list')

    return render(request, 'roles/rol_permisos.html', {
        'role': role,
        'modulos': modulos,
        'acciones': acciones,
        'permisos_dict': permisos_dict,
    })
