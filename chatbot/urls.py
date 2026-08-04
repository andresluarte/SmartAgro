# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('mensaje/', views.chat_endpoint, name='chat_mensaje'),
    path('confirmar-accion/', views.confirmar_accion, name='chat_confirmar_accion'),
]