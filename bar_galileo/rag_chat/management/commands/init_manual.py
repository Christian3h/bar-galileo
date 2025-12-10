"""
Django Management Command para inicializar el Manual de Usuario en el sistema RAG

Uso:
    python manage.py init_manual [--force]

Opciones:
    --force     Fuerza la reinicialización eliminando el manual existente
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from pathlib import Path
from rag_chat.models import DocumentCollection, DocumentChunk
from rag_chat.document_loader import DocumentLoader
from rag_chat.embeddings import get_embedding_generator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicializa el Manual de Usuario en el sistema RAG'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la reinicialización eliminando el manual existente',
        )
        parser.add_argument(
            '--skip-pdf',
            action='store_true',
            help='Omite la conversión a PDF (debe existir el PDF)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 Inicializando Manual de Usuario en Sistema RAG'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        force = options['force']
        skip_pdf = options['skip_pdf']

        # 1. Verificar si ya existe el manual
        existing = DocumentCollection.objects.filter(
            title__icontains='Manual de Usuario'
        ).first()

        if existing:
            if force:
                self.stdout.write(
                    self.style.WARNING(
                        f'🗑️  Eliminando manual anterior (ID: {existing.id})...'
                    )
                )
                existing.delete()
                self.stdout.write(self.style.SUCCESS('✅ Manual anterior eliminado'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Ya existe un manual cargado: {existing.title}'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        '   Usa --force para eliminarlo y crear uno nuevo'
                    )
                )
                return

        # 2. Buscar archivo markdown
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        md_path = base_dir / 'docs' / 'manual_usuario.md'

        if not md_path.exists():
            raise CommandError(f'❌ No se encontró el manual en: {md_path}')

        self.stdout.write(self.style.SUCCESS(f'✅ Manual encontrado: {md_path}'))

        # 3. Preparar o convertir PDF
        pdf_path = base_dir / 'bar_galileo' / 'media' / 'rag_documents' / 'manual_usuario.pdf'
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        if not pdf_path.exists() and not skip_pdf:
            self.stdout.write('📄 Convirtiendo Markdown a PDF...')
            if self._convert_md_to_pdf(md_path, pdf_path):
                self.stdout.write(self.style.SUCCESS('✅ PDF creado correctamente'))
            else:
                raise CommandError(
                    '❌ No se pudo crear el PDF. '
                    'Instala: pip install markdown weasyprint'
                )
        elif not pdf_path.exists():
            raise CommandError(
                f'❌ PDF no encontrado y --skip-pdf activo: {pdf_path}'
            )
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ PDF encontrado: {pdf_path}'))

        # 4. Crear registro en BD
        self.stdout.write('')
        self.stdout.write('📚 Creando colección de documentos...')

        with open(pdf_path, 'rb') as f:
            collection = DocumentCollection.objects.create(
                title='Manual de Usuario - Sistema Bar Galileo',
                file=File(f, name='manual_usuario.pdf'),
                file_type='pdf',
                status='processing'
            )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Colección creada (ID: {collection.id})')
        )

        # 5. Procesar documento
        self.stdout.write('')
        self.stdout.write('🔍 Procesando documento...')
        self.stdout.write('   - Extrayendo texto del PDF')
        self.stdout.write('   - Generando fragmentos (chunks)')
        self.stdout.write('   - Creando embeddings con IA')
        self.stdout.write('   (Esto puede tomar varios minutos...)')
        self.stdout.write('')

        try:
            self._process_document(collection)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(
                self.style.SUCCESS('✅ ¡Manual de Usuario inicializado correctamente!')
            )
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write('')
            self.stdout.write('📊 Estadísticas:')
            self.stdout.write(f'   - Título: {collection.title}')
            self.stdout.write(f'   - Páginas: {collection.page_count}')
            self.stdout.write(f'   - Fragmentos indexados: {collection.chunk_count}')
            self.stdout.write(f'   - Estado: {collection.status}')
            self.stdout.write('')
            self.stdout.write(
                '💬 El chatbot ya puede responder preguntas sobre el manual.'
            )
            self.stdout.write('   Accede en: http://localhost:8000/rag-chat/')
            self.stdout.write('')

        except Exception as e:
            collection.status = 'error'
            collection.error_message = str(e)
            collection.save()
            raise CommandError(f'❌ Error procesando documento: {e}')

    def _convert_md_to_pdf(self, md_path: Path, pdf_path: Path) -> bool:
        """Convierte Markdown a PDF"""
        try:
            import markdown
            from weasyprint import HTML

            # Leer markdown
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convertir a HTML
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'toc']
            )

            # CSS para mejor presentación
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
                    h1 {{ 
                        color: #2c3e50; 
                        border-bottom: 2px solid #3498db; 
                        padding-bottom: 10px; 
                    }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    h3 {{ color: #7f8c8d; }}
                    table {{ 
                        border-collapse: collapse; 
                        width: 100%; 
                        margin: 20px 0; 
                    }}
                    th, td {{ 
                        border: 1px solid #ddd; 
                        padding: 8px; 
                        text-align: left; 
                    }}
                    th {{ 
                        background-color: #3498db; 
                        color: white; 
                    }}
                    code {{ 
                        background-color: #f4f4f4; 
                        padding: 2px 5px; 
                        border-radius: 3px; 
                    }}
                    pre {{ 
                        background-color: #f4f4f4; 
                        padding: 10px; 
                        border-radius: 5px; 
                        overflow-x: auto; 
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Convertir a PDF
            HTML(string=styled_html).write_pdf(pdf_path)
            return True

        except ImportError:
            return False
        except Exception as e:
            logger.exception('Error convirtiendo a PDF')
            return False

    def _process_document(self, collection: DocumentCollection):
        """Procesa el documento: extrae texto, genera chunks y embeddings"""
        loader = DocumentLoader(use_ocr=False)
        file_path = collection.file.path

        # Extraer páginas
        pages_data, total_pages = loader.load_pdf(file_path)
        collection.page_count = total_pages
        collection.save()
        self.stdout.write(f'   ✅ {total_pages} páginas extraídas')

        # Generar chunks
        chunks = loader.chunk_text(pages_data, chunk_size=500, overlap=50)
        self.stdout.write(f'   ✅ {len(chunks)} fragmentos generados')

        # Generar embeddings
        self.stdout.write('   🤖 Generando embeddings con IA...')
        generator = get_embedding_generator()
        texts = [chunk['content'] for chunk in chunks]
        embeddings = generator.encode_documents(texts, show_progress=False)
        self.stdout.write(f'   ✅ {len(embeddings)} embeddings generados')

        # Guardar en BD
        self.stdout.write('   💾 Guardando en base de datos...')
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
