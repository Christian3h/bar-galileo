# Dockerfile para Bar Galileo
# Python 3.11 + dependencias nativas + OCR + NLP

FROM python:3.11-slim-bullseye

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para mysqlclient, pymupdf, pytesseract, cryptography, etc.
RUN apt-get update && apt-get install -y --fix-missing \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    tesseract-ocr \
    tesseract-ocr-spa \
    libmupdf-dev \
    libgl1 \
    libglib2.0-0 \
    netcat-openbsd \
    flite \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias Python
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelos de spaCy y NLTK necesarios en runtime
#RUN python -m spacy download es_core_news_sm
RUN pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0-py3-none-any.whl
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copiar el resto del código fuente
COPY bar_galileo/ .

# Copiar y configurar entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer el puerto de la aplicación
EXPOSE 8000

# Entrypoint: ejecuta migraciones y collectstatic antes de levantar el servidor
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "bar_galileo.asgi:application"]
