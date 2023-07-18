from rest_framework import generics, status
from django.contrib.auth.models import User
from .serializers import UserCreateSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerialzer
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from Posts.models import Post
from Posts.serializers import PostSerializer

# Create your views here.
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


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
    
class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the JWT token from the request header
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return Response({'error': 'Authorization header is missing'})

        auth_header_parts = auth_header.split(' ')
        if len(auth_header_parts) != 2 or auth_header_parts[0] != 'Bearer':
            return Response({'error': 'Authorization header is not in the correct format'})

        token = auth_header_parts[1]

        # Retrieve the authenticated user from the token
        user = get_user_from_token(token)
        profile = get_object_or_404(Profile, user=str(user.id))
        serilizer = ProfileSerialzer(profile)

        # Return a response
        return Response(serilizer.data)
    

#User Follow Hanlder
class UserFollowerAddView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Retrieve the JWT token from the request header
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return Response({'error': 'Authorization header is missing'})

        auth_header_parts = auth_header.split(' ')
        if len(auth_header_parts) != 2 or auth_header_parts[0] != 'Bearer':
            return Response({'error': 'Authorization header is not in the correct format'})

        token = auth_header_parts[1]

        # Retrieve the authenticated user from the token
        user = get_user_from_token(token)
        follower = get_object_or_404(Profile, user=str(user.id))
        following = get_object_or_404(Profile, id=str(pk))

        if following.followers.filter(id=follower.id).exists():
            following.followers.remove(follower)
        else:
            following.followers.add(follower)

        serilizer = ProfileSerialzer(following)

        # Return a response
        return Response(serilizer.data)
    
class UserByIdView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Retrieve the authenticated user from the token
        profile = get_object_or_404(Profile, id=pk)
        serilizer = ProfileSerialzer(profile)

        # Return a response
        return Response(serilizer.data)
    

#User Posts
class UserPostsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Retrieve the authenticated user from the token
        profile = get_object_or_404(Profile, id=pk)
        posts = Post.objects.filter(auhtor__id=pk)
        serilizer = PostSerializer(posts, many=True)

        # Return a response
        return Response(serilizer.data)
    

class LogoutView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refreshToken']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            print(e)
            return Response(
                {'detail': 'Failed to logout. Please try again.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {'detail': 'You have successfully logged out.'}, 
            status=status.HTTP_200_OK
        )