===========================================
  RAG CHAT - Sistema de Q&A sobre Documentos
===========================================

Retrieval-Augmented Generation (RAG) para responder preguntas
basándose en documentos (manuales de usuario, PDFs, etc.).

*** IMPORTANTE: ESTE CÓDIGO ESTÁ CREADO PERO NO INSTALADO ***
*** SIGUE LOS PASOS DE INSTALACIÓN MÁS ABAJO ***

===========================================
¿QUÉ ES RAG Y CÓMO FUNCIONA?
===========================================

RAG = Retrieval-Augmented Generation

NO es un chat normal. Es un sistema que:

1. INDEXA documentos (tu manual de usuario en PDF)
2. Cuando preguntas algo, BUSCA en esos documentos
3. GENERA una respuesta basada en lo que encontró

EJEMPLO:
- Usuario: "¿Cómo crear un empleado?"
- Sistema:
  a) Busca en el PDF fragmentos sobre "crear empleado"
  b) Encuentra 3 párrafos relevantes (páginas 5, 8, 12)
  c) Se los pasa a Google Gemini como contexto
  d) Gemini responde basándose SOLO en esos fragmentos
  e) Usuario recibe respuesta + fuentes (páginas)

===========================================
ARQUITECTURA Y COMPONENTES
===========================================

1. INGESTA (document_loader.py)
   - Extrae texto de PDFs con PyMuPDF
   - Soporte OCR opcional con pytesseract
   - División en chunks con solapamiento

2. EMBEDDINGS (embeddings.py)
   - sentence-transformers (modelo multilingual)
   - Genera vectores de 384 dimensiones
   - Modelo: paraphrase-multilingual-MiniLM-L12-v2

3. BÚSQUEDA VECTORIAL (vector_store.py)
   - FAISS para búsqueda eficiente
   - Similitud coseno
   - Persistencia en BD (DocumentChunk)

4. GENERACIÓN (views.py)
   - Google Gemini 2.0 Flash
   - Prompt engineering con contexto
   - Respuestas fundamentadas en docs

===========================================
MODELOS DE BASE DE DATOS
===========================================

DocumentCollection:
  - Documento subido (PDF)
  - Estado: pending → processing → indexed
  - Cuenta de páginas y chunks

DocumentChunk:
  - Fragmento de texto (chunk)
  - Embedding vectorial (JSON)
  - Metadata: páginas, índice, etc.

RAGQuery:
  - Historial de consultas y respuestas
  - Trazabilidad de chunks usados

===========================================
ENDPOINTS API
===========================================

1. SUBIR DOCUMENTO
   POST /rag-chat/api/upload/

   Form-data:
     file: <archivo.pdf>
     title: "Manual de Usuario"

   Respuesta:
   {
     "collection_id": 1,
     "title": "Manual de Usuario",
     "status": "indexed",
     "chunk_count": 45,
     "page_count": 12
   }

   Nota: Procesa el PDF, genera chunks, embeddings
         y los indexa automáticamente.

-------------------------------------------

2. CONSULTAR CON RAG
   POST /rag-chat/api/query/

   Body:
   {
     "collection_id": 1,
     "query": "¿Cómo crear un nuevo empleado?",
     "top_k": 3
   }

   Respuesta:
   {
     "answer": "Para crear un nuevo empleado...",
     "sources": [
       {
         "content": "Fragmento relevante del manual...",
         "page": [5],
         "similarity": 0.892
       }
     ],
     "collection_title": "Manual de Usuario"
   }

   Flujo:
   1. Genera embedding de la pregunta
   2. Busca los 3 chunks más similares en FAISS
   3. Construye prompt con contexto
   4. Llama a Google API para generar respuesta
   5. Guarda en historial

-------------------------------------------

3. LISTAR DOCUMENTOS
   GET /rag-chat/api/documents/

   Respuesta:
   {
     "documents": [
       {
         "id": 1,
         "title": "Manual de Usuario",
         "status": "indexed",
         "page_count": 12,
         "chunk_count": 45,
         "created_at": "2025-11-13T10:00:00",
         "error": null
       }
     ]
   }

-------------------------------------------

4. ELIMINAR DOCUMENTO
   DELETE /rag-chat/api/document/<id>/

   Ejemplo: DELETE /rag-chat/api/document/1/

   Respuesta:
   {
     "message": "Documento 'Manual de Usuario' eliminado"
   }

-------------------------------------------

