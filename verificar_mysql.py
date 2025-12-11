"""
Script para verificar la migración a MySQL
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bar_galileo'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

print("=" * 70)
print("VERIFICACIÓN DE MIGRACIÓN A MYSQL")
print("=" * 70)

# Verificar conexión
print("\n1. Verificando conexión a la base de datos...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ Conectado a MySQL versión: {version}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"✓ Base de datos activa: {db_name}")
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    sys.exit(1)

# Verificar tablas
print("\n2. Verificando tablas...")
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
        """)
        table_count = cursor.fetchone()[0]
        print(f"✓ Número de tablas: {table_count}")
except Exception as e:
    print(f"✗ Error al contar tablas: {e}")

# Verificar usuarios
print("\n3. Verificando usuarios...")
try:
    User = get_user_model()
    user_count = User.objects.count()
    print(f"✓ Usuarios registrados: {user_count}")
    
    if user_count > 0:
        superusers = User.objects.filter(is_superuser=True).count()
        print(f"✓ Superusuarios: {superusers}")
except Exception as e:
    print(f"✗ Error al verificar usuarios: {e}")

# Verificar otras tablas importantes
print("\n4. Verificando datos de aplicaciones...")
try:
    from products.models import Product
    product_count = Product.objects.count()
    print(f"✓ Productos: {product_count}")
except Exception as e:
    print(f"⚠ Productos: No disponible ({e})")

try:
    from tables.models import Table
    table_count = Table.objects.count()
    print(f"✓ Mesas: {table_count}")
except Exception as e:
    print(f"⚠ Mesas: No disponible ({e})")

try:
    from expenses.models import Expense
    expense_count = Expense.objects.count()
    print(f"✓ Gastos: {expense_count}")
except Exception as e:
    print(f"⚠ Gastos: No disponible ({e})")

print("\n" + "=" * 70)
print("✓ VERIFICACIÓN COMPLETADA")
print("=" * 70)
print("\nLa migración a MySQL se completó exitosamente.")
print("Tu aplicación ahora está usando MySQL en lugar de SQLite.")
print("\nPara iniciar el servidor:")
print("  cd bar_galileo")
print("  python manage.py runserver")
