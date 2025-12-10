"""
RAG Chat Views - Endpoints para upload, indexación y consultas RAG
"""
import os
import json
import logging
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from .models import DocumentCollection, DocumentChunk, RAGQuery
from .document_loader import DocumentLoader
from .embeddings import get_embedding_generator
from .vector_store import DatabaseVectorStore

logger = logging.getLogger(__name__)


def chat_view(request):
    """Vista principal del chat RAG"""
    # Obtener el manual de usuario como documento principal
    manual = DocumentCollection.objects.filter(
        title__icontains='Manual de Usuario',
        status='indexed'
    ).first()
    
    context = {
        'manual_disponible': manual is not None,
        'manual_id': manual.id if manual else None,
        'manual_titulo': manual.title if manual else None,
    }
    
    return render(request, 'rag_chat/chat.html', context)


def _call_google_api_with_context(query: str, context_chunks: list) -> tuple:
    """
    Llama a Google API con contexto de documentos.

    Args:
        query: Pregunta del usuario
        context_chunks: Lista de chunks relevantes

    Returns:
        tuple: (respuesta, error)
    """
    import requests

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None, 'GOOGLE_API_KEY no configurada'

    # Construir prompt con contexto
    context_text = "\n\n".join([
        f"{c['metadata']['content']}"
        for c in context_chunks
    ])

    prompt = f"""Eres el asistente de ayuda del Sistema Bar Galileo. Tu trabajo es responder preguntas sobre cómo usar el sistema basándote ÚNICAMENTE en el manual proporcionado.

INSTRUCCIONES IMPORTANTES:
1. Responde SOLO con información del contexto proporcionado
2. Si la pregunta no está en el contexto, di: "No encontré esa información en el manual"
3. Sé breve y directo - máximo 4-5 líneas
4. Si hay pasos, numéralos claramente
5. Usa un lenguaje simple y amigable
6. NO inventes información que no esté en el contexto

CONTEXTO DEL MANUAL:
{context_text}

PREGUNTA DEL USUARIO: {query}

RESPUESTA (breve y clara):"""

    # Intentar con diferentes modelos disponibles
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',  
        'gemini-pro'
    ]
    
    for model in models_to_try:
        try:
            # Incluir API key en la URL (método alternativo)
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
            headers = {
                'Content-Type': 'application/json'
            }
            payload = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }]
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                candidates = result.get('candidates', [])

                if candidates:
                    candidate = candidates[0]
                    content = candidate.get('content', {})
                    parts = content.get('parts', [])
                    
                    if parts:
                        text = parts[0].get('text', '')
                        if text:
                            logger.info(f'✅ Modelo {model} funcionó')
                            return text, None
            
            # Si llegamos aquí, este modelo no funcionó
            logger.warning(f'Modelo {model} - Status {response.status_code}: {response.text[:200]}')
            
        except Exception as e:
            logger.warning(f'Modelo {model} falló: {e}')
            continue
    
    # FALLBACK: Si la API no funciona, generar respuesta básica desde el contexto
    logger.warning('⚠️ API de Gemini no disponible, usando respuesta basada en contexto')
    
    # Extraer información relevante del contexto
    lines = context_text.split('\n')
    relevant_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('```'):
            relevant_lines.append(line)
            if len('\n'.join(relevant_lines)) > 500:
                break
    
    fallback_response = '\n'.join(relevant_lines)
    return fallback_response, None


