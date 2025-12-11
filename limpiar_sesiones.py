"""
Script para limpiar sesiones y caché
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone

print("=" * 70)
print("LIMPIEZA DE SESIONES")
print("=" * 70)

# Contar sesiones antes
total_before = Session.objects.count()
print(f"\n1. Sesiones totales antes de limpiar: {total_before}")

# Eliminar sesiones expiradas
expired_count = 0
for session in Session.objects.all():
    if session.expire_date < timezone.now():
        session.delete()
        expired_count += 1

print(f"   ✓ Sesiones expiradas eliminadas: {expired_count}")

# Contar sesiones después
total_after = Session.objects.count()
print(f"   ✓ Sesiones activas restantes: {total_after}")

print("\n2. Recomendaciones:")
print("   - Cierra todas las pestañas del navegador")
print("   - Limpia el caché del navegador (Ctrl+Shift+Delete)")
print("   - Vuelve a iniciar sesión")
print("   - Asegúrate de que solo hay un servidor Django corriendo")

print("\n" + "=" * 70)
print("✓ LIMPIEZA COMPLETADA")
print("=" * 70)
