from django.urls import path
from .api import (FriendListView, PendingFriendRequestsView, UserRegistrationView,UserLoginView,UserSearchView, SendFriendRequestView, AcceptRejectFriendRequestView)



urlpatterns = [
    path('signup/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-requests/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-requests/update/', AcceptRejectFriendRequestView.as_view(), name='accept-reject-friend-request'),
    path('friends-list/', FriendListView.as_view(), name='friend-request-accpted-list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
]
