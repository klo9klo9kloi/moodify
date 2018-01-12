from django.contrib import admin

# Register your models here.
from .models import MoodifyUser

class MoodifyAdmin(admin.ModelAdmin):
    fields = ['user', 'display_name', 'spotify_id', 'access_token', 'refresh_token', 'spotify_profile_url', 'spotify_image']

admin.site.register(MoodifyUser, MoodifyAdmin)