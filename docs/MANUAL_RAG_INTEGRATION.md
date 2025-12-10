# Integración del Manual de Usuario con el Chatbot RAG

## 📖 Resumen

El sistema Bar Galileo ahora cuenta con un **Manual de Usuario completo** integrado con el **chatbot de ayuda RAG** (Retrieval-Augmented Generation). Esto permite que los usuarios consulten información del manual de forma conversacional usando inteligencia artificial.

---

## 🎯 Características Implementadas

### 1. Manual de Usuario Completo (`docs/manual_usuario.md`)
✅ Documentación exhaustiva de todo el sistema  
✅ 18 secciones que cubren:
- Introducción y público objetivo
- Acceso y autenticación
- Todos los módulos del sistema
- Procedimientos paso a paso
- Mensajes de error y soluciones
- Preguntas frecuentes (FAQs)
- Glosario de términos

### 2. Script de Inicialización (`rag_chat/initialize_manual.py`)
✅ Convierte el manual de Markdown a PDF  
✅ Carga automáticamente el manual en el sistema RAG  
✅ Indexa el contenido para búsquedas semánticas  
✅ Genera embeddings con IA

### 3. Integración con Chatbot
✅ Carga automática del Manual de Usuario al abrir el chat  
✅ Priorización del manual como fuente principal  
✅ Prompt mejorado para respuestas más claras  
✅ Interfaz actualizada con información contextual

---

## 🚀 Instalación y Configuración

### Paso 1: Instalar Dependencias

El sistema RAG requiere librerías adicionales para procesar PDFs y generar embeddings:

```powershell
# Activar el entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias para conversión de Markdown a PDF
pip install markdown weasyprint

# Instalar dependencias para RAG (si aún no están instaladas)
pip install sentence-transformers pypdf2 numpy
```

**Nota**: Si `weasyprint` da problemas en Windows, puedes:
- Usar un convertidor online para convertir `docs/manual_usuario.md` a PDF
- O instalar usando: `pip install --upgrade weasyprint`

### Paso 2: Configurar la API de Google

El chatbot usa Google Gemini para generar respuestas. Necesitas una API Key:

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API Key
3. Agrega la key en el archivo `.env`:

```env
GOOGLE_API_KEY=tu_api_key_aqui
```

### Paso 3: Inicializar el Manual en el Sistema RAG

Ejecuta el script de inicialización:

```powershell
cd bar_galileo
python manage.py shell
```

Dentro del shell de Django:

```python
exec(open('rag_chat/initialize_manual.py').read())
```

O alternativamente:

```powershell
python -c "exec(open('bar_galileo/rag_chat/initialize_manual.py').read())"
```

El script realizará:
- ✅ Conversión del manual a PDF (si no existe)
- ✅ Carga del PDF en el sistema
- ✅ Extracción de texto (múltiples páginas)
- ✅ Generación de fragmentos (chunks)
- ✅ Creación de embeddings con IA
- ✅ Indexación en la base de datos

**Tiempo estimado**: 3-10 minutos dependiendo del tamaño del manual.

### Paso 4: Verificar la Instalación

1. Inicia el servidor:
```powershell
cd bar_galileo
python manage.py runserver
```

2. Accede al chatbot:
```
http://localhost:8000/rag-chat/
```

3. Deberías ver:
   - ✅ "Manual de Usuario cargado y listo"
   - El manual seleccionado automáticamente en el dropdown
   - Campo de texto habilitado

4. Prueba haciendo una pregunta:
   - "¿Cómo creo un nuevo producto?"
   - "¿Qué permisos tiene el rol de mesero?"
   - "¿Cómo genero un reporte de ventas?"

---

## 💬 Uso del Chatbot

### Acceso
Hay 3 formas de acceder al chatbot:

1. **URL directa**: `/rag-chat/`
2. **Menú lateral**: Sección "Ayuda"
3. **Botón flotante**: (próximamente) en todas las páginas

### Tipos de Preguntas Soportadas

#### ✅ Procedimientos
- "¿Cómo facturo un pedido?"
- "¿Cómo agrego un nuevo empleado?"
- "¿Cómo genero un backup?"

#### ✅ Información de Módulos
- "¿Qué es el módulo de facturación?"
- "¿Para qué sirve el sistema de reportes?"

#### ✅ Permisos y Roles
- "¿Qué puede hacer un mesero?"
- "¿Quién puede crear usuarios?"

#### ✅ Solución de Errores
- "¿Qué significa 'stock no puede ser negativo'?"
- "¿Cómo soluciono el error de sesión expirada?"

#### ✅ Información General
- "¿Cómo inicio sesión?"
- "¿El sistema funciona sin internet?"

### Respuestas del Chatbot

El chatbot proporcionará:
- 📝 Respuestas estructuradas con pasos numerados
- 📚 Referencias al manual cuando sea apropiado
- ⚠️ Advertencias de permisos necesarios
- 💡 Tips y mejores prácticas
- 🔍 Fuentes del manual consultadas

---

## 🔄 Actualización del Manual

Cuando hagas cambios importantes al sistema:

### 1. Actualizar el Archivo Markdown

Edita `docs/manual_usuario.md` con:
- Nuevas funcionalidades
- Cambios en procedimientos
- Nuevos mensajes de error
- FAQs adicionales

