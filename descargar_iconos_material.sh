#!/bin/bash

# Script para descargar iconos de Material Icons necesarios para el módulo de accesibilidad
# Autor: Asistente
# Fecha: 18 de octubre de 2025

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Descargador de Iconos Material Icons ===${NC}\n"

# Directorio de destino
DEST_DIR="bar_galileo/static/img/icons"

# Crear directorio si no existe
mkdir -p "$DEST_DIR"

# URL base de Material Design Icons en GitHub
BASE_URL="https://raw.githubusercontent.com/google/material-design-icons/master/src"

# Lista de iconos necesarios (nombre del icono y su categoría)
declare -A ICONS=(
    ["local_parking"]="maps"
    ["link"]="content"
    ["title"]="editor"
    ["record_voice_over"]="av"
    ["subscriptions"]="av"
    ["nightlight"]="device"
    ["brightness_5"]="device"
    ["format_size"]="content"
    ["remove"]="content"
    ["filter_b_and_w"]="image"
    ["gradient"]="image"
    ["filter_vintage"]="image"
    ["tonality"]="image"
    ["mouse"]="hardware"
    ["motion_photos_off"]="image"
    ["local_library"]="maps"
)

echo -e "${BLUE}Descargando iconos en: ${GREEN}$DEST_DIR${NC}\n"

# Contador
count=0
total=${#ICONS[@]}

# Descargar cada icono
for icon in "${!ICONS[@]}"; do
    category="${ICONS[$icon]}"
    count=$((count + 1))
    
    echo -e "[${count}/${total}] Descargando ${BLUE}${icon}${NC} (categoría: ${category})..."
    
    # Intentar descargar desde diferentes variantes (24px regular)
    URL="${BASE_URL}/${category}/${icon}/materialicons/24px.svg"
    
    # Descargar usando curl
    curl -s -L "$URL" -o "${DEST_DIR}/${icon}.svg"
    
    if [ $? -eq 0 ] && [ -s "${DEST_DIR}/${icon}.svg" ]; then
        echo -e "  ${GREEN}✓${NC} ${icon}.svg descargado correctamente"
    else
        echo -e "  ${RED}✗${NC} Error descargando ${icon}.svg"
        # Intentar URL alternativa
        URL_ALT="${BASE_URL}/${category}/${icon}/materialiconsoutlined/24px.svg"
        curl -s -L "$URL_ALT" -o "${DEST_DIR}/${icon}.svg"
        
        if [ $? -eq 0 ] && [ -s "${DEST_DIR}/${icon}.svg" ]; then
            echo -e "  ${GREEN}✓${NC} ${icon}.svg descargado (variante alternativa)"
        else
            echo -e "  ${RED}✗✗${NC} No se pudo descargar ${icon}.svg"
        fi
    fi
done

echo -e "\n${GREEN}=== Descarga completada ===${NC}"
echo -e "Iconos guardados en: ${GREEN}$(pwd)/${DEST_DIR}${NC}\n"

# Verificar iconos ya existentes
echo -e "${BLUE}Iconos ya existentes:${NC}"
ls -1 "$DEST_DIR" | grep -E "^(add|close|reset)\.svg$" | while read icon; do
    echo -e "  ${GREEN}✓${NC} $icon"
done

echo -e "\n${BLUE}Todos los iconos descargados:${NC}"
ls -1 "$DEST_DIR" | grep "\.svg$" | wc -l | xargs echo -e "  Total:" 

echo -e "\n${BLUE}Para usar estos iconos, debes modificar sienna.js para reemplazar los material-icons por imgs${NC}"
