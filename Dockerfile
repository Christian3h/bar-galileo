# Python slim image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps: build tools, MySQL client libs, flite for audio captcha
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    curl \
    flite \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt && pip install pip-licenses

# Copy project
COPY bar_galileo /app/bar_galileo
COPY run_server.sh /app/run_server.sh

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Environment
ENV DJANGO_SETTINGS_MODULE=bar_galileo.settings \
    PYTHONPATH=/app

# Entrypoint will run migrations and collectstatic before starting
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/run_server.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "bar_galileo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
