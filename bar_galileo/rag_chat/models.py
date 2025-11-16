from django.db import models
from django.contrib.auth.models import User
import json


class DocumentCollection(models.Model):
    """Colección de documentos para RAG (ej. Manual de Usuario)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_collections', null=True, blank=True)
    title = models.CharField(max_length=300, help_text='Nombre del documento')
    file = models.FileField(upload_to='rag_documents/', help_text='Archivo PDF o documento')
    file_type = models.CharField(max_length=50, default='pdf')
    page_count = models.IntegerField(default=0, help_text='Número de páginas')
    chunk_count = models.IntegerField(default=0, help_text='Número de fragmentos indexados')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'Procesando'),
            ('indexed', 'Indexado'),
            ('error', 'Error'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Colección de Documentos'
        verbose_name_plural = 'Colecciones de Documentos'

    def __str__(self):
        return f"{self.title} ({self.status})"


class DocumentChunk(models.Model):
    """Fragmento de documento con embedding para búsqueda vectorial"""
    collection = models.ForeignKey(
        DocumentCollection,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.IntegerField(help_text='Índice del fragmento')
    content = models.TextField(help_text='Texto del fragmento')
    embedding = models.JSONField(
        help_text='Vector embedding (lista de floats)',
        default=list
    )
    metadata = models.JSONField(
        default=dict,
        help_text='Metadatos: página, sección, enlace, etc.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['collection', 'chunk_index']
        verbose_name = 'Fragmento de Documento'
        verbose_name_plural = 'Fragmentos de Documentos'
        indexes = [
            models.Index(fields=['collection', 'chunk_index']),
        ]

    def __str__(self):
        return f"{self.collection.title} - Chunk {self.chunk_index}"

    def get_embedding_vector(self):
        """Retorna el embedding como lista de floats"""
        if isinstance(self.embedding, str):
            return json.loads(self.embedding)
        return self.embedding


class RAGQuery(models.Model):
    """Historial de consultas RAG para análisis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rag_queries')
    collection = models.ForeignKey(
        DocumentCollection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    query = models.TextField(help_text='Pregunta del usuario')
    response = models.TextField(help_text='Respuesta generada')
    chunks_used = models.JSONField(
        default=list,
        help_text='IDs de chunks usados para la respuesta'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consulta RAG'
        verbose_name_plural = 'Consultas RAG'

    def __str__(self):
        return f"{self.user.username}: {self.query[:50]}..."
