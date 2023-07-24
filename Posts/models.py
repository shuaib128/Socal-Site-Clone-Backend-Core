import os
import math
import ffmpeg
import readtime
from django.db import models
from Users.models import Profile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from background_task import background
from django.conf import settings
import base64

# Create your models here.
#Media files (Images/Videos)
@deconstructible
class FileTypeValidator:
    allowed_types = ['image/jpeg', 'image/png', 'video/mp4', 'video/quicktime']

    def __call__(self, value):
        if value.file.content_type not in self.allowed_types:
            raise ValidationError('Only image and video files are allowed.')

# Main Media file
class MediaFile(models.Model):
    filename = models.CharField(max_length=255, default="")
    file = models.FileField(upload_to='media/postsMedia', blank=True)
    hls_directory = models.CharField(max_length=255, null=True, blank=True)

    #Append chunk method
    def append_chunk(self, chunk_base64):
        # Remove the "data:application/octet-stream;base64," prefix from the Base64 string
        prefix = "data:application/octet-stream;base64,"
        if chunk_base64.startswith(prefix):
            chunk_base64 = chunk_base64[len(prefix):]

        # decode the base64 string into bytes
        chunk = base64.b64decode(chunk_base64)

        if self.file:
            self.file.close()
            self.file.open(mode='ab') # append in binary mode
        else:
            self.file.save(self.filename, ContentFile(b''), save=False)  # Save an empty file
            self.file.close()
            self.file.open(mode='ab')
        self.file.write(chunk)
        self.file.close()
        self.save()

    # Start HLS procress
    def start_encoding(self):
        print("start process...")
        encode_video_to_hls(self.id)

# encode_video_to_hls() function
@background(schedule=0)     
def encode_video_to_hls(mediafile_id):
    print("running process...")
    mediafile = MediaFile.objects.get(id=mediafile_id)
    input_file = mediafile.file.path
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(mediafile.id))
    os.makedirs(output_dir, exist_ok=True)

    resolutions = ['360p', '720p']  # Add more resolutions as needed
    master_playlist_content = '#EXTM3U\n'
    
    try:
        for res in resolutions:
            res_output_dir = os.path.join(output_dir, res)
            os.makedirs(res_output_dir, exist_ok=True)
            output_file = os.path.join(res_output_dir, 'playlist.m3u8')

            # Transcode and segment
            ffmpeg.input(input_file).output(output_file, format='hls', start_number=0, hls_time=10, hls_list_size=0, vf='scale=-2:' + res[:-1]).run(overwrite_output=True)
            master_playlist_content += '#EXT-X-STREAM-INF:BANDWIDTH={0}\n{1}/playlist.m3u8\n'.format(int(res[:-1])*1000, res)

        # Save master playlist
        with open(os.path.join(output_dir, 'master.m3u8'), 'w') as f:
            f.write(master_playlist_content)

        # Save the HLS directory to the MediaFile
        mediafile.hls_directory = output_dir
        mediafile.save()
    except ffmpeg.Error as e:
        print('Error creating HLS segments:', e)


#Reply models
class Reply(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, default=0)
    reply = models.TextField(default="Body")
    likes = models.ManyToManyField(Profile, related_name="Replylikes", null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add= True)
    last_edited= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)


#Comments model
class Comment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, default=0)
    comment = models.TextField(default="Body")
    pub_date = models.DateTimeField(auto_now_add= True)
    likes = models.ManyToManyField(Profile, related_name="Commentlikes", null=True, blank=True)
    last_edited= models.DateTimeField(auto_now= True)
    replyes = models.ManyToManyField(Reply, related_name='Replyes', null=True, blank=True)

    class Meta:
        ordering = ['pub_date',]

class Post(models.Model):
    auhtor = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    media_files = models.ManyToManyField(MediaFile, related_name='media', null=True, blank=True)
    likes = models.ManyToManyField(Profile, related_name="likes", null=True, blank=True)
    comments = models.ManyToManyField(Comment, related_name='Comments', null=True, blank=True)

    #Get reading Time
    def get_readtime(self):
        return readtime.of_text(self.description).text

    #Get time afetr post
    def whenpublished(self):
        now = timezone.now()
        diff= now - self.pub_date

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds= diff.seconds           
            if seconds == 1:
                return str(seconds) +  "second ago"          
            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes= math.floor(diff.seconds/60)

            if minutes == 1:
                return str(minutes) + " minute ago"           
            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours= math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days= diff.days
        
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months= math.floor(diff.days/30)           

            if months == 1:
                return str(months) + " month ago"
            else:
                return str(months) + " months ago"


        if diff.days >= 365:
            years= math.floor(diff.days/365)
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"

    def __str__(self):
        return self.description + "-" + str(self.id)