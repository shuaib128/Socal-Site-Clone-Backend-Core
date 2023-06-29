from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional fields for the profile model
    username = models.CharField(max_length=200, default="username")
    firstname = models.CharField(max_length=200, default="firstname")
    lastname = models.CharField(max_length=200, default="lastname")
    bio = models.TextField(max_length=500, blank=True)
    email = models.EmailField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        default='default_profile_picture.png'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        self.firstname = self.user.first_name
        self.lastname = self.user.last_name
        self.email = self.user.email
        self.username = self.user.username
        super().save(*args, **kwargs)