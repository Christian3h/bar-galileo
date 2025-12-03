#!/usr/bin/env python3
import os
import re

def clean_merge_conflicts(file_path):
    """Limpia los conflictos de merge de un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para detectar conflictos de merge
    pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [a-f0-9]+\n?'
    
    def replace_conflict(match):
        head_content = match.group(1)
        other_content = match.group(2)
        
        # Si HEAD tiene contenido y el otro no, usar HEAD
        if head_content.strip() and not other_content.strip():
            return head_content + '\n'
        # Si el otro tiene contenido y HEAD no, usar el otro
        elif other_content.strip() and not head_content.strip():
            return other_content + '\n'
        # Si ambos tienen contenido, usar HEAD (puedes cambiar esta lógica)
        elif head_content.strip() and other_content.strip():
            return head_content + '\n'
        # Si ninguno tiene contenido, eliminar el conflicto
        else:
            return ''
    
    # Reemplazar todos los conflictos de merge
    cleaned_content = re.sub(pattern, replace_conflict, content, flags=re.DOTALL)
    
    # Verificar si se hicieron cambios
    if cleaned_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Limpiado: {file_path}")
        return True
    return False

def find_and_clean_conflicts(directory):
    """Busca y limpia conflictos de merge en archivos Python."""
    cleaned_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    if clean_merge_conflicts(file_path):
                        cleaned_files.append(file_path)
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
    
    return cleaned_files

if __name__ == "__main__":
    # Directorio del proyecto Django
    project_dir = r"c:\Users\felip\Desktop\bar-galileo\bar_galileo"
    
    print("Buscando y limpiando conflictos de merge...")
    cleaned_files = find_and_clean_conflicts(project_dir)
    
    if cleaned_files:
        print(f"\nArchivos limpiados ({len(cleaned_files)}):")
        for file in cleaned_files:
            print(f"  - {file}")
    else:
        print("No se encontraron conflictos de merge para limpiar.")
    
    print("\n¡Proceso completado!")