### 2. Reinicializar en el Sistema RAG

```powershell
cd bar_galileo
python manage.py shell
```

```python
# Dentro del shell de Django
exec(open('rag_chat/initialize_manual.py').read())
```

Cuando se te pregunte si deseas eliminar el manual anterior, responde `s` (sí).

### 3. Verificar Cambios

Haz preguntas al chatbot sobre las nuevas funcionalidades para verificar que las respuestas reflejen los cambios.

---

## 🛠️ Mantenimiento

### Ver Documentos Indexados

```python
from rag_chat.models import DocumentCollection

# Listar todos los documentos
docs = DocumentCollection.objects.all()
for doc in docs:
    print(f"ID: {doc.id}, Título: {doc.title}, Estado: {doc.status}")
    print(f"Páginas: {doc.page_count}, Chunks: {doc.chunk_count}")
```

### Eliminar Manual Antiguo

```python
from rag_chat.models import DocumentCollection

# Buscar y eliminar
manual = DocumentCollection.objects.filter(title__icontains='Manual de Usuario').first()
if manual:
    manual.delete()
    print(f"Manual '{manual.title}' eliminado")
```

### Ver Historial de Consultas

```python
from rag_chat.models import RAGQuery

# Últimas 10 consultas
queries = RAGQuery.objects.all()[:10]
for q in queries:
    print(f"Usuario: {q.user.username}")
    print(f"Pregunta: {q.query}")
    print(f"Respuesta: {q.response[:100]}...")
    print("---")
```

---

## 📊 Estadísticas y Métricas

### Fragmentos (Chunks) Generados
El manual se divide en fragmentos de ~500 caracteres con superposición de 50. Esto permite:
- Búsquedas más precisas
- Respuestas contextuales
- Menor uso de tokens

### Embeddings
Cada fragmento tiene un vector de embeddings (768 dimensiones por defecto) que permite:
- Búsqueda semántica (no solo palabras clave)
- Comprensión de sinónimos
- Búsqueda de conceptos relacionados

---

## 🔧 Solución de Problemas

### Error: "GOOGLE_API_KEY no configurada"
**Solución**: Agrega tu API key en el archivo `.env`

### Error: "No se pudo convertir a PDF"
**Solución**: 
1. Instala las dependencias: `pip install markdown weasyprint`
2. O convierte manualmente el markdown a PDF y colócalo en `media/rag_documents/manual_usuario.pdf`

### Error: "No se encontró el manual en..."
**Solución**: Verifica que existe el archivo `docs/manual_usuario.md`

### Chatbot no responde correctamente
**Posibles causas**:
1. El manual no está indexado (verifica en `/rag-chat/api/documents/`)
2. La API de Google no está respondiendo
3. El manual no contiene información sobre esa pregunta

**Solución**: Actualiza el manual con más información y reinicializa.

### Respuestas lentas
**Causa**: Generación de embeddings y llamada a la API de Google
**Solución**: Es normal. Respuestas típicas toman 2-5 segundos.

---

## 🎓 Mejores Prácticas

### Para Usuarios
- ✅ Haz preguntas específicas y claras
- ✅ Usa términos del sistema (módulos, funciones)
- ✅ Si la respuesta no es clara, reformula la pregunta
- ✅ Revisa las "fuentes" que el chatbot proporciona

### Para Administradores
- ✅ Mantén el manual actualizado con cada cambio importante
- ✅ Agrega FAQs basadas en preguntas frecuentes de usuarios
- ✅ Reindexa el manual después de actualizaciones grandes
- ✅ Monitorea el historial de consultas para identificar gaps en la documentación

### Para Desarrolladores
- ✅ Documenta nuevas funcionalidades en el manual antes del deployment
- ✅ Incluye ejemplos de uso y casos edge
- ✅ Agrega mensajes de error a la sección correspondiente
- ✅ Usa un lenguaje claro y no técnico en el manual

---

## 📚 Recursos Adicionales

### Archivos Clave
- `docs/manual_usuario.md` - Manual en Markdown
- `rag_chat/initialize_manual.py` - Script de inicialización
- `rag_chat/views.py` - Lógica del chatbot
- `rag_chat/models.py` - Modelos de datos RAG
- `static/js/rag_chat/chat.js` - Frontend del chatbot

### Documentación Relacionada
- [Google Gemini API](https://ai.google.dev/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [WeasyPrint](https://weasyprint.org/)

---

## 🚦 Estado del Sistema

### ✅ Completado
- [x] Manual de usuario completo
- [x] Script de inicialización
- [x] Integración con chatbot
- [x] Carga automática del manual
- [x] Mejoras en prompts
- [x] Interfaz actualizada

### 🔄 Próximas Mejoras
- [ ] Botón flotante de ayuda en todas las páginas
- [ ] Soporte para más formatos (TXT, DOCX)
- [ ] Búsqueda en múltiples documentos simultáneamente
- [ ] Sugerencias de preguntas frecuentes
- [ ] Feedback de respuestas (útil/no útil)

---

## 📞 Soporte

Para problemas con el chatbot RAG o el manual:
1. Consulta este README
2. Revisa los logs del servidor
3. Contacta al administrador del sistema

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0  
**Autor**: Sistema Bar Galileo
