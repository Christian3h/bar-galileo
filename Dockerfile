# Python slim image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps: build tools, MySQL client libs, flite for audio captcha
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    flite \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (using lightweight requirements without torch/CUDA)
COPY requirements-docker.txt /app/requirements-docker.txt
RUN pip install --upgrade pip && pip install -r /app/requirements-docker.txt

# Copy project
COPY bar_galileo /app/bar_galileo
COPY run_server.sh /app/run_server.sh
COPY docker/entrypoint.sh /app/entrypoint.sh

# Make scripts executable
RUN chmod +x /app/entrypoint.sh /app/run_server.sh

# Create a non-root user and set ownership
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment
ENV DJANGO_SETTINGS_MODULE=bar_galileo.settings \
    PYTHONPATH=/app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "bar_galileo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
