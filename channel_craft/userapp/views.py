from datetime import timezone

from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from userapp.models import Friend


class LoginView(View):
    def get(self, request):
        return render(request, 'userapp/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('user-list'))
        return redirect('user-login')


@login_required
def logout_view(request):
    logout(request)
    return redirect('user-login')


class UserListView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('user-login')
        template_name = 'userapp/user_list.html'
        context = {
            'users': User.objects.all().exclude(username=request.user.username).order_by('username')
        }
        return render(request, template_name, context)


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
            return render(request, 'userapp/friend_request.html', {"friend_request": 'friend_request'})


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
