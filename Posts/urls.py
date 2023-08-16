from django.urls import path
from .views import (
    PostsAPIView, PostCreateAPIView, PostImageCreateAPIView,
    PostVideoCreateAPIView, FinalizeUploadView, PostLikeView,
    PostCommentView, PostCommentLikeView, PostReplyView,
    PostReplyLikeView, PostDetailView, PostDetailEditView,
    PostSearchAPIView, PostDeleteView
)

urlpatterns = [
    path('', PostsAPIView.as_view(), name='Posts'),
    path('post/search', PostSearchAPIView.as_view(), name='PostSearchAPIView'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='PostDetailView'),
    path('post/create/', PostCreateAPIView.as_view(), name='PostCreate'),
    path('post/edit/<int:pk>/', PostDetailEditView.as_view(), name='PostDetailEditView'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='PostDeleteView'),
    path('post/add/media/image/', PostImageCreateAPIView.as_view(), name='AddImage'),
    path('post/add/media/video/', PostVideoCreateAPIView.as_view(), name='AddVideo'),
    path('post/add/media/video/finalize/', FinalizeUploadView.as_view(), name='FinalizeVideo'),
    path('post/add/like/', PostLikeView.as_view(), name='PostLikeView'),
    path('post/add/comment/', PostCommentView.as_view(), name='PostCommentView'),
    path('post/add/comment/like/', PostCommentLikeView.as_view(), name='PostCommentLikeView'),
    path('post/add/reply/', PostReplyView.as_view(), name='PostReplyView'),
    path('post/add/reply/like/', PostReplyLikeView.as_view(), name='PostReplyLikeView'),
]