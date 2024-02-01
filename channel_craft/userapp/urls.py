from django.urls import path
from .views import UserListView, friends_list

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('friends/', friends_list, name='friend-list')
]
