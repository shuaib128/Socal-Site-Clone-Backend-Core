import os
from rest_framework import serializers
from .models import Post, MediaFile, Comment, Reply
from Users.models import Profile
from django.conf import settings
from urllib.parse import urljoin
from pathlib import Path


#Image serilizer
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

#Image serilizer
class MediaSerializer(serializers.ModelSerializer):
    hls_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = ['id', 'filename', 'file', 'hls_url']

    def get_hls_url(self, obj):
        if obj.hls_directory:
            # Remove MEDIA_ROOT from the start of the hls_directory
            hls_path = Path(obj.hls_directory[len(settings.MEDIA_ROOT):])
            # Normalize the path to remove any leading or trailing slashes
            hls_path = hls_path.as_posix().strip('/')
            # Append the master playlist file name
            hls_path = f"{hls_path}/master.m3u8"
            # Join MEDIA_URL and the remaining hls_path
            return urljoin(settings.MEDIA_URL, hls_path)
        return None

#Reply serilizer
class ReplySerializer(serializers.ModelSerializer):
    likes = AuthorSerializer(many=True)
    author = AuthorSerializer()
    class Meta:
        model = Reply
        fields = '__all__' 

#Comment serilizer
class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    likes = AuthorSerializer(many=True)
    replyes = ReplySerializer(many=True)
    class Meta:
        model = Comment
        fields = '__all__'        

#Post serilizer
class PostSerializer(serializers.ModelSerializer):
    auhtor = AuthorSerializer()
    media_files = MediaSerializer(many=True)
    likes = AuthorSerializer(many=True)
    comments = CommentSerializer(many=True)
    class Meta:
        model = Post
        fields = '__all__'