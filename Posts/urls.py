from django.urls import path
from .views import (
    PostsAPIView, PostCreateAPIView, PostImageCreateAPIView,
    PostVideoCreateAPIView, FinalizeUploadView
)

urlpatterns = [
    path('', PostsAPIView.as_view(), name='Posts'),
    path('post/create/', PostCreateAPIView.as_view(), name='PostCreate'),
    path('post/add/media/image/', PostImageCreateAPIView.as_view(), name='AddImage'),
    path('post/add/media/video/', PostVideoCreateAPIView.as_view(), name='AddVideo'),
    path('post/add/media/video/finalize/', FinalizeUploadView.as_view(), name='FinalizeVideo'),
]