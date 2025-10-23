"""
Script para verificar usuarios y roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from roles.models import UserProfile, Role


class Command(BaseCommand):
    help = 'Verifica los usuarios y sus roles asignados'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Verificando usuarios y roles...'))
        self.stdout.write('')
        
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No hay usuarios en el sistema'))
            return
        
        for user in users:
            if hasattr(user, 'userprofile') and user.userprofile.rol:
                rol_nombre = user.userprofile.rol.nombre
                self.stdout.write(f'✓ Usuario: {user.username} | Rol: {rol_nombre}')
            else:
                self.stdout.write(f'⚠️  Usuario: {user.username} | Rol: Sin rol asignado')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Verificación completada'))
