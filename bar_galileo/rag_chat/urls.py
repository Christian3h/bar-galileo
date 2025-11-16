from django.urls import path
from . import views

app_name = 'rag_chat'

urlpatterns = [
    # Vista principal del chat
    path('', views.chat_view, name='chat'),

    # Subir y procesar documento
    path('api/upload/', views.UploadDocumentView.as_view(), name='upload_document'),

    # Hacer consulta con RAG
    path('api/query/', views.QueryRAGView.as_view(), name='query_rag'),

    # Listar documentos indexados
    path('api/documents/', views.ListDocumentsView.as_view(), name='list_documents'),

    # Eliminar documento
    path('api/document/<int:collection_id>/', views.DeleteDocumentView.as_view(), name='delete_document'),

    # Historial de consultas
    path('api/history/', views.QueryHistoryView.as_view(), name='query_history'),
]
