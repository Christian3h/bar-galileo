from django.core.management.base import BaseCommand
from nominas.models import Empleado, Pago, Bonificacion
from roles.models import Role, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Carga empleados de ejemplo con rol Empleado, pagos y bonificaciones.'

    def handle(self, *args, **options):
        # Datos de ejemplo
        empleados_data = [
            {
                'nombre': 'Juan Pérez',
                'cargo': 'Mesero',
                'salario': 1500000,
                'fecha_contratacion': timezone.now().date().replace(year=2022, month=3, day=15),
                'estado': 'activo',
                'tipo_contrato': 'tiempo_completo',
                'email': 'juan.perez@ejemplo.com',
                'telefono': '+573001234567',
                'direccion': 'Calle 123 #45-67, Bogotá',
            },
            {
                'nombre': 'Ana Gómez',
                'cargo': 'Cocinera',
                'salario': 1800000,
                'fecha_contratacion': timezone.now().date().replace(year=2021, month=7, day=10),
                'estado': 'activo',
                'tipo_contrato': 'tiempo_completo',
                'email': 'ana.gomez@ejemplo.com',
                'telefono': '+573002345678',
                'direccion': 'Cra 45 #67-89, Medellín',
            },
            {
                'nombre': 'Carlos Ruiz',
                'cargo': 'Bartender',
                'salario': 1600000,
                'fecha_contratacion': timezone.now().date().replace(year=2023, month=1, day=5),
                'estado': 'activo',
                'tipo_contrato': 'medio_tiempo',
                'email': 'carlos.ruiz@ejemplo.com',
                'telefono': '+573003456789',
                'direccion': 'Av. Siempre Viva 742, Cali',
            },
        ]

        rol_empleado = Role.objects.filter(nombre__iexact='Empleado').first()
        if not rol_empleado:
            self.stdout.write(self.style.ERROR('No existe el rol Empleado.'))
            return

        for data in empleados_data:
            # Crear usuario base
            username = data['email'].split('@')[0]
            user, _ = User.objects.get_or_create(username=username, defaults={
                'email': data['email'],
                'first_name': data['nombre'].split()[0],
                'last_name': ' '.join(data['nombre'].split()[1:]),
            })
            # Asignar perfil y rol
            UserProfile.objects.get_or_create(user=user, defaults={'rol': rol_empleado})
            # Crear empleado
            empleado, created = Empleado.objects.get_or_create(
                nombre=data['nombre'],
                cargo=data['cargo'],
                salario=data['salario'],
                fecha_contratacion=data['fecha_contratacion'],
                estado=data['estado'],
                tipo_contrato=data['tipo_contrato'],
                email=data['email'],
                telefono=data['telefono'],
                direccion=data['direccion'],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Empleado creado: {empleado}"))
            else:
                self.stdout.write(self.style.WARNING(f"Empleado ya existe: {empleado}"))
            # Crear pagos de ejemplo
            for mes in range(1, 4):
                Pago.objects.get_or_create(
                    empleado=empleado,
                    fecha_pago=timezone.now().date().replace(month=mes, day=5),
                    monto=empleado.salario,
                    tipo='salario',
                    descripcion=f'Salario correspondiente a mes {mes}'
                )
            # Crear bonificación de ejemplo
            Bonificacion.objects.get_or_create(
                empleado=empleado,
                nombre='Bono puntualidad',
                monto=random.randint(50000, 100000),
                recurrente=False,
                fecha_inicio=timezone.now().date().replace(month=2, day=1)
            )
        self.stdout.write(self.style.SUCCESS('Empleados de ejemplo cargados correctamente.'))
