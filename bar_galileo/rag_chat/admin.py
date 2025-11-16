from django.contrib import admin
from .models import DocumentCollection, DocumentChunk, RAGQuery


@admin.register(DocumentCollection)
class DocumentCollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'chunk_count', 'page_count', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'chunk_count', 'page_count']

    fieldsets = (
        ('Información', {
            'fields': ('user', 'title', 'file', 'file_type')
        }),
        ('Estado', {
            'fields': ('status', 'error_message', 'page_count', 'chunk_count')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'chunk_index', 'content_preview', 'created_at']
    list_filter = ['collection', 'created_at']
    search_fields = ['content', 'collection__title']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content
    content_preview.short_description = 'Contenido'


@admin.register(RAGQuery)
class RAGQueryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'query_preview', 'collection', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['query', 'response', 'user__username']
    readonly_fields = ['created_at']

    def query_preview(self, obj):
        return obj.query[:100] + '...' if len(obj.query) > 100 else obj.query
    query_preview.short_description = 'Consulta'
