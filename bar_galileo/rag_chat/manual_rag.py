import os
import numpy as np
from .document_loader import DocumentLoader
from .embeddings import get_embedding_generator
from .vector_store import VectorStore

# Ruta fija del manual PDF
MANUAL_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media", "user_manuals", "manual.pdf")
)

def load_manual_chunks(chunk_size=500, overlap=50):
    """
    Carga y divide el manual fijo en chunks.
    """
    loader = DocumentLoader(use_ocr=False)
    pages_data, _ = loader.load_pdf(MANUAL_PATH)
    # El chunker espera 'content', pero pages_data tiene 'text'
    # Adaptamos cada página para que tenga 'content'
    for page in pages_data:
        page["content"] = page.get("text", "")
    chunks = loader.chunk_text(pages_data, chunk_size=chunk_size, overlap=overlap)
    return chunks

def get_embeddings_and_store(chunks):
    """
    Genera embeddings para los chunks y los almacena en un VectorStore.
    """
    generator = get_embedding_generator()
    texts = [chunk["content"] for chunk in chunks]
    # Ajustar el generador si es necesario (TF-IDF)
    if hasattr(generator, "_is_fitted") and not generator._is_fitted:
        generator.fit_on_documents(texts)
    embeddings = generator.encode_documents(texts)
    embeddings_array = np.vstack([np.array(e, dtype=np.float32) for e in embeddings])
    vector_store = VectorStore(generator.get_dimension())
    vector_store.add(embeddings_array, chunks)
    return vector_store

def search_manual(query, top_k=3):
    """
    Busca los chunks más relevantes del manual para una consulta.
    Devuelve los chunks y el vector de consulta.
    """
    chunks = load_manual_chunks()
    generator = get_embedding_generator()
    texts = [chunk["content"] for chunk in chunks]
    if hasattr(generator, "_is_fitted") and not generator._is_fitted:
        generator.fit_on_documents(texts)
    query_vector = generator.encode_query(query)
    vector_store = get_embeddings_and_store(chunks)
    results = vector_store.search(query_vector, k=top_k)
    return results, query_vector
