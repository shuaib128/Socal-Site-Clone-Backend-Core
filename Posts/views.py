import base64
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, MediaFile
from Users.models import Profile
from .serializers import PostSerializer, MediaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

# Create your views here.
class PostsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
        
#Create post
class PostCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, format=None):
        try:
            #Posted data
            author_name = request.data['authorName']
            description = request.data['description']
            author = get_object_or_404(Profile, username=author_name)

            # # Create a post object
            post = Post.objects.create(
                auhtor=author,
                description=description
            )

            return Response(
                {
                    'message': 'Post created successfully',
                    'post_id' : post.id
                }, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

#Add Image to a post
class PostImageCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, format=None):
        try:
            #Posted data
            post_id = request.data['postID']
            post = get_object_or_404(Post, id=post_id)

            format, imgstr = request.data['imageBase64'].split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(base64.b64decode(imgstr), name=f"image.{ext}")

            media_file = MediaFile()
            media_file.file.save("image.jpg", file_content)
            post.media_files.add(media_file)

            return Response(
                {
                    'message': 'Image Added suffcefull',
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

#Add video to a post
class PostVideoCreateAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            filename = request.data.get('filename')
            chunk = request.data.get('chunk')

            if not filename or not chunk:
                return Response(
                    {'status': 'Bad request'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            media_files = MediaFile.objects.filter(filename=filename)
            if media_files.exists():
                # If a matching MediaFile exists, choose the first one
                media_file = media_files.first()
            else:
                # If no matching MediaFile exists, create a new one
                media_file = MediaFile.objects.create(filename=filename)

            if chunk:
                media_file.append_chunk(chunk.read())

            serializer = MediaSerializer(media_file)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Add Video file to the Post
class FinalizeUploadView(APIView):
    parser_classes = [JSONParser]
    def post(self, request, *args, **kwargs):
        try:
            post_id = request.data.get('postID')
            video_id = request.data.get('videoID')

            post = get_object_or_404(Post, id=post_id)
            video_file = get_object_or_404(MediaFile, id=video_id)

            post.media_files.add(video_file)
            post.save()

            # Start encoding the video to HLS
            video_file.start_encoding()
            
            return Response(
                {"Video Added Successfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )