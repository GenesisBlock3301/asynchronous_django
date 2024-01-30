# chat/views.py
from django.shortcuts import render

from chatapp.models import Room


def index(request):
    return render(request, "chat/index.html",{
        'rooms': Room.objects.all()
    })


def room(request, room_name):
    _room, created = Room.objects.get_or_create(name=room_name)
    return render(request, "chat/room.html", {"room_name": _room.name})
