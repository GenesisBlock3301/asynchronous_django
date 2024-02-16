from django.urls import path
from .views import UserListView, friends_list, LoginView, logout_view, make_friend_request, friend_request_action

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('friends/', friends_list, name='friend-list'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('send-request/<int:friend_id>/', make_friend_request, name='make-friends-list'),
    path('request-action/<int:friend_request_id>/<str:action_type>/', friend_request_action,
         name='friend-request-action'),
]
