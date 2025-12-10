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
    return render(request, 'rag_chat/chat.html')


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
        f"[Página {c['metadata'].get('source_pages', ['?'])[0]}] {c['metadata']['content']}"
        for c in context_chunks
    ])

    prompt = f"""Basándote en la siguiente información del manual de usuario, responde la pregunta del usuario.
Si la respuesta no está en el contexto, indícalo claramente.

CONTEXTO:
{context_text}

PREGUNTA: {query}

RESPUESTA:"""

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    payload = {
        'contents': [{
            'parts': [{'text': prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return None, f'Error API: {response.status_code} - {response.text}'

        result = response.json()

        # Extraer respuesta del formato de Google Gemini
        candidates = result.get('candidates', [])

        if not candidates:
            return None, 'No se recibieron candidatos en la respuesta'

        candidate = candidates[0]
        content = candidate.get('content', {})
        parts = content.get('parts', [])

        if not parts:
            return None, 'No se encontraron partes en la respuesta'

        text = parts[0].get('text', '')

        if not text:
            return None, 'La respuesta no contiene texto'

        return text, None

    except Exception as e:
        logger.exception('Error llamando a Google API')
        return None, str(e)


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
            top_k = data.get('top_k', 3)

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
            vector_store = DatabaseVectorStore(collection_id, generator.get_dimension())
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
            sources = [
                {
                    'content': r['metadata']['content'][:200] + '...',
                    'page': r['metadata'].get('source_pages', []),
                    'similarity': round(r['similarity'], 3)
                }
                for r in results
            ]

            return JsonResponse({
                'answer': answer,
                'sources': sources,
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
            
            # Eliminar el archivo físico si existe
            if collection.file:
                try:
                    file_path = collection.file.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f'Archivo eliminado: {file_path}')
                except Exception as file_error:
                    logger.warning(f'No se pudo eliminar el archivo: {file_error}')
            
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
