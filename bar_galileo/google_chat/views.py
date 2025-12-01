import os
import json
import logging
import requests
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)


def _call_google_api(messages_history):
    """
    Llamada a Google Generative Language API con historial completo.

    Args:
        messages_history: Lista de dict con formato [{'role': 'user', 'content': '...'}, ...]

    Returns:
        tuple: (respuesta_texto, error_mensaje)
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None, 'GOOGLE_API_KEY no configurada en .env'

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }

    # Convertir historial al formato de Google API
    # Google usa 'user' y 'model', no 'assistant'
    contents = []
    for msg in messages_history:
        role = 'model' if msg['role'] == 'model' else 'user'
        contents.append({
            'role': role,
            'parts': [{'text': msg['content']}]
        })

    payload = {'contents': contents}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            error_msg = f'Error {response.status_code}: {response.text}'
            logger.error(f'Google API error: {error_msg}')
            return None, error_msg

        result = response.json()
        candidates = result.get('candidates', [])

        if candidates and 'content' in candidates[0]:
            parts = candidates[0]['content'].get('parts', [])
            if parts and 'text' in parts[0]:
                return parts[0]['text'], None

        return None, 'No se recibió respuesta válida del modelo'

    except requests.RequestException as e:
        logger.exception('Error en petición a Google API')
        return None, f'Error de red: {str(e)}'
    except Exception as e:
        logger.exception('Error inesperado')
        return None, f'Error: {str(e)}'


@method_decorator(csrf_exempt, name='dispatch')
class CreateSessionView(LoginRequiredMixin, View):
    """POST /api/chat/create - Crear nueva sesión de chat"""

    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else {}
            title = data.get('title', 'Nueva conversación')

            session = ChatSession.objects.create(
                user=request.user,
                title=title
            )

            return JsonResponse({
                'session_id': session.id,
                'title': session.title,
                'created_at': session.created_at.isoformat()
            }, status=201)

        except Exception as e:
            logger.exception('Error creando sesión')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(LoginRequiredMixin, View):
    """POST /api/chat/send - Enviar mensaje con contexto"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({'error': 'Mensaje vacío'}, status=400)

            if not session_id:
                return JsonResponse({'error': 'session_id requerido'}, status=400)

            # Verificar que la sesión pertenece al usuario
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return JsonResponse({'error': 'Sesión no encontrada'}, status=404)

            # Guardar mensaje del usuario
            user_msg = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message
            )

            # Obtener historial completo para contexto
            history = list(session.messages.values('role', 'content'))

            # Llamar a Google API con todo el historial
            reply, error = _call_google_api(history)

            if error:
                return JsonResponse({'error': error}, status=500)

            # Guardar respuesta del modelo
            model_msg = ChatMessage.objects.create(
                session=session,
                role='model',
                content=reply
            )

            return JsonResponse({
                'session_id': session.id,
                'user_message': {
                    'id': user_msg.id,
                    'content': user_msg.content,
                    'created_at': user_msg.created_at.isoformat()
                },
                'model_response': {
                    'id': model_msg.id,
                    'content': model_msg.content,
                    'created_at': model_msg.created_at.isoformat()
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            logger.exception('Error enviando mensaje')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class GetHistoryView(LoginRequiredMixin, View):
    """GET /api/chat/history/<session_id> - Obtener historial de conversación"""

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)

            messages = [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in session.messages.all()
            ]

            return JsonResponse({
                'session_id': session.id,
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'messages': messages
            })

        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Sesión no encontrada'}, status=404)
        except Exception as e:
            logger.exception('Error obteniendo historial')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ListSessionsView(LoginRequiredMixin, View):
    """GET /api/chat/sessions - Listar todas las sesiones del usuario"""

    def get(self, request):
        try:
            sessions = ChatSession.objects.filter(user=request.user)

            data = [
                {
                    'id': s.id,
                    'title': s.title,
                    'created_at': s.created_at.isoformat(),
                    'updated_at': s.updated_at.isoformat(),
                    'message_count': s.messages.count()
                }
                for s in sessions
            ]

            return JsonResponse({'sessions': data})

        except Exception as e:
            logger.exception('Error listando sesiones')
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ClearSessionView(LoginRequiredMixin, View):
    """DELETE /api/chat/clear/<session_id> - Eliminar sesión y su historial"""

    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.delete()

            return JsonResponse({'message': 'Sesión eliminada correctamente'})

        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Sesión no encontrada'}, status=404)
        except Exception as e:
            logger.exception('Error eliminando sesión')
            return JsonResponse({'error': str(e)}, status=500)