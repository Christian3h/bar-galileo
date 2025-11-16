"""
Embeddings Generator - Genera vectores con sentence-transformers
"""
import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

# Intentar importar sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning(
        "sentence-transformers no instalado. "
        "Instala con: pip install sentence-transformers"
    )


class EmbeddingGenerator:
    """Generador de embeddings usando sentence-transformers"""

    # Modelos recomendados (ordenados por calidad/tamaño)
    MODELS = {
        'mini': 'sentence-transformers/all-MiniLM-L6-v2',  # Rápido, 384 dims
        'multilingual': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Español, 384 dims
        'large': 'intfloat/multilingual-e5-base',  # Mejor calidad, 768 dims
    }

    def __init__(self, model_name: str = 'multilingual'):
        """
        Inicializa el generador de embeddings.

        Args:
            model_name: 'mini', 'multilingual', o 'large'
                       También acepta nombre completo del modelo
        """
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError(
                "sentence-transformers requerido. "
                "Instala con: pip install sentence-transformers"
            )

        # Resolver nombre del modelo
        if model_name in self.MODELS:
            model_path = self.MODELS[model_name]
        else:
            model_path = model_name

        logger.info(f"Cargando modelo de embeddings: {model_path}")
        self.model = SentenceTransformer(model_path)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Modelo cargado. Dimensión: {self.dimension}")

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Genera embeddings para uno o varios textos.

        Args:
            texts: Texto o lista de textos
            batch_size: Tamaño del lote para procesar
            show_progress: Mostrar barra de progreso

        Returns:
            Array numpy con los embeddings (shape: [n_texts, dimension])
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """
        Genera embedding para una consulta (query).
        Wrapper de encode() para claridad semántica.

        Args:
            query: Texto de la consulta

        Returns:
            Array numpy con el embedding
        """
        return self.encode(query)[0]

    def encode_documents(
        self,
        documents: List[str],
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings para múltiples documentos.

        Args:
            documents: Lista de textos a embedizar
            show_progress: Mostrar barra de progreso

        Returns:
            Array numpy con los embeddings
        """
        return self.encode(documents, show_progress=show_progress)

    def get_dimension(self) -> int:
        """Retorna la dimensionalidad de los embeddings"""
        return self.dimension


# Instancia global lazy-loaded
_global_generator = None


def get_embedding_generator(model_name: str = 'multilingual') -> EmbeddingGenerator:
    """
    Obtiene una instancia global del generador (singleton).
    Útil para evitar cargar el modelo múltiples veces.

    Args:
        model_name: Nombre del modelo a usar

    Returns:
        Instancia de EmbeddingGenerator
    """
    global _global_generator

    if _global_generator is None:
        _global_generator = EmbeddingGenerator(model_name)

    return _global_generator
