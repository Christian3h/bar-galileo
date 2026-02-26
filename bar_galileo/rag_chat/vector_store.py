"""
Vector Store - Búsqueda vectorial con FAISS
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Intentar importar FAISS o alternativa liviana
try:
    import faiss

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning(
        "FAISS no instalado. Se usará NearestNeighbors de scikit-learn como alternativa liviana."
    )
    from sklearn.neighbors import NearestNeighbors


from .embeddings import EmbeddingGenerator, get_embedding_generator


class VectorStore:
    """
    Almacén de vectores con búsqueda eficiente usando FAISS o NearestNeighbors (scikit-learn).
    Usa un EmbeddingGenerator para generar los embeddings de los documentos y queries.
    """

    def __init__(self, dimension: int, embedding_generator: EmbeddingGenerator = None):
        """
        Inicializa el vector store.

        Args:
            dimension: Dimensionalidad de los vectores
            embedding_generator: instancia de EmbeddingGenerator (opcional)
        """
        self.dimension = dimension
        self.index = None
        self.metadata = []  # Lista de metadata por cada vector
        self.vectors = None  # Solo para alternativa liviana
        self.use_faiss = HAS_FAISS
        self.embedding_generator = embedding_generator or get_embedding_generator()
        self._initialize_index()

    def _initialize_index(self):
        """Inicializa el índice FAISS o NearestNeighbors"""
        if self.use_faiss:
            # Usar índice Flat (exacto) para datasets pequeños/medianos
            # Para millones de vectores, cambiar a IndexIVFFlat
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"Índice FAISS inicializado (dim={self.dimension})")
        else:
            self.index = NearestNeighbors(metric="euclidean")
            logger.info(
                f"Índice NearestNeighbors (scikit-learn) inicializado (dim={self.dimension})"
            )

    def add(self, vectors: np.ndarray, metadata: List[Dict]):
        """
        Añade vectores al índice.

        Args:
            vectors: Array numpy (shape: [n, dimension])
            metadata: Lista de dicts con metadata de cada vector
        """
        if len(vectors) != len(metadata):
            raise ValueError("Número de vectores y metadata debe coincidir")
        if self.use_faiss:
            # Asegurar tipo float32 (requerido por FAISS)
            vectors = vectors.astype("float32")
            # Normalizar vectores para búsqueda por similitud coseno (opcional)
            # faiss.normalize_L2(vectors)
            self.index.add(vectors)
            logger.info(f"Añadidos {len(vectors)} vectores. Total: {self.index.ntotal}")
        else:
            # Concatenar los nuevos vectores a los existentes
            if self.vectors is None:
                self.vectors = vectors
            else:
                self.vectors = np.vstack([self.vectors, vectors])
            # Ajustar el índice con todos los vectores actuales
            self.index.fit(self.vectors)
            logger.info(f"Añadidos {len(vectors)} vectores. Total: {len(self.vectors)}")
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Busca los k vectores más similares.

        Args:
            query_vector: Vector de consulta (shape: [dimension])
            k: Número de resultados a retornar

        Returns:
            Lista de dicts con 'metadata' y 'score' (distancia)
        """
        if self.use_faiss:
            if self.index.ntotal == 0:
                logger.warning("Índice vacío, no hay resultados")
                return []
            # Preparar query
            query_vector = query_vector.astype("float32").reshape(1, -1)
            # faiss.normalize_L2(query_vector)
            k = min(k, self.index.ntotal)  # No buscar más de lo disponible
            distances, indices = self.index.search(query_vector, k)
            indices = indices[0]
            distances = distances[0]
        else:
            if self.vectors is None or len(self.vectors) == 0:
                logger.warning("Índice vacío, no hay resultados")
                return []
            k = min(k, len(self.vectors))
            distances, indices = self.index.kneighbors(
                query_vector.reshape(1, -1), n_neighbors=k
            )
            indices = indices[0]
            distances = distances[0]

        # Preparar resultados
        results = []
        for idx, dist in zip(indices, distances):
            if idx < len(self.metadata):  # Verificar índice válido
                results.append(
                    {
                        "metadata": self.metadata[idx],
                        "score": float(dist),
                        "similarity": 1
                        / (1 + float(dist)),  # Convertir distancia a similitud
                    }
                )

        return results

    def save(self, path: str):
        """
        Guarda el índice en disco.

        Args:
            path: Ruta donde guardar (sin extensión)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Guardar índice FAISS
        index_path = str(path.with_suffix(".index"))
        faiss.write_index(self.index, index_path)

        # Guardar metadata (como numpy comprimido)
        metadata_path = str(path.with_suffix(".meta.npz"))
        np.savez_compressed(metadata_path, metadata=self.metadata)

        logger.info(f"Vector store guardado en {path}")

    def load(self, path: str):
        """
        Carga el índice desde disco.

        Args:
            path: Ruta del índice (sin extensión)
        """
        path = Path(path)

        # Cargar índice FAISS
        index_path = str(path.with_suffix(".index"))
        self.index = faiss.read_index(index_path)

        # Cargar metadata
        metadata_path = str(path.with_suffix(".meta.npz"))
        data = np.load(metadata_path, allow_pickle=True)
        self.metadata = data["metadata"].tolist()

        logger.info(f"Vector store cargado desde {path}. {self.index.ntotal} vectores")

    def clear(self):
        """Limpia el índice"""
        self._initialize_index()
        self.metadata = []
        logger.info("Vector store limpiado")

    def size(self) -> int:
        """Retorna el número de vectores en el índice"""
        return self.index.ntotal if self.index else 0


class DatabaseVectorStore:
    """
    Vector store híbrido: FAISS/NearestNeighbors para búsqueda rápida + Django ORM para persistencia.
    Sincroniza automáticamente con DocumentChunk.
    """

    def __init__(
        self,
        collection_id: int,
        dimension: int,
        embedding_generator: EmbeddingGenerator = None,
    ):
        """
        Args:
            collection_id: ID de la colección de documentos
            dimension: Dimensionalidad de embeddings
            embedding_generator: instancia de EmbeddingGenerator (opcional)
        """
        self.collection_id = collection_id
        self.dimension = dimension
        self.embedding_generator = embedding_generator or get_embedding_generator()
        self.vector_store = VectorStore(
            dimension, embedding_generator=self.embedding_generator
        )
        self._load_from_database()

    def _load_from_database(self):
        """Carga textos y metadatos desde la base de datos, ajusta el vectorizador y genera embeddings"""
        from .models import DocumentChunk

        chunks = DocumentChunk.objects.filter(
            collection_id=self.collection_id
        ).order_by("chunk_index")

        if not chunks.exists():
            logger.info(f"No hay chunks para colección {self.collection_id}")
            self.texts = []
            self.metadata = []
            self.vectors_array = None
            return

        texts = []
        metadata = []

        for chunk in chunks:
            texts.append(chunk.content)
            metadata.append(
                {
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    **chunk.metadata,
                }
            )

        # FORZAR: Siempre recalcular embeddings desde textos originales y ajustar vectorizador
        if texts:
            # Ajustar el vectorizador SIEMPRE antes de calcular embeddings
            if hasattr(self.embedding_generator, "fit_on_documents"):
                self.embedding_generator.fit_on_documents(texts)
            vectors_array = self.embedding_generator.encode_documents(texts)
            self.vector_store.add(vectors_array, metadata)
            logger.info(
                f"Cargados {len(vectors_array)} chunks de BD (embeddings recalculados desde textos originales)"
            )
            self.texts = texts
            self.metadata = metadata
            self.vectors_array = vectors_array
        else:
            logger.info(
                "No hay textos para ajustar el vectorizador ni generar embeddings."
            )
            self.texts = []
            self.metadata = []
            self.vectors_array = None

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Busca chunks similares a una query de texto"""
        # Si no hay embeddings cargados o vectorizador no ajustado, retorna vacío
        if (
            not hasattr(self, "vectors_array")
            or self.vectors_array is None
            or len(self.vectors_array) == 0
        ):
            logger.warning("No hay embeddings cargados. Retornando resultados vacíos.")
            return []
        if (
            hasattr(self.embedding_generator, "_is_fitted")
            and not self.embedding_generator._is_fitted
        ):
            logger.warning(
                "El vectorizador TF-IDF no ha sido ajustado. Retornando resultados vacíos."
            )
            return []
        query_vector = self.embedding_generator.encode_query(query)
        return self.vector_store.search(query_vector, k)
