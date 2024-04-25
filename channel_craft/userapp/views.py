from django.utils import timezone

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, F, Value, IntegerField, BooleanField, Q, OuterRef, Subquery
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

        subquery = Friend.objects.annotate(
            is_friend=Q(from_user=request.user, to_user=OuterRef('pk'), is_accepted=True) |
                      Q(from_user=OuterRef('pk'), to_user=request.user, is_accepted=True)
        ).values('id')[:1]
        users = User.objects.annotate(
            is_friend=Subquery(subquery)
        ).filter(is_friend=True).exclude(username=request.user.username).order_by('username')
        get_friend_request_users = Friend.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            is_accepted=False
        ).select_related('from_user', 'to_user').exclude(from_user=request.user)
        test_dict = dict()
        test_dict[1] = "one"
        test_dict[2] = "two"
        test_dict[3] = "three"
        context = {
            'users': users,
            "get_friend_request_users": get_friend_request_users,
            "test_dict": test_dict,
            "vals": [1,2,3,4,5]
        }
        return render(request, template_name, context)


@login_required
def friends_list(request):
    friend_list = Friend.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        is_accepted=True
    )
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
def friend_request_action(request, friend_request_id, action_type):
    if action_type == 'accept':
        try:
            friend_request = get_object_or_404(Friend, from_user__id=friend_request_id, to_user=request.user,
                                               is_accepted=False)
            friend_request.is_accepted = True
            friend_request.created_at = timezone.now()
            friend_request.save()
            return redirect('friend-list')
        except Exception as e:
            print(str(e))
            return redirect('user-list')
    else:
        try:
            friend_request = get_object_or_404(Friend, from_user__id=friend_request_id, to_user=request.user,
                                               is_accepted=False)
            friend_request.delete()
            return redirect('user-list')
        except Exception as e:
            print(str(e))
            return redirect('user-list')
