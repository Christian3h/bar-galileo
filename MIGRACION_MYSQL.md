# Guía de Migración a MySQL para Bar Galileo

## Pasos para completar la migración:

### 1. Instalar MySQL (si no está instalado)
- Descargar MySQL Community Server desde: https://dev.mysql.com/downloads/mysql/
- O instalar XAMPP/WAMP que incluye MySQL

### 2. Crear la base de datos y usuario
Abre una terminal de MySQL como administrador y ejecuta:

```bash
# Opción 1: Ejecutar archivo SQL
mysql -u root -p < setup_mysql.sql

# Opción 2: Ejecutar comandos directamente
mysql -u root -p
```

Luego dentro de MySQL:
```sql
CREATE DATABASE IF NOT EXISTS bar_galileo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bar_galileo_user'@'localhost' IDENTIFIED BY 'Galileo2025';
GRANT ALL PRIVILEGES ON bar_galileo.* TO 'bar_galileo_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Importar el backup de datos
Desde la terminal de Windows (PowerShell):

```powershell
# Navegar a la carpeta donde está el backup
cd C:\Users\felip\Downloads

# Importar el backup
mysql -u bar_galileo_user -pGalileo2025 bar_galileo < bar_galileo_backup.sql
```

**Nota:** Si el comando anterior da error, intenta sin espacio después de -p:
```powershell
mysql -u bar_galileo_user -p bar_galileo < bar_galileo_backup.sql
# Luego ingresa la contraseña: Galileo2025
```

### 4. Activar MySQL en Django
Edita el archivo `.env` y agrega o modifica:
```
USE_MYSQL=True
```

### 5. Verificar la conexión
```powershell
cd bar_galileo
python manage.py check
```

### 6. Ejecutar el servidor
```powershell
python manage.py runserver
```

## Credenciales configuradas:
- **Base de datos:** bar_galileo
- **Usuario:** bar_galileo_user
- **Contraseña:** Galileo2025
- **Host:** localhost
- **Puerto:** 3306

## Solución de problemas:

### Error: "Access denied"
Verificar que MySQL esté corriendo:
```powershell
# En XAMPP: Iniciar MySQL desde el panel de control
# En Windows Services: Verificar que "MySQL" esté corriendo
```

### Error: "Can't connect to MySQL server"
- Verificar que MySQL esté instalado y corriendo
- Verificar que el puerto 3306 esté abierto
- Verificar las credenciales en el archivo .env

### Volver a SQLite temporalmente
Si necesitas volver a SQLite, simplemente cambia en `.env`:
```
USE_MYSQL=False
```
