"""
Script para inicializar el sistema RAG con el Manual de Usuario

Este script:
1. Verifica si existe el manual de usuario en docs/manual_usuario.md
2. Lo convierte a PDF si no existe en formato PDF
3. Lo carga en el sistema RAG como documento base
4. Lo indexa para que esté disponible en el chatbot

Ejecutar con:
    python manage.py shell < rag_chat/initialize_manual.py
O:
    python bar_galileo/manage.py runscript initialize_manual
"""

import os
import sys
from pathlib import Path

# Configurar el path para Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bar_galileo.settings')

import django
django.setup()

from rag_chat.models import DocumentCollection, DocumentChunk
from rag_chat.document_loader import DocumentLoader
from rag_chat.embeddings import get_embedding_generator
from django.core.files import File
import logging

logger = logging.getLogger(__name__)


def convert_md_to_pdf(md_path: str, pdf_path: str) -> bool:
    """
    Convierte el manual de Markdown a PDF usando markdown2 y pdfkit/weasyprint
    
    Args:
        md_path: Ruta al archivo .md
        pdf_path: Ruta donde guardar el PDF
        
    Returns:
        True si la conversión fue exitosa
    """
    try:
        import markdown
        from weasyprint import HTML, CSS
        
        # Leer markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convertir a HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Agregar CSS para mejor presentación
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #555; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convertir a PDF
        HTML(string=styled_html).write_pdf(pdf_path)
        print(f"✅ Manual convertido a PDF: {pdf_path}")
        return True
        
    except ImportError as e:
        print(f"⚠️ No se pudo convertir a PDF: {e}")
        print("Instala las dependencias: pip install markdown weasyprint")
        return False
    except Exception as e:
        print(f"❌ Error convirtiendo a PDF: {e}")
        return False


def initialize_manual():
    """Inicializa el sistema RAG con el manual de usuario"""
    
    print("=" * 60)
    print("🚀 Inicializando Sistema RAG con Manual de Usuario")
    print("=" * 60)
    
    # 1. Verificar si ya existe el manual en el sistema
    existing = DocumentCollection.objects.filter(title__icontains='Manual de Usuario').first()
    
    if existing:
        print(f"\n⚠️ Ya existe un manual cargado: {existing.title}")
        response = input("¿Deseas eliminarlo y crear uno nuevo? (s/n): ").strip().lower()
        
        if response == 's':
            print(f"🗑️ Eliminando manual anterior (ID: {existing.id})...")
            existing.delete()
            print("✅ Manual anterior eliminado")
        else:
            print("❌ Operación cancelada")
            return
    
    # 2. Buscar el archivo markdown
    md_path = BASE_DIR / 'docs' / 'manual_usuario.md'
    
    if not md_path.exists():
        print(f"❌ No se encontró el manual en: {md_path}")
        return
    
    print(f"✅ Manual encontrado: {md_path}")
    
    # 3. Intentar convertir a PDF
    pdf_path = BASE_DIR / 'media' / 'rag_documents' / 'manual_usuario.pdf'
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    pdf_created = False
    
    if not pdf_path.exists():
        print("\n📄 Convirtiendo Markdown a PDF...")
        pdf_created = convert_md_to_pdf(str(md_path), str(pdf_path))
    else:
        print(f"✅ PDF ya existe: {pdf_path}")
        pdf_created = True
    
    if not pdf_created:
        print("⚠️ No se pudo crear PDF. El sistema RAG requiere formato PDF.")
        print("Puedes convertir manualmente el archivo docs/manual_usuario.md a PDF")
        print("y colocarlo en media/rag_documents/manual_usuario.pdf")
        return
    
    # 4. Crear registro en la base de datos
    print("\n📚 Creando colección de documentos...")
    
    with open(pdf_path, 'rb') as f:
        collection = DocumentCollection.objects.create(
            title='Manual de Usuario - Sistema Bar Galileo',
            file=File(f, name='manual_usuario.pdf'),
            file_type='pdf',
            status='processing'
        )
    
    print(f"✅ Colección creada (ID: {collection.id})")
    
    # 5. Procesar documento (extraer texto, generar chunks, embeddings)
    print("\n🔍 Procesando documento...")
    print("   - Extrayendo texto del PDF")
    print("   - Generando fragmentos (chunks)")
    print("   - Creando embeddings con IA")
    print("   (Esto puede tomar varios minutos...)")
    
    try:
        loader = DocumentLoader(use_ocr=False)
        file_path = collection.file.path
        
        # Extraer páginas
        pages_data, total_pages = loader.load_pdf(file_path)
        collection.page_count = total_pages
        collection.save()
        print(f"   ✅ {total_pages} páginas extraídas")
        
        # Generar chunks
        chunks = loader.chunk_text(pages_data, chunk_size=500, overlap=50)
        print(f"   ✅ {len(chunks)} fragmentos generados")
        
        # Generar embeddings
        print("   🤖 Generando embeddings con IA...")
        generator = get_embedding_generator()
        texts = [chunk['content'] for chunk in chunks]
        embeddings = generator.encode_documents(texts, show_progress=True)
        print(f"   ✅ {len(embeddings)} embeddings generados")
        
        # Guardar en base de datos
        print("   💾 Guardando en base de datos...")
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            DocumentChunk.objects.create(
                collection=collection,
                chunk_index=idx,
                content=chunk['content'],
                embedding=embedding.tolist(),
                metadata=chunk['metadata']
            )
        
        collection.chunk_count = len(chunks)
        collection.status = 'indexed'
        collection.save()
        
        print("\n" + "=" * 60)
        print("✅ ¡Manual de Usuario inicializado correctamente!")
        print("=" * 60)
        print(f"\n📊 Estadísticas:")
        print(f"   - Título: {collection.title}")
        print(f"   - Páginas: {collection.page_count}")
        print(f"   - Fragmentos indexados: {collection.chunk_count}")
        print(f"   - Estado: {collection.status}")
        print(f"\n💬 El chatbot ya puede responder preguntas sobre el manual.")
        print(f"   Accede en: http://localhost:8000/rag-chat/")
        print("\n")
        
    except Exception as e:
        collection.status = 'error'
        collection.error_message = str(e)
        collection.save()
        print(f"\n❌ Error procesando documento: {e}")
        logger.exception("Error en inicialización de manual")
        raise


if __name__ == '__main__':
    try:
        initialize_manual()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
