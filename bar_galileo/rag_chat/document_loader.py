"""
Document Loader - Extrae texto de PDFs con soporte para OCR
"""
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Intentar importar PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF no instalado. Instala con: pip install pymupdf")

# Intentar importar pytesseract para OCR
try:
    import pytesseract
    from PIL import Image
    import io
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logger.warning("OCR no disponible. Instala con: pip install pytesseract pillow")


class DocumentLoader:
    """Extractor de texto de PDFs con soporte OCR opcional"""

    def __init__(self, use_ocr: bool = False):
        """
        Args:
            use_ocr: Si True, intenta OCR en páginas sin texto
        """
        self.use_ocr = use_ocr and HAS_OCR

        if not HAS_PYMUPDF:
            raise ImportError(
                "PyMuPDF es requerido. Instala con: pip install pymupdf"
            )

    def load_pdf(self, file_path: str) -> Tuple[List[Dict], int]:
        """
        Carga un PDF y extrae texto por página.

        Args:
            file_path: Ruta al archivo PDF

        Returns:
            Tuple de (lista de páginas con texto y metadata, número total de páginas)
            Cada página es un dict: {'page': int, 'text': str, 'metadata': dict}
        """
        pages_data = []

        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)

            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()

                # Si no hay texto y OCR está activado, intentar OCR
                if not text.strip() and self.use_ocr:
                    logger.info(f"Página {page_num + 1} sin texto, aplicando OCR...")
                    text = self._ocr_page(page)

                if text.strip():  # Solo guardar si hay texto
                    pages_data.append({
                        'page': page_num + 1,
                        'text': text,
                        'metadata': {
                            'page_number': page_num + 1,
                            'total_pages': total_pages,
                        }
                    })

            doc.close()
            logger.info(f"PDF cargado: {total_pages} páginas, {len(pages_data)} con texto")
            return pages_data, total_pages

        except Exception as e:
            logger.exception(f"Error cargando PDF: {e}")
            raise

    def _ocr_page(self, page) -> str:
        """Aplica OCR a una página de PDF"""
        if not self.use_ocr:
            return ""

        try:
            # Renderizar página como imagen
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom para mejor OCR
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Aplicar OCR con configuración para español
            text = pytesseract.image_to_string(img, lang='spa')
            return text

        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            return ""

    def chunk_text(
        self,
        pages_data: List[Dict],
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict]:
        """
        Divide el texto en chunks con solapamiento.

        Args:
            pages_data: Lista de páginas con texto
            chunk_size: Tamaño aproximado de cada chunk (en palabras)
            overlap: Palabras solapadas entre chunks

        Returns:
            Lista de chunks con formato:
            {
                'content': str,
                'metadata': {
                    'page': int,
                    'chunk_index': int,
                    'source_pages': List[int]
                }
            }
        """
        chunks = []
        chunk_index = 0

        # Concatenar todo el texto manteniendo info de páginas
        full_text = ""
        page_boundaries = [0]  # Posiciones donde comienza cada página

        for page_data in pages_data:
            full_text += page_data['text'] + "\n\n"
            page_boundaries.append(len(full_text.split()))

        # Dividir en palabras
        words = full_text.split()

        # Crear chunks con solapamiento
        i = 0
        while i < len(words):
            chunk_end = min(i + chunk_size, len(words))
            chunk_words = words[i:chunk_end]
            chunk_text = ' '.join(chunk_words)

            # Determinar páginas de origen
            word_pos = i + len(chunk_words) // 2  # Posición media del chunk
            source_pages = []
            for page_idx, boundary in enumerate(page_boundaries[:-1]):
                next_boundary = page_boundaries[page_idx + 1]
                if boundary <= word_pos < next_boundary:
                    source_pages.append(pages_data[page_idx]['page'])
                    break

            if chunk_text.strip():
                chunks.append({
                    'content': chunk_text.strip(),
                    'metadata': {
                        'chunk_index': chunk_index,
                        'source_pages': source_pages,
                        'word_count': len(chunk_words)
                    }
                })
                chunk_index += 1

            # Avanzar con solapamiento
            i += chunk_size - overlap

        logger.info(f"Texto dividido en {len(chunks)} chunks")
        return chunks
