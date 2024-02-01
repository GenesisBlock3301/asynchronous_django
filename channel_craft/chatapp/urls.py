from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='chat-index'),
    path('<str:room_name>/', views.RoomView.as_view(), name='chat-room')
]