@method_decorator(csrf_exempt, name='dispatch')
class UploadDocumentView(View):
    """POST /api/rag/upload - Sube y procesa un documento"""

    def post(self, request):
        try:
            # Validar archivo
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No se envió archivo'}, status=400)

            file = request.FILES['file']
            title = request.POST.get('title', file.name)

            # Validar tipo
            if not file.name.lower().endswith('.pdf'):
                return JsonResponse({'error': 'Solo PDFs soportados'}, status=400)

            # Crear registro en BD
            collection = DocumentCollection.objects.create(
                user=request.user if request.user.is_authenticated else None,
                title=title,
                file=file,
                file_type='pdf',
                status='processing'
            )

            # Procesar en segundo plano (idealmente con Celery)
            # Por simplicidad, procesamos síncrono aquí
            try:
                self._process_document(collection)
                collection.status = 'indexed'
                collection.save()

                return JsonResponse({
                    'collection_id': collection.id,
                    'title': collection.title,
                    'status': collection.status,
                    'chunk_count': collection.chunk_count,
                    'page_count': collection.page_count
                }, status=201)

            except Exception as e:
                collection.status = 'error'
                collection.error_message = str(e)
                collection.save()
                raise

        except Exception as e:
            logger.exception('Error en upload')
            return JsonResponse({'error': str(e)}, status=500)

    def _process_document(self, collection: DocumentCollection):
        """Procesa documento: extrae texto, genera chunks, embeddings"""
        # 1. Cargar PDF
        loader = DocumentLoader(use_ocr=False)
        file_path = collection.file.path
        pages_data, total_pages = loader.load_pdf(file_path)

        collection.page_count = total_pages
        collection.save()

        # 2. Generar chunks
        chunks = loader.chunk_text(pages_data, chunk_size=500, overlap=50)

        # 3. Generar embeddings
        generator = get_embedding_generator()
        texts = [chunk['content'] for chunk in chunks]
        embeddings = generator.encode_documents(texts, show_progress=True)

        # 4. Guardar en BD
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            DocumentChunk.objects.create(
                collection=collection,
                chunk_index=idx,
                content=chunk['content'],
                embedding=embedding.tolist(),
                metadata=chunk['metadata']
            )

        collection.chunk_count = len(chunks)
        collection.save()

        logger.info(f"Documento procesado: {len(chunks)} chunks indexados")


