#!/bin/bash
# Script para verificar la configuración de GPG

echo "================================================"
echo "Verificación de GPG para Backups"
echo "================================================"
echo ""

# Verificar si GPG está instalado
if ! command -v gpg &> /dev/null; then
    echo "❌ GPG no está instalado"
    echo ""
    echo "Para instalar GPG en macOS:"
    echo "  brew install gnupg"
    exit 1
fi

echo "✅ GPG está instalado"
gpg --version | head -n 1
echo ""

# Email configurado
EMAIL="bargalileo07@gmail.com"

# Verificar claves existentes
echo "Buscando claves para $EMAIL..."
echo ""

if gpg --list-keys "$EMAIL" &> /dev/null; then
    echo "✅ Se encontraron claves GPG:"
    echo ""
    gpg --list-keys "$EMAIL"
    echo ""
    
    # Verificar si la clave tiene contraseña
    echo "Probando si la clave necesita contraseña..."
    echo "test" | gpg --encrypt --recipient "$EMAIL" --armor | gpg --decrypt --batch --yes &> /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ La clave NO requiere contraseña (perfecto para backups automáticos)"
    else
        echo "⚠️  La clave REQUIERE contraseña"
        echo ""
        echo "SOLUCIONES:"
        echo "1. Agregar la contraseña al archivo .env:"
        echo "   DBBACKUP_GPG_PASSPHRASE=tu_contraseña_aqui"
        echo ""
        echo "2. Crear una nueva clave sin contraseña ejecutando:"
        echo "   ./configurar_gpg_sin_password.sh"
    fi
else
    echo "❌ No se encontraron claves GPG para $EMAIL"
    echo ""
    echo "SOLUCIÓN:"
    echo "Ejecuta el siguiente comando para crear una clave sin contraseña:"
    echo "  ./configurar_gpg_sin_password.sh"
fi

echo ""
echo "================================================"
echo "Estado del archivo .env"
echo "================================================"
echo ""

if [ -f "bar_galileo/bar_galileo/.env" ]; then
    if grep -q "DBBACKUP_GPG_PASSPHRASE" bar_galileo/bar_galileo/.env; then
        passphrase_value=$(grep "DBBACKUP_GPG_PASSPHRASE" bar_galileo/bar_galileo/.env | cut -d'=' -f2)
        if [ "$passphrase_value" == "tu_contraseña_gpg_aqui" ] || [ -z "$passphrase_value" ]; then
            echo "⚠️  DBBACKUP_GPG_PASSPHRASE está configurado pero con valor por defecto"
            echo "   Debes cambiar 'tu_contraseña_gpg_aqui' por tu contraseña real"
            echo "   O crear una clave sin contraseña con ./configurar_gpg_sin_password.sh"
        else
            echo "✅ DBBACKUP_GPG_PASSPHRASE está configurado"
        fi
    else
        echo "⚠️  DBBACKUP_GPG_PASSPHRASE no está en el archivo .env"
    fi
else
    echo "❌ No se encontró el archivo .env"
fi

echo ""
