"""
Script para probar transacciones y persistencia de datos
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth import get_user_model

print("=" * 70)
print("PRUEBA DE PERSISTENCIA DE DATOS")
print("=" * 70)

User = get_user_model()

# Test 1: Crear y verificar persistencia
print("\n1. Prueba de creación y lectura inmediata:")
try:
    test_username = f'persistence_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Crear usuario
    user = User.objects.create_user(
        username=test_username,
        password='testpass123',
        email=f'{test_username}@test.com'
    )
    print(f"   ✓ Usuario creado: {user.username} (ID: {user.id})")
    
    # Verificar en la misma sesión
    user_check = User.objects.get(username=test_username)
    print(f"   ✓ Usuario encontrado en misma sesión: {user_check.username}")
    
    # Verificar con query directa SQL
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT username, email FROM auth_user WHERE username = %s",
            [test_username]
        )
        result = cursor.fetchone()
        if result:
            print(f"   ✓ Usuario encontrado con SQL directo: {result[0]}")
        else:
            print(f"   ✗ Usuario NO encontrado con SQL directo")
    
    # Limpiar
    user.delete()
    print(f"   ✓ Usuario de prueba eliminado")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Verificar modo de aislamiento
print("\n2. Verificando configuración de transacciones:")
with connection.cursor() as cursor:
    cursor.execute("SELECT @@transaction_isolation")
    isolation = cursor.fetchone()[0]
    print(f"   Nivel de aislamiento: {isolation}")
    
    cursor.execute("SELECT @@autocommit")
    autocommit = cursor.fetchone()[0]
    print(f"   Autocommit: {autocommit}")

# Test 3: Verificar que los cambios se persisten después de commit
print("\n3. Prueba de transacción explícita:")
try:
    test_username2 = f'transaction_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    with transaction.atomic():
        user = User.objects.create_user(
            username=test_username2,
            password='testpass123',
            email=f'{test_username2}@test.com'
        )
        print(f"   ✓ Usuario creado en transacción: {user.username}")
    
    # Verificar después del commit
    user_after = User.objects.get(username=test_username2)
    print(f"   ✓ Usuario persiste después de commit: {user_after.username}")
    
    # Limpiar
    user_after.delete()
    print(f"   ✓ Usuario limpiado")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Verificar tabla de sesiones
print("\n4. Verificando tabla de sesiones:")
try:
    from django.contrib.sessions.models import Session
    session_count = Session.objects.count()
    print(f"   ✓ Sesiones activas: {session_count}")
except Exception as e:
    print(f"   ⚠ Error al verificar sesiones: {e}")

# Test 5: Información de conexión
print("\n5. Información de conexión:")
print(f"   Base de datos: {connection.settings_dict['NAME']}")
print(f"   Motor: {connection.settings_dict['ENGINE']}")
print(f"   Autocommit activo: {connection.get_autocommit()}")

print("\n" + "=" * 70)
print("CONCLUSIÓN")
print("=" * 70)
print("""
Si todas las pruebas anteriores pasaron correctamente, significa que:
✓ MySQL está funcionando correctamente
✓ Las transacciones se están guardando
✓ Los datos persisten después del commit

Si los cambios no aparecen en la página, puede ser por:
1. Caché del navegador (Ctrl+Shift+R para refrescar)
2. Sesiones antiguas (cerrar sesión y volver a entrar)
3. El código no está guardando los cambios correctamente
4. Hay múltiples instancias del servidor corriendo

Soluciones:
- Reinicia el servidor: python manage.py runserver
- Limpia caché del navegador
- Verifica que solo haya una instancia del servidor
- Revisa los logs del servidor cuando hagas un cambio
""")
