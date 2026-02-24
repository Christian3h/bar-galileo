from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/query/', views.QueryRAGView.as_view(), name='query_rag'),
]