"""
Script de diagnóstico para problemas de actualización de base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.db import connection
from django.conf import settings

print("=" * 70)
print("DIAGNÓSTICO DE BASE DE DATOS")
print("=" * 70)

# 1. Verificar configuración
print("\n1. Configuración actual:")
print(f"   Motor: {connection.settings_dict['ENGINE']}")
print(f"   Base de datos: {connection.settings_dict['NAME']}")
print(f"   Usuario: {connection.settings_dict.get('USER', 'N/A')}")
print(f"   Host: {connection.settings_dict.get('HOST', 'N/A')}")

# 2. Verificar variable USE_MYSQL
use_mysql = os.getenv('USE_MYSQL', 'False')
print(f"\n2. Variable USE_MYSQL: {use_mysql}")

# 3. Probar escritura
print("\n3. Probando escritura en la base de datos...")
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Crear usuario de prueba
    test_user = User.objects.create_user(
        username=f'test_user_{os.getpid()}',
        password='testpass123',
        email='test@test.com'
    )
    print(f"   ✓ Usuario de prueba creado: {test_user.username}")
    
    # Leer el usuario
    retrieved = User.objects.get(username=test_user.username)
    print(f"   ✓ Usuario recuperado: {retrieved.username}")
    
    # Eliminar usuario de prueba
    test_user.delete()
    print(f"   ✓ Usuario de prueba eliminado")
    
    print("\n   ✅ La escritura en la base de datos funciona correctamente")
    
except Exception as e:
    print(f"\n   ✗ Error al probar escritura: {e}")

# 4. Verificar transacciones
print("\n4. Configuración de transacciones:")
print(f"   ATOMIC_REQUESTS: {connection.settings_dict.get('ATOMIC_REQUESTS', False)}")
print(f"   AUTOCOMMIT: {connection.get_autocommit()}")

# 5. Verificar migraciones pendientes
print("\n5. Verificando migraciones pendientes...")
from django.db.migrations.executor import MigrationExecutor
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

if plan:
    print(f"   ⚠ Hay {len(plan)} migraciones pendientes:")
    for migration, backwards in plan:
        print(f"     - {migration.app_label}.{migration.name}")
else:
    print("   ✓ No hay migraciones pendientes")

# 6. Verificar permisos
print("\n6. Verificando permisos del usuario de base de datos...")
try:
    with connection.cursor() as cursor:
        if 'mysql' in connection.settings_dict['ENGINE']:
            cursor.execute("""
                SHOW GRANTS FOR CURRENT_USER()
            """)
            grants = cursor.fetchall()
            print("   Permisos actuales:")
            for grant in grants:
                print(f"     {grant[0]}")
except Exception as e:
    print(f"   ⚠ No se pudieron verificar permisos: {e}")

print("\n" + "=" * 70)
print("FIN DEL DIAGNÓSTICO")
print("=" * 70)
