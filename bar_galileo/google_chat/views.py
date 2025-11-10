import os
import json
import logging
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def chat_view(request):
    """Vista principal con el formulario de chat"""
    return render(request, 'google_chat/index.html')


def _call_google_api(message):
    """Llamada a Google Generative Language API"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None, 'GOOGLE_API_KEY no configurada en .env'

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    payload = {
        'contents': [{
            'parts': [{'text': message}]
        }]
    }

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


@require_POST
@csrf_exempt
def send_message(request):
    """Endpoint para enviar mensaje a Google Gemini API"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

        reply, error = _call_google_api(message)

        if error:
            return JsonResponse({'error': error}, status=500)

        return JsonResponse({'reply': reply})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.exception('Error inesperado en send_message')
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
