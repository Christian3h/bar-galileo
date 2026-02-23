#!/bin/bash
# Script para configurar GPG sin contraseña para backups automáticos

echo "================================================"
echo "Configurando GPG para backups sin contraseña"
echo "================================================"
echo ""

# Verificar si GPG está instalado
if ! command -v gpg &> /dev/null; then
    echo "❌ GPG no está instalado."
    echo "Instalando GPG..."
    if command -v brew &> /dev/null; then
        brew install gnupg
    else
        echo "Por favor instala GPG manualmente: https://gnupg.org/download/"
        exit 1
    fi
fi

echo "✅ GPG está instalado"
echo ""

# Email para la clave
EMAIL="bargalileo07@gmail.com"

# Verificar si ya existe una clave para este email
echo "Verificando claves existentes para $EMAIL..."
existing_key=$(gpg --list-keys "$EMAIL" 2>/dev/null | grep "$EMAIL")

if [ ! -z "$existing_key" ]; then
    echo "⚠️  Ya existe una clave para $EMAIL"
    echo ""
    echo "Claves existentes:"
    gpg --list-keys "$EMAIL"
    echo ""
    read -p "¿Deseas eliminar la clave existente y crear una nueva sin contraseña? (s/n): " respuesta
    if [ "$respuesta" != "s" ]; then
        echo "Operación cancelada"
        exit 0
    fi
    
    # Eliminar clave existente
    echo "Eliminando clave existente..."
    key_id=$(gpg --list-keys --with-colons "$EMAIL" | awk -F: '/^pub/ {print $5; exit}')
    gpg --batch --yes --delete-secret-keys "$key_id" 2>/dev/null
    gpg --batch --yes --delete-keys "$key_id" 2>/dev/null
fi

echo "Creando nueva clave GPG sin contraseña..."
echo ""

# Crear archivo de configuración para generar la clave
cat > /tmp/gpg-batch-config <<EOF
%no-protection
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Bar Galileo Backups
Name-Email: $EMAIL
Expire-Date: 0
%commit
EOF

# Generar la clave
gpg --batch --gen-key /tmp/gpg-batch-config

# Limpiar archivo temporal
rm /tmp/gpg-batch-config

echo ""
echo "✅ Clave GPG creada exitosamente!"
echo ""
echo "Información de la clave:"
gpg --list-keys "$EMAIL"
echo ""
echo "================================================"
echo "✅ Configuración completada"
echo "================================================"
echo ""
echo "Ahora puedes:"
echo "1. Eliminar la línea DBBACKUP_GPG_PASSPHRASE del archivo .env"
echo "2. Reiniciar tu servidor Django"
echo "3. Los backups se crearán y restaurarán sin pedir contraseña"
echo ""
