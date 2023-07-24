import base64
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, MediaFile, Comment, Reply
from Users.models import Profile
from .serializers import PostSerializer, MediaSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.db.models import Count
from django.db.models.functions import Length


# Decode the token payload to get the user ID
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        return user
    except:
        return None
    
# Create your views here.
class PostsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        page_number = request.GET.get('page', 1)  # Get page number from URL, default is 1
        page_size = 4  # Set the number of posts per page
        start = (int(page_number) - 1) * page_size  # Calculate start index
        end = start + page_size  # Calculate end index

        posts = Post.objects.all()[start:end]  # Slice the queryset
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

# Post detail view
class PostDetailView(APIView):
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=404)
        
# Post detail view for user
class PostDetailEditView(APIView):
    def get(self, request, pk):
        try:
            # Retrieve the JWT token from the request header
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return Response({'error': 'Authorization header is missing'})

            auth_header_parts = auth_header.split(' ')
            if len(auth_header_parts) != 2 or auth_header_parts[0] != 'Bearer':
                return Response({'error': 'Authorization header is not in the correct format'})

            token = auth_header_parts[1]
            user = get_user_from_token(token)
            profile = get_object_or_404(Profile, user=str(user.id))
            print(profile.id)

            post = get_object_or_404(Post, id=pk, auhtor=profile)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=404)
        
#Create post
class PostCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, format=None):
        try:
            if request.data['existingPostId'] == "":
                #Posted data
                author_name = request.data['authorName']
                description = request.data['description']
                author = get_object_or_404(Profile, username=author_name)

                # Create a post object
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
            
            else:
                postID = request.data["existingPostId"]
                description = request.data['description']
                deletedImagesId = request.data["deleteImages"]
                print(deletedImagesId)

                post = get_object_or_404(Post, id=postID)
                post.description = description # Edit the description
                # Loop deletedImagesId and delete all the images for the post
                for id in deletedImagesId:
                    post.media_files.remove(id)
                post.save()

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
                media_file.append_chunk(chunk)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
        
# Update likes
class PostLikeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            channel_layer = get_channel_layer()
            data = request.data

            #Query Post and the Author(Profile Object)
            post = get_object_or_404(Post, id=data["postID"])
            author = get_object_or_404(Profile, id=data["author"])

            #Increase or decress the like count
            if post.likes.filter(id=author.id).exists():
                post.likes.remove(author)
            else:
                post.likes.add(author)

            async_to_sync(channel_layer.group_send)(
                # This is the group name
                "post",
                {
                    # This should match the method name in the consumer
                    "type": "like_post",
                    "post_id": data["postID"]
                },
            )

            return Response(
                {"Like was added scucessfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Update comments
class PostCommentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            channel_layer = get_channel_layer()
            data = request.data

            # Create the comment and ad it to the post
            author = get_object_or_404(Profile, id=data["authorID"])
            comment_content = data["commentContent"]
            comment = Comment.objects.create(
                author = author,
                comment = comment_content
            )

            post = get_object_or_404(Post, id=data["postID"])
            post.comments.add(comment)

            async_to_sync(channel_layer.group_send)(
                # This is the group name
                "post",
                {
                    # This should match the method name in the consumer
                    "type": "like_post",
                    "post_id": data["postID"],
                    "Post": post
                },
            )

            return Response(
                {"Comment was added scucessfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# Update comments
class PostReplyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            channel_layer = get_channel_layer()
            data = request.data

            # Create the comment and ad it to the post
            author = get_object_or_404(Profile, id=data["authorID"])
            comment_content = data["commentContent"]
            reply = Reply.objects.create(
                author = author,
                reply = comment_content
            )

            comment = get_object_or_404(Comment, id=data["commentID"])
            comment.replyes.add(reply)
            post = get_object_or_404(Post, id=data["postID"])

            async_to_sync(channel_layer.group_send)(
                # This is the group name
                "post",
                {
                    # This should match the method name in the consumer
                    "type": "like_post",
                    "post_id": data["postID"],
                    "Post": post
                },
            )

            return Response(
                {"Reply was added scucessfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# Update comment likes
class PostCommentLikeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            channel_layer = get_channel_layer()
            data = request.data

            # Create the comment and ad it to the post
            author = get_object_or_404(Profile, id=data["authorID"])
            comment = get_object_or_404(Comment, id=data["commentID"])
            post = get_object_or_404(Post, id=data["postID"])

            if comment.likes.filter(id=author.id).exists():
                comment.likes.remove(author)
            else:
                comment.likes.add(author)

            async_to_sync(channel_layer.group_send)(
                # This is the group name
                "post",
                {
                    # This should match the method name in the consumer
                    "type": "like_post",
                    "post_id": data["postID"],
                    "Post": post
                },
            )

            return Response(
                {"Like addeed to comment"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# Update comment likes
class PostReplyLikeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            channel_layer = get_channel_layer()
            data = request.data

            # Create the comment and ad it to the post
            author = get_object_or_404(Profile, id=data["authorID"])
            reply = get_object_or_404(Reply, id=data["commentID"])
            post = get_object_or_404(Post, id=data["postID"])

            if reply.likes.filter(id=author.id).exists():
                reply.likes.remove(author)
            else:
                reply.likes.add(author)

            async_to_sync(channel_layer.group_send)(
                # This is the group name
                "post",
                {
                    # This should match the method name in the consumer
                    "type": "like_post",
                    "post_id": data["postID"],
                    "Post": post
                },
            )

            return Response(
                {"Like addeed to comment"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# Post search view
class PostSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        queries = query.split(" ")
        print(queries)

        query_filter = Q()

        for q in queries:
            query_filter |= Q(description__icontains=q)

        posts = Post.objects.filter(query_filter).distinct()
        posts = posts.annotate(match_count=Count('description', filter=query_filter))
        posts = posts.order_by('-match_count', Length('description'))

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)