from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile
from django.shortcuts import get_object_or_404
from utils.Image.saveImage import saveImage


class ProfileSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Profile


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    def validate_password(self, value):
        try:
            # Use Django's built-in password validation
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address is already in use.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value
    
    def create(self, validated_data):
        profile_image_data = self.initial_data["profile_image"]
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        if profile_image_data:
            self.save_profile_picture(user, profile_image_data)
        return user
    
    def save_profile_picture(self, user, profile_picture_data):
        profile_object = get_object_or_404(Profile, username=user.username)

        saveImage(
            profile_picture_data,
            profile_object,
            user
        )