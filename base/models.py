from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MoodifyUser(models.Model):
	user = models.OneToOneField(User, related_name='moodify', on_delete=models.CASCADE)
	display_name = models.CharField(max_length=100)
	spotify_id = models.CharField(max_length=62, unique=True)
	access_token = models.CharField(max_length=200, unique=True)
	refresh_token = models.CharField(max_length=200, unique=True)
	spotify_profile_url = models.URLField()
	spotify_image = models.URLField()

# chris's sad attempt at image upload
# class Document(models.Model):
# 	description = models.CharField(max_length=255, blank=True)
# 	document = models.FileField(upload_to='uploads/')
# 	uploaded_at = models.DateTimeField(auto_now_add=True)