5. HISTORIAL DE CONSULTAS
   GET /rag-chat/api/history/?limit=20

   Respuesta:
   {
     "history": [
       {
         "id": 15,
         "query": "¿Cómo resetear contraseña?",
         "response": "Para resetear la contraseña...",
         "collection": "Manual de Usuario",
         "created_at": "2025-11-13T11:30:00"
       }
     ]
   }

===========================================
INSTALACIÓN Y CONFIGURACIÓN
===========================================

*** SIGUE ESTOS PASOS EN ORDEN ***

PASO 1: INSTALAR DEPENDENCIAS
------------------------------

Las dependencias ya están en requirements.txt, instálalas:

cd /home/christian/Documents/bar-galileo
pip install pymupdf sentence-transformers faiss-cpu numpy torch

Esto instalará:
- pymupdf: Lee PDFs
- sentence-transformers: Genera embeddings (vectores)
- faiss-cpu: Búsqueda vectorial rápida
- torch: Requerido por sentence-transformers

Tiempo estimado: 5-10 minutos (descarga ~1.5GB)

NOTA: Si tienes GPU, instala faiss-gpu en vez de faiss-cpu

PASO 2: MIGRAR BASE DE DATOS
-----------------------------

Crea las tablas en SQLite:

cd bar_galileo
python3 manage.py makemigrations rag_chat
python3 manage.py migrate

Esto crea 3 tablas:
- rag_chat_documentcollection: Documentos subidos
- rag_chat_documentchunk: Fragmentos con embeddings
- rag_chat_ragquery: Historial de consultas

PASO 3: VERIFICAR CONFIGURACIÓN
--------------------------------

La app ya está registrada en:
- INSTALLED_APPS (settings.py)
- URLs (bar_galileo/urls.py) como /rag-chat/

Verifica que GOOGLE_API_KEY esté en tu .env:
GOOGLE_API_KEY=tu_clave_aqui

PASO 4: REINICIAR SERVIDOR
---------------------------

Si el servidor estaba corriendo, reinícialo para que cargue
los nuevos módulos.

===========================================
PRIMER USO: INDEXAR UN DOCUMENTO
===========================================

Una vez instalado, el flujo es:

1. SUBIR PDF
------------

curl -X POST http://localhost:8000/rag-chat/api/upload/ \
  -F "file=@/ruta/a/manual_usuario.pdf" \
  -F "title=Manual de Usuario"

¿Qué pasa internamente?
a) Se guarda el PDF en media/rag_documents/
b) PyMuPDF extrae el texto de cada página
c) El texto se divide en chunks de ~500 palabras con solapamiento
d) sentence-transformers genera un vector de 384 números por cada chunk
e) Los vectores se guardan en la BD (tabla documentchunk)
f) Status cambia a "indexed"

Tiempo: ~30 segundos para un PDF de 50 páginas

Respuesta esperada:
{
  "collection_id": 1,
  "title": "Manual de Usuario",
  "status": "indexed",
  "chunk_count": 45,
  "page_count": 12
}

Si falla, revisa:
- Que el PDF no esté corrupto
- Logs del servidor para ver el error

2. HACER CONSULTA
-----------------

curl -X POST http://localhost:8000/rag-chat/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "collection_id": 1,
    "query": "¿Cómo crear un nuevo empleado?",
    "top_k": 3
  }'

¿Qué pasa internamente?
a) sentence-transformers genera vector de tu pregunta
b) FAISS busca los 3 chunks más similares (búsqueda vectorial)
c) Se construye un prompt con esos 3 fragmentos como contexto
d) Google Gemini genera la respuesta basándose en el contexto
e) Se guarda la query en el historial

Tiempo: ~2-3 segundos

Respuesta esperada:
{
  "answer": "Para crear un nuevo empleado, ve a...",
  "sources": [
    {
      "content": "Fragmento relevante del manual...",
      "page": [5],
      "similarity": 0.892
    },
    ...
  ],
  "collection_title": "Manual de Usuario"
}

===========================================
¿CÓMO FUNCIONA LA BASE VECTORIAL?
===========================================

NO ES UNA BASE DE DATOS SEPARADA.

Todo se guarda en tu SQLite/PostgreSQL normal:

1. EMBEDDINGS EN LA BD
-----------------------

Tabla: rag_chat_documentchunk

Cada registro tiene:
- content: "Para crear un empleado, navegue al menú..."
- embedding: [0.234, -0.891, 0.445, ..., 0.123] (384 números)
- metadata: {"source_pages": [5], "chunk_index": 12}

