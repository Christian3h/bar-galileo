from django.urls import path
from . import views

app_name = 'google_chat'

urlpatterns = [
    path('', views.chat_view, name='index'),
    path('api/send/', views.send_message, name='send_message'),
]
