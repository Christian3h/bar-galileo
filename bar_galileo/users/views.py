from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from roles.models import UserProfile, Role
from roles.forms import UserProfileForm
from django.db.models import Case, When, Value, IntegerField

from notifications.utils import notificar_usuario

def user_list(request):
    users = User.objects.all().select_related('userprofile')
    # Ordenar: usuarios con rol al final
    users = users.annotate(
        is_user_role=Case(
            When(userprofile__rol__nombre='usuario', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_user_role', 'username')
    roles = Role.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        rol_id = request.POST.get('rol_id')
        user = User.objects.get(id=user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.rol_id = rol_id
        profile.save()
        
        rol = Role.objects.get(id=rol_id)
        mensaje = f"El rol del usuario '{user.username}' ha sido actualizado a '{rol.name}'."
        notificar_usuario(request.user, mensaje)

        return redirect('users:user_list')
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})


# Vista para el panel de usuario
from django.contrib.auth.decorators import login_required

@login_required
def panel_usuario(request):
    # Aquí puedes obtener datos reales del usuario
    user = request.user
    # Ejemplo de datos, reemplaza por datos reales de tu modelo
    datos = {
        'nombre': user.get_full_name() or user.username,
        'cedula': getattr(user, 'cedula', '1.234.567.890'),
        'telefono': getattr(user, 'telefono', '+57 312 456 7890'),
        'email': user.email,
        'direccion': getattr(user, 'direccion', 'Cra 15 #85-23, Bogotá'),
        'cliente_desde': 'Enero 2023',
        'emergencia': {
            'nombre': 'María Elena Mendoza',
            'relacion': 'Esposa',
            'telefono': '+57 314 396 2770',
            'telefono_alt': '+57 314 396 2770',
            'sangre': 'O+ Positivo',
            'alergias': 'Mariscos, Cacahuetes',
        },
        'cuenta_actual': {
            'total': 45750,
            'items': [
                {'nombre': 'Cervezas (3)', 'precio': 18000},
                {'nombre': 'Alitas BBQ', 'precio': 15500},
                {'nombre': 'Nachos Supreme', 'precio': 12250},
            ]
        },
        'historial_mensual': {
            'mes': 'Julio',
            'total': 450000,
            'barras': [120000, 160000, 90000, 180000, 140000],
        }
    }
    return render(request, 'users/panel de usuario.html', {'datos': datos})
