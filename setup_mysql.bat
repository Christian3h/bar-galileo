@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ======================================================================
echo CONFIGURACIÓN DE MYSQL - BAR GALILEO
echo ======================================================================
echo.

set MYSQL_BIN="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

echo Este script configurará tu base de datos MySQL.
echo.
echo Opciones:
echo   1. Tengo la contraseña de root de MySQL
echo   2. No tengo contraseña de root (acceso sin contraseña)
echo   3. Usar MySQL Workbench manualmente
echo   4. Salir
echo.
set /p OPTION="Selecciona una opción (1-4): "

if "%OPTION%"=="4" goto :END
if "%OPTION%"=="3" goto :MANUAL

if "%OPTION%"=="1" (
    set /p ROOT_PASS="Ingresa la contraseña de root: "
    set MYSQL_CMD=%MYSQL_BIN% -u root -p!ROOT_PASS!
) else if "%OPTION%"=="2" (
    set MYSQL_CMD=%MYSQL_BIN% -u root
) else (
    echo Opción inválida
    goto :END
)

echo.
echo Creando base de datos y usuario...
echo.

%MYSQL_CMD% -e "CREATE DATABASE IF NOT EXISTS bar_galileo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'bar_galileo_user'@'localhost' IDENTIFIED BY 'Galileo2025'; GRANT ALL PRIVILEGES ON bar_galileo.* TO 'bar_galileo_user'@'localhost'; FLUSH PRIVILEGES;"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Error al crear la base de datos.
    echo.
    echo Posibles causas:
    echo   - Contraseña incorrecta
    echo   - MySQL no está corriendo
    echo   - Problemas de permisos
    echo.
    echo Intenta la opción 3 para configurar manualmente con MySQL Workbench
    goto :END
)

echo ✓ Base de datos y usuario creados exitosamente
echo.
echo Importando datos...
echo.

set /p BACKUP_PATH="Ruta al archivo bar_galileo_backup.sql (Enter para C:\Users\felip\Downloads\bar_galileo_backup.sql): "

if "%BACKUP_PATH%"=="" (
    set BACKUP_PATH=C:\Users\felip\Downloads\bar_galileo_backup.sql
)

if not exist "%BACKUP_PATH%" (
    echo ✗ Archivo no encontrado: %BACKUP_PATH%
    goto :END
)

echo Importando desde: %BACKUP_PATH%
%MYSQL_BIN% -u bar_galileo_user -pGalileo2025 bar_galileo < "%BACKUP_PATH%"

if %ERRORLEVEL% NEQ 0 (
    echo ✗ Error al importar datos
    goto :END
)

echo.
echo ======================================================================
echo ✓ MIGRACIÓN COMPLETADA EXITOSAMENTE
echo ======================================================================
echo.
echo Próximos pasos:
echo   1. Edita el archivo .env y agrega: USE_MYSQL=True
echo   2. Ejecuta: cd bar_galileo
echo   3. Ejecuta: python manage.py check
echo   4. Ejecuta: python manage.py runserver
echo.
goto :END

:MANUAL
echo.
echo ======================================================================
echo INSTRUCCIONES PARA CONFIGURACIÓN MANUAL
echo ======================================================================
echo.
echo 1. Abre MySQL Workbench
echo 2. Conéctate a tu servidor local
echo 3. Ejecuta este script SQL:
echo.
echo    CREATE DATABASE IF NOT EXISTS bar_galileo 
echo    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo.
echo    CREATE USER IF NOT EXISTS 'bar_galileo_user'@'localhost' 
echo    IDENTIFIED BY 'Galileo2025';
echo.
echo    GRANT ALL PRIVILEGES ON bar_galileo.* 
echo    TO 'bar_galileo_user'@'localhost';
echo.
echo    FLUSH PRIVILEGES;
echo.
echo 4. Importa el archivo: C:\Users\felip\Downloads\bar_galileo_backup.sql
echo    (Server → Data Import → Import from Self-Contained File)
echo.
echo 5. Luego edita el archivo .env y agrega: USE_MYSQL=True
echo.
pause
goto :END

:END
echo.
pause