Los embeddings se guardan como JSON en la columna "embedding".

2. ÍNDICE FAISS EN MEMORIA
---------------------------

Cuando haces una consulta:

a) Se cargan TODOS los embeddings de la BD
b) Se construye un índice FAISS en RAM
c) FAISS hace la búsqueda rápida (similitud coseno)
d) Retorna los IDs de los chunks más similares
e) Se consultan esos chunks en la BD para obtener el texto

FAISS es solo para BÚSQUEDA RÁPIDA, no almacena nada.
Los datos reales están en tu BD de Django.

3. ¿POR QUÉ FAISS?
-------------------

Comparar tu pregunta con 1000 chunks uno por uno:
→ Lento (~5 segundos)

Comparar con FAISS:
→ Rápido (~50ms)

FAISS usa algoritmos optimizados para encontrar
los vectores más cercanos sin comparar todos.

===========================================
CONCEPTOS CLAVE EXPLICADOS
===========================================

EMBEDDING / VECTOR
------------------
Una lista de números que representa el SIGNIFICADO de un texto.

Ejemplo:
"crear empleado" → [0.2, -0.8, 0.4, ..., 0.1]
"agregar trabajador" → [0.19, -0.79, 0.41, ..., 0.09]

Estos dos vectores son SIMILARES porque el significado es parecido.

CHUNK
-----
Fragmento de texto. Como tu PDF tiene 50 páginas (mucho),
lo dividimos en pedazos de ~500 palabras.

¿Por qué? Porque Google Gemini tiene límite de tokens y
queremos darle solo lo relevante, no todo el PDF.

SIMILITUD COSENO
----------------
Mide qué tan "parecidos" son dos vectores.

Score 0.9 = muy similares (misma idea)
Score 0.3 = poco similares (temas distintos)

TOP_K
-----
"Dame los K fragmentos más similares"

top_k=3 → los 3 mejores chunks
top_k=5 → los 5 mejores chunks

Más chunks = más contexto pero más lento y más tokens usados.

PROMPT ENGINEERING
------------------
Cómo le hablamos a Google Gemini.

Malo:
"Pregunta: ¿Cómo crear empleado?"

Bueno:
"Basándote en este contexto del manual:
[fragmento 1]
[fragmento 2]
[fragmento 3]

Responde: ¿Cómo crear empleado?
Si no está en el contexto, di que no sabes."

===========================================

1. INSTALAR DEPENDENCIAS

   pip install pymupdf sentence-transformers faiss-cpu

   Opcional (OCR para PDFs escaneados):
   pip install pytesseract pillow
   apt-get install tesseract-ocr tesseract-ocr-spa

2. CONFIGURAR .env

   GOOGLE_API_KEY=tu_clave_aqui

3. MIGRAR BASE DE DATOS

   python manage.py makemigrations rag_chat
   python manage.py migrate

4. REGISTRAR EN SETTINGS.PY

   INSTALLED_APPS = [
       ...
       'rag_chat',
   ]

5. AGREGAR URLS (bar_galileo/urls.py)

   urlpatterns = [
       ...
       path('rag-chat/', include(('rag_chat.urls', 'rag_chat'), namespace='rag_chat')),
   ]

===========================================
EJEMPLO DE USO
===========================================

# 1. Subir manual de usuario
curl -X POST http://localhost:8000/rag-chat/api/upload/ \
  -F "file=@manual_usuario.pdf" \
  -F "title=Manual de Usuario v1.0"

# Respuesta: {"collection_id": 1, ...}

# 2. Hacer consulta
curl -X POST http://localhost:8000/rag-chat/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "collection_id": 1,
    "query": "¿Cómo crear un nuevo empleado en el sistema?",
    "top_k": 3
  }'

# 3. Ver historial
curl http://localhost:8000/rag-chat/api/history/

===========================================
AJUSTES AVANZADOS
===========================================

CAMBIAR MODELO DE EMBEDDINGS (embeddings.py):

  # En vez de 'multilingual', usa:
  generator = EmbeddingGenerator('large')  # Mejor calidad
  # o
  generator = EmbeddingGenerator('mini')   # Más rápido

AJUSTAR CHUNK SIZE (document_loader.py):

  chunks = loader.chunk_text(
      pages_data,
      chunk_size=800,  # Más contexto por chunk
      overlap=100      # Mayor solapamiento
  )

