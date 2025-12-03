#!/usr/bin/env python3
"""
Script para limpiar archivos duplicados con el patrón " 2.extensión"
Este script busca archivos que terminan con " 2.xxx" y los elimina de forma segura.
"""

import os
import shutil
import sys
from pathlib import Path

def find_duplicates(root_dir):
    """Encuentra todos los archivos duplicados con el patrón ' 2.xxx'"""
    duplicates = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if ' 2.' in file:
                file_path = os.path.join(root, file)
                duplicates.append(file_path)
    
    return duplicates

def verify_original_exists(duplicate_path):
    """Verifica si existe el archivo original (sin ' 2')"""
    # Remover ' 2' del nombre del archivo
    original_path = duplicate_path.replace(' 2.', '.')
    return os.path.exists(original_path)

def cleanup_duplicates(root_dir, dry_run=True):
    """Limpia archivos duplicados"""
    duplicates = find_duplicates(root_dir)
    
    print(f"Encontrados {len(duplicates)} archivos duplicados:")
    print("-" * 60)
    
    removed_count = 0
    safe_to_remove = []
    
    for duplicate in duplicates:
        original_exists = verify_original_exists(duplicate)
        relative_path = os.path.relpath(duplicate, root_dir)
        
        if original_exists:
            safe_to_remove.append(duplicate)
            print(f"✓ SEGURO: {relative_path}")
        else:
            print(f"⚠ CUIDADO: {relative_path} (no existe original)")
    
    print(f"\nArchivos seguros para eliminar: {len(safe_to_remove)}")
    print(f"Archivos que requieren revisión manual: {len(duplicates) - len(safe_to_remove)}")
    
    if not dry_run and safe_to_remove:
        confirm = input(f"\n¿Confirmar eliminación de {len(safe_to_remove)} archivos? (y/N): ")
        if confirm.lower() == 'y':
            for file_path in safe_to_remove:
                try:
                    os.remove(file_path)
                    removed_count += 1
                    print(f"Eliminado: {os.path.relpath(file_path, root_dir)}")
                except Exception as e:
                    print(f"Error eliminando {file_path}: {e}")
            
            print(f"\n✓ Eliminados {removed_count} archivos duplicados")
        else:
            print("Operación cancelada")
    
    return len(safe_to_remove), len(duplicates) - len(safe_to_remove)

if __name__ == "__main__":
    root_directory = "/Users/jorgealfredoarismendyzambrano/Documents/bar-galileo"
    
    print("=== LIMPIEZA DE ARCHIVOS DUPLICADOS ===")
    print(f"Directorio: {root_directory}")
    print()
    
    # Primero hacer un dry run
    print("1. ANÁLISIS (sin eliminar archivos):")
    safe_count, unsafe_count = cleanup_duplicates(root_directory, dry_run=True)
    
    if safe_count > 0:
        print(f"\n2. ELIMINACIÓN REAL:")
        cleanup_duplicates(root_directory, dry_run=False)
    else:
        print("\nNo hay archivos seguros para eliminar automáticamente.")
