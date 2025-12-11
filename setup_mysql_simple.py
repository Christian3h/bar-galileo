"""
Script simplificado para importar datos usando comando mysql directamente
Requiere que la BD y usuario ya estén creados
"""
import subprocess
import sys
import os

def run_mysql_command(command, password=None):
    """Ejecutar comando mysql"""
    mysql_bin = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    
    if password:
        cmd = [mysql_bin, '-u', 'root', f'-p{password}', '-e', command]
    else:
        cmd = [mysql_bin, '-u', 'root', '-e', command]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)


def import_sql_file(backup_file, password=None):
    """Importar archivo SQL completo"""
    mysql_bin = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    
    if not os.path.exists(backup_file):
        print(f"✗ Archivo no encontrado: {backup_file}")
        return False
    
    if password:
        cmd = [
            mysql_bin,
            '-u', 'bar_galileo_user',
            f'-p{password}',
            'bar_galileo'
        ]
    else:
        cmd = [
            mysql_bin,
            '-u', 'bar_galileo_user',
            '-pGalileo2025',
            'bar_galileo'
        ]
    
    try:
        with open(backup_file, 'r', encoding='utf8') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True,
                encoding='utf8'
            )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Excepción: {e}")
        return False


print("=" * 70)
print("CONFIGURACIÓN RÁPIDA DE MYSQL - BAR GALILEO")
print("=" * 70)

# Solicitar contraseña de root
print("\nPara crear la base de datos, necesito la contraseña de root de MySQL.")
print("(Si instalaste MySQL recientemente y no configuraste contraseña, presiona Enter)")
root_pass = input("Contraseña de root de MySQL: ")

# Crear BD y usuario
print("\n1. Creando base de datos y usuario...")
sql_setup = """
CREATE DATABASE IF NOT EXISTS bar_galileo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bar_galileo_user'@'localhost' IDENTIFIED BY 'Galileo2025';
GRANT ALL PRIVILEGES ON bar_galileo.* TO 'bar_galileo_user'@'localhost';
FLUSH PRIVILEGES;
"""

success, stdout, stderr = run_mysql_command(sql_setup, root_pass if root_pass else None)

if success:
    print("✓ Base de datos y usuario creados exitosamente")
elif "already exists" in stderr.lower():
    print("⚠ Base de datos y usuario ya existen (OK)")
else:
    print(f"✗ Error: {stderr}")
    print("\n¿La contraseña fue correcta?")
    print("Puedes intentar crear la BD manualmente con MySQL Workbench o phpMyAdmin")
    sys.exit(1)

# Importar datos
print("\n2. Importando datos desde backup...")
backup_path = input("\nRuta al archivo bar_galileo_backup.sql\n(Enter para usar: C:\\Users\\felip\\Downloads\\bar_galileo_backup.sql): ")

if not backup_path.strip():
    backup_path = r"C:\Users\felip\Downloads\bar_galileo_backup.sql"

if import_sql_file(backup_path):
    print("✓ Datos importados exitosamente")
    print("\n" + "=" * 70)
    print("✓ MIGRACIÓN COMPLETADA")
    print("=" * 70)
    print("\nAhora edita el archivo .env y agrega:")
    print("  USE_MYSQL=True")
    print("\nLuego ejecuta:")
    print("  cd bar_galileo")
    print("  python manage.py check")
    print("  python manage.py runserver")
else:
    print("✗ Error al importar datos")
    sys.exit(1)
