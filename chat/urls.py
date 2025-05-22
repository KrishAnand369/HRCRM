from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView


from django.urls import path
from . import views

urlpatterns = [
    path('chat/<str:room_name>/', views.chat_room, name='chat-room'),
    path('private/<str:username>/', views.private_chat, name='private-chat'),
    path('private/chats', views.private_chat, name='private-chat'),
]
