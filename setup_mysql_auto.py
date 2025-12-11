"""
Script para configurar la base de datos MySQL automáticamente
"""
import pymysql
import sys
import os
from pathlib import Path

def setup_mysql_database():
    """Crear base de datos y usuario MySQL para Bar Galileo"""
    
    # Solicitar contraseña de root si es necesario
    print("=" * 60)
    print("CONFIGURACIÓN DE BASE DE DATOS MYSQL")
    print("=" * 60)
    
    # Intentar conectar como root sin contraseña primero
    connection = None
    try:
        print("\n1. Intentando conectar a MySQL como root sin contraseña...")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            charset='utf8mb4'
        )
        print("✓ Conexión exitosa sin contraseña")
    except pymysql.err.OperationalError as e:
        if "Access denied" in str(e):
            print("✗ Se requiere contraseña de root")
            # Solicitar contraseña
            from getpass import getpass
            root_password = getpass("Ingresa la contraseña de root de MySQL: ")
            
            try:
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password=root_password,
                    charset='utf8mb4'
                )
                print("✓ Conexión exitosa con contraseña")
            except Exception as e:
                print(f"✗ Error al conectar: {e}")
                print("\nPor favor verifica:")
                print("  - MySQL está corriendo")
                print("  - La contraseña de root es correcta")
                sys.exit(1)
        else:
            print(f"✗ Error al conectar a MySQL: {e}")
            print("\nAsegúrate de que MySQL esté corriendo.")
            sys.exit(1)
    
    if connection is None:
        print("✗ No se pudo establecer conexión con MySQL")
        sys.exit(1)
    
    try:
        cursor = connection.cursor()
        
        # Crear base de datos
        print("\n2. Creando base de datos 'bar_galileo'...")
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS bar_galileo "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print("✓ Base de datos creada/verificada")
        
        # Crear usuario
        print("\n3. Creando usuario 'bar_galileo_user'...")
        try:
            cursor.execute(
                "CREATE USER 'bar_galileo_user'@'localhost' "
                "IDENTIFIED BY 'Galileo2025'"
            )
            print("✓ Usuario creado")
        except pymysql.err.OperationalError as e:
            if "already exists" in str(e) or "Operation CREATE USER" in str(e):
                print("⚠ Usuario ya existe, actualizando contraseña...")
                cursor.execute(
                    "ALTER USER 'bar_galileo_user'@'localhost' "
                    "IDENTIFIED BY 'Galileo2025'"
                )
                print("✓ Contraseña actualizada")
            else:
                raise
        
        # Otorgar permisos
        print("\n4. Otorgando permisos...")
        cursor.execute(
            "GRANT ALL PRIVILEGES ON bar_galileo.* "
            "TO 'bar_galileo_user'@'localhost'"
        )
        cursor.execute("FLUSH PRIVILEGES")
        print("✓ Permisos otorgados")
        
        print("\n" + "=" * 60)
        print("✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nCredenciales configuradas:")
        print("  Base de datos: bar_galileo")
        print("  Usuario: bar_galileo_user")
        print("  Contraseña: Galileo2025")
        print("  Host: localhost")
        print("  Puerto: 3306")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error durante la configuración: {e}")
        return False
    finally:
        if connection:
            connection.close()


def import_backup(backup_file):
    """Importar el archivo de backup SQL"""
    
    print("\n" + "=" * 60)
    print("IMPORTACIÓN DE DATOS")
    print("=" * 60)
    
    if not os.path.exists(backup_file):
        print(f"\n✗ Archivo de backup no encontrado: {backup_file}")
        print("\nPor favor, proporciona la ruta correcta al archivo bar_galileo_backup.sql")
        return False
    
    try:
        print(f"\n1. Conectando a base de datos 'bar_galileo'...")
        connection = pymysql.connect(
            host='localhost',
            user='bar_galileo_user',
            password='Galileo2025',
            database='bar_galileo',
            charset='utf8mb4'
        )
        print("✓ Conexión exitosa")
        
        print(f"\n2. Leyendo archivo de backup...")
        with open(backup_file, 'r', encoding='utf8') as f:
            sql_content = f.read()
        
        # Dividir en comandos individuales
        commands = sql_content.split(';')
        total_commands = len([c for c in commands if c.strip()])
        
        print(f"✓ {total_commands} comandos SQL encontrados")
        
        print(f"\n3. Ejecutando comandos SQL...")
        cursor = connection.cursor()
        executed = 0
        
        for i, command in enumerate(commands, 1):
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    executed += 1
                    if executed % 100 == 0:
                        print(f"   Ejecutados: {executed}/{total_commands}")
                except Exception as e:
                    # Ignorar algunos errores comunes
                    if "already exists" not in str(e).lower():
                        print(f"   ⚠ Advertencia en comando {i}: {e}")
        
        connection.commit()
        print(f"✓ {executed} comandos ejecutados exitosamente")
        
        print("\n" + "=" * 60)
        print("✓ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error durante la importación: {e}")
        return False
    finally:
        if 'connection' in locals() and connection:
            connection.close()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("SCRIPT DE MIGRACIÓN A MYSQL - BAR GALILEO")
    print("=" * 60)
    
    # Paso 1: Configurar base de datos
    if not setup_mysql_database():
        print("\n✗ Fallo en la configuración de la base de datos")
        sys.exit(1)
    
    # Paso 2: Importar datos
    backup_file = input("\nIngresa la ruta completa al archivo bar_galileo_backup.sql\n(o presiona Enter para usar: C:\\Users\\felip\\Downloads\\bar_galileo_backup.sql): ")
    
    if not backup_file.strip():
        backup_file = r"C:\Users\felip\Downloads\bar_galileo_backup.sql"
    
    if import_backup(backup_file):
        print("\n" + "=" * 60)
        print("✓ MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print("\nPróximos pasos:")
        print("1. Edita el archivo .env y agrega: USE_MYSQL=True")
        print("2. Ejecuta: python manage.py check")
        print("3. Ejecuta: python manage.py runserver")
    else:
        print("\n✗ La importación falló. Revisa los errores anteriores.")
        sys.exit(1)
