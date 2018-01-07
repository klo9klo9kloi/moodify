from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('login/', views.login, name='login'),
	path('callback/', views.callback, name='callback'),
	path('home/', views.home, name='home'),
	path('refresh_token/', views.refresh_token, name='refresh_token'),
	path('matches/', views.matches, name='matches')
]