MEJORAR BÚSQUEDA VECTORIAL (vector_store.py):

  # Para millones de vectores, cambiar a IndexIVFFlat:
  quantizer = faiss.IndexFlatL2(dimension)
  self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
  self.index.train(training_vectors)

===========================================
MEJORAS FUTURAS
===========================================

☐ Procesamiento asíncrono con Celery
☐ Soporte para DOCX, TXT, MD
☐ Re-ranking con cross-encoders
☐ Interfaz web interactiva
☐ Chunking inteligente por secciones
☐ Caché de embeddings frecuentes
☐ Soporte multimodal (imágenes en PDFs)
☐ Fine-tuning del modelo de embeddings

===========================================
TROUBLESHOOTING
===========================================

Error: "sentence-transformers no instalado"
→ pip install sentence-transformers

Error: "FAISS no instalado"
→ pip install faiss-cpu (o faiss-gpu si tienes CUDA)

Documento queda en "processing"
→ Revisar logs para ver el error específico
→ Verificar que el PDF no esté corrupto

Respuestas irrelevantes
→ Aumentar top_k a 5-7
→ Cambiar a modelo de embeddings 'large'
→ Ajustar chunk_size y overlap

OCR muy lento
→ Desactivar OCR si no es necesario
→ O usar GPU con easyocr en vez de pytesseract

===========================================
ESTADO ACTUAL DEL PROYECTO
===========================================

✅ CÓDIGO CREADO:
- Modelos de BD (DocumentCollection, DocumentChunk, RAGQuery)
- Módulos Python (document_loader, embeddings, vector_store)
- Views con endpoints RESTful
- URLs configuradas
- Admin de Django
- App registrada en INSTALLED_APPS

❌ FALTA HACER (TÚ):
- Instalar dependencias (pip install...)
- Crear tablas (makemigrations, migrate)
- Probar con un PDF real
- Ajustar parámetros si es necesario

📁 ARCHIVOS CREADOS:
bar_galileo/rag_chat/
├── __init__.py
├── apps.py
├── models.py              ← Tablas de BD
├── admin.py               ← Django admin
├── views.py               ← 5 endpoints (upload, query, etc)
├── urls.py                ← Rutas
├── document_loader.py     ← Lee PDFs y crea chunks
├── embeddings.py          ← Genera vectores con sentence-transformers
├── vector_store.py        ← Búsqueda FAISS
└── README.txt             ← Este archivo

===========================================
DIAGRAMA DE FLUJO COMPLETO
===========================================

1. INDEXACIÓN (una vez por documento)
--------------------------------------

   [PDF]
     ↓
   document_loader.py
     → Lee páginas
     → Divide en chunks de 500 palabras
     ↓
   embeddings.py
     → Genera vector por cada chunk
     ↓
   [Base de Datos]
     → Guarda chunks + vectores

2. CONSULTA (cada vez que preguntas)
-------------------------------------

   [Pregunta del usuario]
     ↓
   embeddings.py
     → Genera vector de la pregunta
     ↓
   vector_store.py (FAISS)
     → Busca chunks similares en BD
     → Retorna los 3 más parecidos
     ↓
   views.py
     → Construye prompt con contexto
     → Llama a Google Gemini API
     ↓
   [Respuesta fundamentada]
     + Fuentes (páginas)

===========================================
RESUMEN PARA NO PROGRAMADORES
===========================================

¿Qué problema resuelve esto?

ANTES:
- Usuario: "¿Cómo hacer X?"
- Tú: "Busca en el manual en la página... no sé cuál"
- Usuario pierde tiempo buscando

DESPUÉS:
- Usuario: "¿Cómo hacer X?"
- Sistema: "Según el manual (pág 5): Para hacer X..."
- Usuario tiene respuesta instantánea con fuente

¿Cómo lo hace?

1. Subes el PDF del manual (1 vez)
2. Sistema lo "lee" y lo convierte en números
3. Usuario pregunta
4. Sistema busca qué parte del manual responde
5. Le pasa esa parte a la IA (Google Gemini)
6. IA responde basándose en tu manual, no inventando

===========================================
NOTAS IMPORTANTES
===========================================

✓ Archivos subidos se guardan en media/rag_documents/
✓ Embeddings se guardan en BD (JSON) para persistencia
✓ FAISS se reconstruye en memoria al iniciar
✓ Google API tiene límite de tokens (~30K para Gemini)
✓ Para producción, considera usar Celery para procesamiento
✓ El modelo multilingual funciona bien en español
