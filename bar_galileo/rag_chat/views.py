"""
RAG Chat Views - Endpoints para upload, indexación y consultas RAG
"""

import json
import logging
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .document_loader import DocumentLoader
from .embeddings import get_embedding_generator

from .vector_store import DatabaseVectorStore

logger = logging.getLogger(__name__)


def chat_view(request):
    """Vista principal del chat RAG"""
    return render(request, "rag_chat/chat.html")


# ─────────────────────────────────────────────
#  PROMPT ÚNICO compartido por todos los modelos
# ─────────────────────────────────────────────

def _build_prompt(query: str, context_text: str) -> str:
    return f"""Eres el asistente virtual del bar Galileo. Tu única función es ayudar a los usuarios con el sistema de gestión del bar.

QUIÉN ERES:
- Si alguien te pregunta qué eres o quién eres, responde que eres el asistente del bar Galileo, listo para ayudarles con el sistema.

CÓMO RESPONDER:
- Si te preguntan por el filtro avanzado o vas a usar el termino "AND" u "OR" cambialos por sus equivalentes en español segun lo requiera el contexto.
- Responde siempre en español, de forma breve, directa y amigable. Máximo 3-4 oraciones salvo que el tema lo requiera.
- Habla de forma natural, como si le explicaras algo a un compañero de trabajo.
- Nunca uses palabras en inglés dentro de las explicaciones. Usa "Y" en vez de "AND", "O" en vez de "OR", "Aplicar" en vez de "Apply", "Datos" en vez de "Data", etc.
- Evita listas largas y pasos numerados interminables. Prefiere explicar en frases fluidas y naturales.
- Si el usuario escribe algo vago como "ayuda", "no funciona" o un mensaje muy corto, pregúntale con amabilidad qué está intentando hacer.
- Si necesitas más información para ayudar, haz solo una pregunta concreta, no varias a la vez.

TEMAS FUERA DEL SISTEMA:
- Si alguien pregunta algo que no tiene que ver con el bar Galileo ni con el sistema, dile amablemente que no estás capacitado para eso, pero relaciona su consulta con algo que sí puedas ayudarle dentro del sistema.
- Ejemplo: si alguien dice "necesito comprar mesas", responde algo como: "No estoy capacitado para temas de compras externas, pero si quieres te explico cómo registrar productos o gestionar el inventario del bar."
- Siempre termina ofreciendo ayuda con algo del sistema del bar Galileo.

LIMITACIONES:
- Solo usa la información del manual de usuario proporcionado como contexto.
- Si la respuesta no está en el manual, dilo con amabilidad y sugiere qué módulo o sección podría ser útil revisar.

CONTEXTO DEL MANUAL:
{context_text}

PREGUNTA DEL USUARIO:
{query}

RESPUESTA:"""


def _call_google_api_with_context(query: str, context_chunks: list) -> tuple:
    """
    Llama a Google Gemini API con contexto de documentos.

    Args:
        query: Pregunta del usuario
        context_chunks: Lista de chunks relevantes

    Returns:
        tuple: (respuesta, error)
    """
    import requests

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None, "GOOGLE_API_KEY no configurada"

    context_text = "\n\n".join(
        [
            f"[Página {c['metadata'].get('source_pages', ['?'])[0]}] {c['metadata']['content']}"
            for c in context_chunks
        ]
    )

    prompt = _build_prompt(query, context_text)

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return None, f"Error API: {response.status_code} - {response.text}"

        result = response.json()
        candidates = result.get("candidates", [])

        if not candidates:
            return None, "No se recibieron candidatos en la respuesta"

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            return None, "No se encontraron partes en la respuesta"

        text = parts[0].get("text", "")

        if not text:
            return None, "La respuesta no contiene texto"

        return text, None

    except Exception as e:
        logger.exception("Error llamando a Google API")
        return None, str(e)


