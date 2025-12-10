#!/usr/bin/env python
"""
Script para reindexar el manual de usuario en el sistema RAG
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')
django.setup()

from rag_chat.models import DocumentCollection, DocumentChunk
from rag_chat.document_loader import DocumentLoader
from rag_chat.embeddings import get_embedding_generator
from rag_chat.vector_store import DatabaseVectorStore

def reindex_manual():
    """Reindexar el manual de usuario"""
    print("🔄 Reinicializando manual de usuario...")
    
    # 1. Eliminar manual anterior si existe
    old_manuals = DocumentCollection.objects.filter(title__icontains='Manual')
    if old_manuals.exists():
        print(f"  ✓ Eliminando {old_manuals.count()} manuales antiguos...")
        old_manuals.delete()
    
    # 2. Encontrar el archivo del manual
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    manual_path = os.path.join(docs_dir, 'manual_usuario.md')
    
    if not os.path.exists(manual_path):
        print(f"  ❌ Error: No se encontró el manual en {manual_path}")
        return False
    
    print(f"  ✓ Manual encontrado: {manual_path}")
    
    # 3. Guardar archivo temporalmente para el FileField
    from django.core.files import File
    
    collection = DocumentCollection.objects.create(
        title='Manual de Usuario - Bar Galileo',
        file_type='markdown',
        status='processing'
    )
    
    # Guardar el archivo
    with open(manual_path, 'rb') as f:
        collection.file.save('manual_usuario.md', File(f), save=True)
    
    print(f"  ✓ Colección creada (ID: {collection.id})")
    
    # 4. Procesar documento
    try:
        loader = DocumentLoader()
        
        # Leer el archivo markdown
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_text = f.read()
        
        # Crear páginas simuladas para markdown
        pages_data = [{
            'page': 1,
            'text': manual_text,
            'metadata': {
                'page_number': 1,
                'total_pages': 1,
                'source': 'manual_usuario.md'
            }
        }]
        
        # Dividir en chunks
        chunks = loader.chunk_text(pages_data, chunk_size=500, overlap=100)
        
        if not chunks:
            print("  ❌ Error: No se generaron chunks")
            collection.status = 'failed'
            collection.error_message = 'No se pudieron generar chunks'
            collection.save()
            return False
        
        print(f"  ✓ Generados {len(chunks)} chunks")
        
        # 5. Generar embeddings
        generator = get_embedding_generator()
        print(f"  ✓ Usando modelo de embeddings (dimensión: {generator.dimension})")
        
        # 6. Guardar chunks con embeddings
        for i, chunk_data in enumerate(chunks, 1):
            # Generar embedding
            embedding = generator.encode([chunk_data['content']])[0].tolist()
            
            # Crear chunk en DB con embedding
            chunk = DocumentChunk.objects.create(
                collection=collection,
                content=chunk_data['content'],
                metadata=chunk_data['metadata'],
                chunk_index=i-1,
                embedding=embedding  # Guardar directamente
            )
            
            if i % 10 == 0:
                print(f"  ✓ Procesados {i}/{len(chunks)} chunks...")
        
        # 7. Actualizar colección
        collection.status = 'indexed'
        collection.chunk_count = len(chunks)
        collection.page_count = 1
        collection.save()
        
        print(f"  ✅ Manual indexado exitosamente!")
        print(f"     - Total de chunks: {len(chunks)}")
        print(f"     - Dimensión de vectores: {generator.dimension}")
        print(f"     - ID de colección: {collection.id}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error durante la indexación: {e}")
        collection.status = 'failed'
        collection.error_message = str(e)
        collection.save()
        return False

if __name__ == '__main__':
    success = reindex_manual()
    sys.exit(0 if success else 1)