@method_decorator(csrf_exempt, name='dispatch')
class QueryRAGView(View):
    """POST /api/rag/query - Consulta con RAG"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            collection_id = data.get('collection_id')
            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)  # Aumentado de 3 a 5 para mejor contexto

            if not query:
                return JsonResponse({'error': 'Query vacío'}, status=400)

            if not collection_id:
                return JsonResponse({'error': 'collection_id requerido'}, status=400)

            # Verificar colección
            try:
                collection = DocumentCollection.objects.get(id=collection_id)
            except DocumentCollection.DoesNotExist:
                return JsonResponse({'error': 'Colección no encontrada'}, status=404)

            if collection.status != 'indexed':
                return JsonResponse({
                    'error': f'Colección no lista (status: {collection.status})'
                }, status=400)

            # 1. Generar embedding de la query
            generator = get_embedding_generator()
            query_vector = generator.encode_query(query)

            # 2. Buscar chunks similares
            vector_store = DatabaseVectorStore(collection_id, generator.dimension)
            results = vector_store.search(query_vector, k=top_k)

            if not results:
                return JsonResponse({
                    'answer': 'No encontré información relevante en el manual.',
                    'sources': []
                })

            # 3. Generar respuesta con Google API
            answer, error = _call_google_api_with_context(query, results)

            if error:
                return JsonResponse({'error': error}, status=500)

            # 4. Guardar query en historial
            chunk_ids = [r['metadata']['chunk_id'] for r in results]
            if request.user.is_authenticated:
                RAGQuery.objects.create(
                    user=request.user,
                    collection=collection,
                    query=query,
                    response=answer,
                    chunks_used=chunk_ids
                )

            # 5. Preparar fuentes
            # No mostrar fuentes al usuario
            return JsonResponse({
                'answer': answer,
                'collection_title': collection.title
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            logger.exception('Error en query RAG')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ListDocumentsView(View):
    """GET /api/rag/documents - Lista documentos del usuario"""

    def get(self, request):
        try:
            collections = DocumentCollection.objects.all()

            data = [
                {
                    'id': c.id,
                    'title': c.title,
                    'status': c.status,
                    'page_count': c.page_count,
                    'chunk_count': c.chunk_count,
                    'created_at': c.created_at.isoformat(),
                    'error': c.error_message
                }
                for c in collections
            ]

            return JsonResponse({'documents': data})

        except Exception as e:
            logger.exception('Error listando documentos')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteDocumentView(View):
    """DELETE /api/rag/document/<id> - Elimina documento y chunks"""

    def delete(self, request, collection_id):
        try:
            collection = DocumentCollection.objects.get(id=collection_id)

            title = collection.title
            collection.delete()  # Cascada elimina chunks también

            return JsonResponse({
                'message': f'Documento "{title}" eliminado correctamente'
            })

        except DocumentCollection.DoesNotExist:
            return JsonResponse({'error': 'Documento no encontrado'}, status=404)
        except Exception as e:
            logger.exception('Error eliminando documento')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class QueryHistoryView(View):
    """GET /api/rag/history - Historial de consultas del usuario"""

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 20))
            queries = RAGQuery.objects.all()[:limit]

            data = [
                {
                    'id': q.id,
                    'query': q.query,
                    'response': q.response[:200] + '...',
                    'collection': q.collection.title if q.collection else None,
                    'created_at': q.created_at.isoformat()
                }
                for q in queries
            ]

            return JsonResponse({'history': data})

        except Exception as e:
            logger.exception('Error obteniendo historial')
            return JsonResponse({'error': str(e)}, status=500)


def view_manual_pdf(request):
    """Vista para mostrar el PDF del manual en el navegador (sin descargar)"""
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings
    
    # Ruta al PDF del manual
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'rag_documents', 'manual_usuario.pdf')
    
    if not os.path.exists(pdf_path):
        raise Http404("El manual no está disponible")
    
    # Servir el archivo para visualizarlo en el navegador
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Manual_Usuario_Bar_Galileo.pdf"'
    
    return response


def download_manual_view(request):
    """Vista para descargar el manual de usuario en PDF"""
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings
    
    # Ruta al PDF del manual
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'rag_documents', 'manual_usuario.pdf')
    
    if not os.path.exists(pdf_path):
        raise Http404("El manual no está disponible")
    
    # Servir el archivo para descargarlo
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Manual_Usuario_Bar_Galileo.pdf"'
    
    return response


def view_manual_page(request):
    """Vista HTML que muestra el manual convertido a HTML"""
    import os
    import markdown
    from django.conf import settings
    
    # Leer el archivo markdown
    manual_path = os.path.join(settings.BASE_DIR.parent, 'docs', 'manual_usuario.md')
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_md = f.read()
        
        # Convertir markdown a HTML
        manual_html = markdown.markdown(manual_md, extensions=['extra', 'codehilite'])
    except FileNotFoundError:
        manual_html = "<h1>Manual no disponible</h1><p>El archivo del manual no se encontró.</p>"
    
    return render(request, 'rag_chat/manual.html', {'manual_html': manual_html})


def edit_manual(request):
    """Vista para editar el manual de usuario (solo administradores)"""
    import os
    from django.conf import settings
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.contrib.auth.decorators import user_passes_test
    
    # Solo staff y superusuarios pueden editar
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para editar el manual.')
        return redirect('rag_chat:view_manual')
    
    # Ruta al archivo markdown del manual
    manual_path = os.path.join(settings.BASE_DIR.parent, 'docs', 'manual_usuario.md')
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        # Validar contenido
        if len(content.strip()) < 100:
            messages.error(request, 'El contenido del manual es demasiado corto.')
            return render(request, 'rag_chat/edit_manual.html', {'content': content})
        
        try:
            # Guardar el archivo markdown
            with open(manual_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Intentar regenerar el PDF
            try:
                from .document_loader import convert_markdown_to_pdf
                pdf_path = os.path.join(settings.MEDIA_ROOT, 'rag_documents', 'manual_usuario.pdf')
                convert_markdown_to_pdf(manual_path, pdf_path)
                messages.success(request, 'Manual actualizado correctamente. El PDF ha sido regenerado.')
            except Exception as pdf_error:
                logger.warning(f"No se pudo regenerar el PDF: {pdf_error}")
                messages.success(request, 'Manual actualizado correctamente. El PDF no se pudo regenerar automáticamente.')
            
            return redirect('rag_chat:view_manual')
            
        except Exception as e:
            logger.error(f"Error al guardar el manual: {e}")
            messages.error(request, f'Error al guardar el manual: {str(e)}')
            return render(request, 'rag_chat/edit_manual.html', {'content': content})
    
    # GET - Mostrar formulario de edición
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        messages.error(request, 'No se encontró el archivo del manual.')
        content = '# Manual de Usuario\n\nEl archivo del manual no existe.'
    except Exception as e:
        logger.error(f"Error al leer el manual: {e}")
        messages.error(request, f'Error al leer el manual: {str(e)}')
        content = ''
    
    return render(request, 'rag_chat/edit_manual.html', {'content': content})

