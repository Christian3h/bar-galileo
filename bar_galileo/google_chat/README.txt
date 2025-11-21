===========================================
  GOOGLE CHAT API - ENDPOINTS
===========================================

Integración con Google Generative Language API (Gemini 2.0 Flash)
con memoria/contexto persistente en base de datos.

-------------------------------------------
CONFIGURACIÓN
-------------------------------------------
Variable de entorno requerida en .env:
  GOOGLE_API_KEY=tu_clave_aqui

-------------------------------------------
ENDPOINTS DISPONIBLES
-------------------------------------------

1. CREAR NUEVA SESIÓN
   POST /google-chat/api/create/

   Body (opcional):
   {
     "title": "Nombre de la conversación"
   }

   Respuesta:
   {
     "session_id": 1,
     "title": "Nueva conversación",
     "created_at": "2025-11-11T10:30:00"
   }

-------------------------------------------

2. ENVIAR MENSAJE (CON CONTEXTO AUTOMÁTICO)
   POST /google-chat/api/send/

   Body:
   {
     "session_id": 1,
     "message": "Hola, cómo estás?"
   }

   Respuesta:
   {
     "session_id": 1,
     "user_message": {
       "id": 1,
       "content": "Hola, cómo estás?",
       "created_at": "2025-11-11T10:30:00"
     },
     "model_response": {
       "id": 2,
       "content": "¡Hola! Estoy bien...",
       "created_at": "2025-11-11T10:30:01"
     }
   }

-------------------------------------------

3. VER HISTORIAL DE UNA SESIÓN
   GET /google-chat/api/history/<session_id>/

   Ejemplo: GET /google-chat/api/history/1/

   Respuesta:
   {
     "session_id": 1,
     "title": "Mi conversación",
     "created_at": "2025-11-11T10:30:00",
     "messages": [
       {
         "id": 1,
         "role": "user",
         "content": "Hola",
         "created_at": "2025-11-11T10:30:00"
       },
       {
         "id": 2,
         "role": "model",
         "content": "¡Hola! ¿En qué puedo ayudarte?",
         "created_at": "2025-11-11T10:30:01"
       }
     ]
   }

-------------------------------------------

4. LISTAR TODAS LAS SESIONES DEL USUARIO
   GET /google-chat/api/sessions/

   Respuesta:
   {
     "sessions": [
       {
         "id": 1,
         "title": "Conversación 1",
         "created_at": "2025-11-11T10:30:00",
         "updated_at": "2025-11-11T11:00:00",
         "message_count": 10
       },
       {
         "id": 2,
         "title": "Otra conversación",
         "created_at": "2025-11-11T09:00:00",
         "updated_at": "2025-11-11T09:15:00",
         "message_count": 4
       }
     ]
   }

-------------------------------------------

5. ELIMINAR SESIÓN Y SU HISTORIAL
   DELETE /google-chat/api/clear/<session_id>/

   Ejemplo: DELETE /google-chat/api/clear/1/

   Respuesta:
   {
     "message": "Sesión eliminada correctamente"
   }

===========================================
CARACTERÍSTICAS
===========================================

✅ Memoria persistente: El historial se guarda en BD
✅ Contexto automático: Cada mensaje envía el historial completo
✅ Multi-sesión: Usuarios pueden tener múltiples conversaciones
✅ Seguridad: LoginRequiredMixin en todas las vistas
✅ Class-Based Views: Consistente con el resto del proyecto

===========================================
MODELOS
===========================================

ChatSession:
  - user (FK a User)
  - title (CharField)
  - created_at, updated_at (DateTimeField)

ChatMessage:
  - session (FK a ChatSession)
  - role ('user' o 'model')
  - content (TextField)
  - created_at (DateTimeField)

===========================================
EJEMPLO DE USO EN JAVASCRIPT
===========================================

// 1. Crear sesión
const session = await fetch('/google-chat/api/create/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({title: 'Mi chat'})
}).then(r => r.json());

const sessionId = session.session_id;

// 2. Enviar mensaje
const response = await fetch('/google-chat/api/send/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: sessionId,
    message: 'Hola, soy Christian'
  })
}).then(r => r.json());

console.log(response.model_response.content);

// 3. Siguiente mensaje (recordará el anterior)
const response2 = await fetch('/google-chat/api/send/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: sessionId,
    message: '¿Cómo me llamo?'
  })
}).then(r => r.json());

// Responderá: "Te llamas Christian"

===========================================
NOTAS IMPORTANTES
===========================================

1. El contexto se envía completo en cada petición
2. Google API tiene límite de tokens (~30K para Gemini 2.0 Flash)
3. Si el historial es muy largo, considera limpiar mensajes antiguos
4. CSRF está desactivado (@csrf_exempt) para facilitar APIs
5. Autenticación requerida (LoginRequiredMixin)
