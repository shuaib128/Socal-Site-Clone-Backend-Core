import base64
from django.core.files.base import ContentFile

def saveImage(profile_picture_data, profile_object, user):
    format, imgstr = profile_picture_data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name=f"{user.username}_profile_picture.{ext}")
    profile_object.profile_picture.save(f"{user.username}_profile_picture.{ext}", data, save=True)