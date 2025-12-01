"""
Vector Store - Búsqueda vectorial con FAISS
"""
import logging
from typing import List, Dict, Tuple
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Intentar importar FAISS
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning(
        "FAISS no instalado. Instala con: pip install faiss-cpu "
        "(o faiss-gpu si tienes CUDA)"
    )


class VectorStore:
    """Almacén de vectores con búsqueda eficiente usando FAISS"""

    def __init__(self, dimension: int):
        """
        Inicializa el vector store.

        Args:
            dimension: Dimensionalidad de los vectores
        """
        if not HAS_FAISS:
            raise ImportError(
                "FAISS requerido. Instala con: pip install faiss-cpu"
            )

        self.dimension = dimension
        self.index = None
        self.metadata = []  # Lista de metadata por cada vector
        self._initialize_index()

    def _initialize_index(self):
        """Inicializa el índice FAISS"""
        # Usar índice Flat (exacto) para datasets pequeños/medianos
        # Para millones de vectores, cambiar a IndexIVFFlat
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Índice FAISS inicializado (dim={self.dimension})")

    def add(
        self,
        vectors: np.ndarray,
        metadata: List[Dict]
    ):
        """
        Añade vectores al índice.

        Args:
            vectors: Array numpy (shape: [n, dimension])
            metadata: Lista de dicts con metadata de cada vector
        """
        if len(vectors) != len(metadata):
            raise ValueError("Número de vectores y metadata debe coincidir")

        # Asegurar tipo float32 (requerido por FAISS)
        vectors = vectors.astype('float32')

        # Normalizar vectores para búsqueda por similitud coseno
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.metadata.extend(metadata)

        logger.info(f"Añadidos {len(vectors)} vectores. Total: {self.index.ntotal}")

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5
    ) -> List[Dict]:
        """
        Busca los k vectores más similares.

        Args:
            query_vector: Vector de consulta (shape: [dimension])
            k: Número de resultados a retornar

        Returns:
            Lista de dicts con 'metadata' y 'score' (distancia)
        """
        if self.index.ntotal == 0:
            logger.warning("Índice vacío, no hay resultados")
            return []

        # Preparar query
        query_vector = query_vector.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_vector)

        # Buscar
        k = min(k, self.index.ntotal)  # No buscar más de lo disponible
        distances, indices = self.index.search(query_vector, k)

        # Preparar resultados
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):  # Verificar índice válido
                results.append({
                    'metadata': self.metadata[idx],
                    'score': float(dist),
                    'similarity': 1 / (1 + float(dist))  # Convertir distancia a similitud
                })

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
        index_path = str(path.with_suffix('.index'))
        faiss.write_index(self.index, index_path)

        # Guardar metadata (como numpy comprimido)
        metadata_path = str(path.with_suffix('.meta.npz'))
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
        index_path = str(path.with_suffix('.index'))
        self.index = faiss.read_index(index_path)

        # Cargar metadata
        metadata_path = str(path.with_suffix('.meta.npz'))
        data = np.load(metadata_path, allow_pickle=True)
        self.metadata = data['metadata'].tolist()

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
    Vector store híbrido: FAISS para búsqueda rápida + Django ORM para persistencia.
    Sincroniza automáticamente con DocumentChunk.
    """

    def __init__(self, collection_id: int, dimension: int):
        """
        Args:
            collection_id: ID de la colección de documentos
            dimension: Dimensionalidad de embeddings
        """
        self.collection_id = collection_id
        self.dimension = dimension
        self.vector_store = VectorStore(dimension)
        self._load_from_database()

    def _load_from_database(self):
        """Carga vectores desde la base de datos"""
        from .models import DocumentChunk

        chunks = DocumentChunk.objects.filter(
            collection_id=self.collection_id
        ).order_by('chunk_index')

        if not chunks.exists():
            logger.info(f"No hay chunks para colección {self.collection_id}")
            return

        vectors = []
        metadata = []

        for chunk in chunks:
            embedding = chunk.get_embedding_vector()
            if embedding:
                vectors.append(embedding)
                metadata.append({
                    'chunk_id': chunk.id,
                    'chunk_index': chunk.chunk_index,
                    'content': chunk.content,
                    **chunk.metadata
                })

        if vectors:
            vectors_array = np.array(vectors)
            self.vector_store.add(vectors_array, metadata)
            logger.info(f"Cargados {len(vectors)} chunks de BD")

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """Busca chunks similares"""
        return self.vector_store.search(query_vector, k)
