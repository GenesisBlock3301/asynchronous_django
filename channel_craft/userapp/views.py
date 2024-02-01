from datetime import timezone

from django.contrib.auth.models import User
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from userapp.models import Friend


class UserListView(ListView):
    model = User
    paginate_by = 10
    template_name = 'userapp/user_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        return context


@login_required
def friends_list(request):
    friend_list = request.user.friends.all()
    return render(request, 'userapp/friend_list.html', {'friend_list': friend_list})


@login_required
def make_friend_request(request, friend_id):
    if request.method == 'POST':
        target_user = User.objects.filter(id=friend_id).first()
        # request already exist or not
        existing_user = User.objects.filter(
            users=request.user, friends=target_user
        ).first()
        if not existing_user and target_user != request.user:
            Friend.objects.create(users=request.user, friends=target_user)
            return render(request, 'userapp/friend_request.html', {"friend_request": friend_request})


@login_required
def accept_friend_request(request, friend_request_id):
    friend_request = Friend.objects.get(
        id=friend_request_id,
        friends=request.user,
        accepted=False
    )
    friend_request.accepted = True
    friend_request.created_at = timezone.now()
    friend_request.save()
    return


@login_required
def decline_friend_request(request, friend_request_id):
    friend_request = Friend.objects.get(
        id=friend_request_id,
        friends=request.user,
        accepted=False
    )
    friend_request.delete()
    return
