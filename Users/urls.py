from django.urls import path
from .views import (
    UserCreateAPIView, UserView, LogoutView, UserPostsView, UserByIdView,
    UserFollowerAddView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('author/', UserView.as_view(), name='UserView'),
    path('user/<int:pk>/', UserByIdView.as_view(), name='UserByIdView'),
    path('user/follower/add/<int:pk>/', UserFollowerAddView.as_view(), name='UserFollowerAddView'),
    path('user/posts/<int:pk>/', UserPostsView.as_view(), name='UserPostsView'),
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', UserCreateAPIView.as_view(), name='register'),
    path('user/logout/', LogoutView.as_view(), name='LogoutView'),
]