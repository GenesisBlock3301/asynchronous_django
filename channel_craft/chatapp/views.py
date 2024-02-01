# chat/views.py
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views import View


class HomeView(View):
    def get(self, request):
        users = User.objects.all()
        return render(request, "chat/index.html", {'users': users})


class RoomView(View):
    def get(self, request, room_name):
        return render(request, "chat/room.html", {"room_name": room_name})


