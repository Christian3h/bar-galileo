@echo off
chcp 65001 > nul
cls

echo ======================================================================
echo SOLUCIÓN: BASE DE DATOS NO SE ACTUALIZA
echo ======================================================================
echo.

echo PASO 1: Verificando procesos de Python/Django...
echo.
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE 2>nul
echo.

echo ¿Hay múltiples procesos de python.exe corriendo?
echo Si es así, presiona 1 para matarlos todos
echo Si no, presiona 2 para continuar
echo.
set /p KILL_OPTION="Selecciona (1/2): "

if "%KILL_OPTION%"=="1" (
    echo.
    echo Cerrando todos los procesos de Python...
    taskkill /F /IM python.exe 2>nul
    timeout /t 2 > nul
    echo ✓ Procesos cerrados
)

echo.
echo ======================================================================
echo PASO 2: Limpiando sesiones de Django...
echo ======================================================================
echo.
cd /d "%~dp0"
python limpiar_sesiones.py
echo.
timeout /t 2 > nul

echo.
echo ======================================================================
echo PASO 3: Verificando migraciones...
echo ======================================================================
echo.
cd bar_galileo
python manage.py showmigrations
echo.

echo.
echo ======================================================================
echo SOLUCIONES ADICIONALES
echo ======================================================================
echo.
echo 1. LIMPIA EL CACHÉ DEL NAVEGADOR:
echo    - Chrome/Edge: Ctrl + Shift + Delete
echo    - Selecciona "Imágenes y archivos en caché"
echo    - Click en "Borrar datos"
echo.
echo 2. RECARGA LA PÁGINA SIN CACHÉ:
echo    - Ctrl + Shift + R (Windows)
echo    - Ctrl + F5 (alternativa)
echo.
echo 3. CIERRA SESIÓN Y VUELVE A ENTRAR:
echo    - Esto cargará una nueva sesión desde MySQL
echo.
echo 4. USA MODO INCÓGNITO:
echo    - Para descartar problemas de caché
echo.
echo 5. VERIFICA EN MYSQL WORKBENCH:
echo    - Abre MySQL Workbench
echo    - Ejecuta: SELECT * FROM nombre_tabla ORDER BY id DESC LIMIT 10;
echo    - Verifica si los cambios están ahí
echo.
echo ======================================================================
echo.

echo ¿Deseas iniciar el servidor Django ahora? (S/N)
set /p START_SERVER="Respuesta: "

if /i "%START_SERVER%"=="S" (
    echo.
    echo Iniciando servidor Django...
    echo Si el servidor no inicia correctamente, presiona Ctrl+C
    echo.
    timeout /t 2 > nul
    python manage.py runserver
) else (
    echo.
    echo Para iniciar manualmente:
    echo   cd bar_galileo
    echo   python manage.py runserver
)

echo.
pause
