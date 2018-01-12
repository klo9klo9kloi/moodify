from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('login/', views.login, name='login'),
	path('register/', views.register, name='register'),
	path('authorize/', views.authorize_spotify, name='authorize'),
	path('callback/', views.callback, name='callback'),
	path('home/<user_id>', views.home, name='home'),
	path('refresh_token/<user_id>', views.refresh_token, name='refresh_token'),
	path('matches/<user_id>', views.matches, name='matches')
]