def _call_deepseek_api_with_context(query: str, context_chunks: list) -> tuple:
    """
    Llama a DeepSeek API con contexto de documentos.

    Args:
        query: Pregunta del usuario
        context_chunks: Lista de chunks relevantes

    Returns:
        tuple: (respuesta, error)
    """
    import requests

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None, "DEEPSEEK_API_KEY no configurada"

    context_text = "\n\n".join(
        [
            f"[Página {c['metadata'].get('source_pages', ['?'])[0]}] {c['metadata']['content']}"
            for c in context_chunks
        ]
    )

    prompt = _build_prompt(query, context_text)

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return None, f"Error API: {response.status_code} - {response.text}"

        result = response.json()
        choices = result.get("choices", [])
        if not choices:
            return None, "No se recibieron respuestas de DeepSeek"

        message = choices[0].get("message", {})
        text = message.get("content", "")

        if not text:
            return None, "La respuesta de DeepSeek está vacía"

        return text, None

    except Exception as e:
        logger.exception("Error llamando a DeepSeek API")
        return None, str(e)


def call_llm_with_context(provider: str, query: str, context_chunks: list) -> tuple:
    """
    Llama al proveedor LLM seleccionado con el contexto dado.

    Args:
        provider: "google" o "deepseek"
        query: Pregunta del usuario
        context_chunks: Lista de chunks relevantes

    Returns:
        tuple: (respuesta, error)
    """
    if provider == "deepseek":
        return _call_deepseek_api_with_context(query, context_chunks)
    # Por defecto usa Google Gemini
    return _call_google_api_with_context(query, context_chunks)


@method_decorator(csrf_exempt, name="dispatch")
# Lógica de subida de documentos eliminada: el sistema ahora usa un manual fijo en static/manual/manual.pdf


@method_decorator(csrf_exempt, name="dispatch")
class QueryRAGView(View):
    """POST /api/rag/query - Consulta con RAG"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            query = data.get("query", "").strip()
            top_k = data.get("top_k", 3)

            if not query:
                return JsonResponse({"error": "Consulta vacía"}, status=400)

            # Usar manual fijo
            from .manual_rag import search_manual

            results, query_vector = search_manual(query, top_k=top_k)

            if not results:
                return JsonResponse(
                    {
                        "answer": "No encontré información relevante en el manual.",
                        "sources": [],
                    }
                )

            # Generar respuesta con el proveedor LLM seleccionado
            provider = os.getenv("LLM_PROVIDER", "google")
            answer, error = call_llm_with_context(provider, query, results)

            if error:
                return JsonResponse({"error": error}, status=500)

            # Preparar fuentes
            sources = [
                {
                    "content": r["metadata"]["content"][:200] + "...",
                    "page": r["metadata"].get("source_pages", []),
                    "similarity": round(r["similarity"], 3),
                }
                for r in results
            ]

            return JsonResponse(
                {
                    "answer": answer,
                    "sources": sources,
                    "collection_title": "Manual fijo",
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            logger.exception("Error en query RAG")
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ListDocumentsView(View):
    """GET /api/rag/documents - Lista documentos del usuario"""

    def get(self, request):
        try:
            collections = DocumentCollection.objects.all()

            data = [
                {
                    "id": c.id,
                    "title": c.title,
                    "status": c.status,
                    "page_count": c.page_count,
                    "chunk_count": c.chunk_count,
                    "created_at": c.created_at.isoformat(),
                    "error": c.error_message,
                }
                for c in collections
            ]

            return JsonResponse({"documents": data})

        except Exception as e:
            logger.exception("Error listando documentos")
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
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
                        logger.info(f"Archivo eliminado: {file_path}")
                except Exception as file_error:
                    logger.warning(f"No se pudo eliminar el archivo: {file_error}")

            collection.delete()  # Cascada elimina chunks también

            return JsonResponse(
                {"message": f'Documento "{title}" eliminado correctamente'}
            )

        except DocumentCollection.DoesNotExist:
            return JsonResponse({"error": "Documento no encontrado"}, status=404)
        except Exception as e:
            logger.exception("Error eliminando documento")
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class QueryHistoryView(View):
    """GET /api/rag/history - Historial de consultas del usuario"""

    def get(self, request):
        try:
            limit = int(request.GET.get("limit", 20))
            queries = RAGQuery.objects.all()[:limit]

            data = [
                {
                    "id": q.id,
                    "query": q.query,
                    "response": q.response[:200] + "...",
                    "collection": q.collection.title if q.collection else None,
                    "created_at": q.created_at.isoformat(),
                }
                for q in queries
            ]

            return JsonResponse({"history": data})

        except Exception as e:
            logger.exception("Error obteniendo historial")
            return JsonResponse({"error": str(e)}, status=500)
