from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Create your views here.
from django.http import HttpResponse
from .forms import MatchForm, RegisterForm, LoginForm
from .models import MoodifyUser

import base64, requests, math, random

client_id = 'cd960552ab404a439a6b8f100caed209'
client_secret = '371e9a11868642f095646f001ca55ee3'
scope = 'user-read-private user-read-email user-top-read'
login_redirect = 'http://127.0.0.1:8000/callback/'
state_key = 'spotify_auth_state'
scope = 'user-read-private user-read-email user-top-read'


SPOTIFY_APIENDPOINT = 'https://api.spotify.com'
SPOTIFY_ACCOUNTENDPOINT = 'https://accounts.spotify.com'
SEARCH_ENDPOINT = '/v1/search'
ME_ENDPOINT = '/v1/me'

def generateRandomString(length):
  text = ''
  possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for i in range(len(possible)):
    text += possible[math.floor(random.random() * len(possible))];
  return text


def index(request):
	return render(request, 'base/index.html')

def login(request):
	if request.method == 'POST':
		login_form = LoginForm(data=request.POST)
		if login_form.is_valid():
			user = User.objects.get(username=login_form.cleaned_data['username'])
			if not hasattr(user, 'moodify'):
				return redirect('authorize')
			return redirect('home', user.moodify.id)
		else:
			messages.error(request, 'Username or Password Incorrect')

	form = LoginForm()
	context = {
		'type': 'Login',
		'form': form,
		'action': '/login/'

	}
	return render(request, 'base/form.html', context)

def register(request):
	if request.method == 'POST':
		reg_form = RegisterForm(data=request.POST)
		if reg_form.is_valid():
			user = reg_form.save()
			return redirect('authorize')
		else:
			messages.error(request, 'One or more fields were invalid')
	form = RegisterForm()
	context = {
		'type': 'Register',
		'form': form,
		'action': '/register/'

	}
	return render(request, 'base/form.html', context)


def authorize_spotify(request):
	state = generateRandomString(16) 
	cookies = {state_key: state}
	# p = {'client_id': client_id, 'response_type': 'code', 'redirect_uri': 'http://127.0.0.1:8000/home/', 'show_dialog': True, 'state': state}
	# r = requests.get(SPOTIFY_ACCOUNTENDPOINT + '/authorize', params=p, cookies=cookies, allow_redirects=True)
	# return redirect(r.url)
	url = SPOTIFY_ACCOUNTENDPOINT + '/authorize/?response_type=code&state=' + state + '&redirect_uri=' + login_redirect + '&client_id=' + client_id + '&scope=' + scope
	r = redirect(url)
	r.set_cookie(state_key, state, max_age=1000)
	return r

def callback(request):
	code = request.GET.get('code', None)
	state = request.GET.get('state', None)
	error = request.GET.get('error', None)
	storedState = request.COOKIES.get(state_key, None) if request.COOKIES else None

	if (state is None) or (state != storedState):
		messages.error(request, 'State mismatch.')
		return redirect('index')
	else:
		request.COOKIES[state_key] = None
		d = {'code': code, 'redirect_uri': login_redirect, 'grant_type': 'authorization_code', 'client_id': client_id, 'client_secret': client_secret}
		r = requests.post(SPOTIFY_ACCOUNTENDPOINT + '/api/token', data=d)

		if r.status_code == requests.codes.ok:
			response = r.json()
			user_info = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT, headers={'Authorization': 'Bearer ' + response['access_token']}).json()

			user=User.objects.get(email=user_info['email'])
			print(user)
			try:
				moodify_user = user.moodify
				print('here')
			except:
				moodify_user = MoodifyUser(user=user, display_name=user_info['display_name'], spotify_id=user_info['id'], access_token=response['access_token'], 
					refresh_token=response['refresh_token'], spotify_profile_url=user_info['external_urls']['spotify'], spotify_image=user_info['images'][0]['url'])
				moodify_user.save()
				user.moodify = moodify_user
			print(moodify_user)
			return redirect('home', moodify_user.id)
		else:
			messages.error(request, 'Error: '+ str(r.status_code))
			return redirect('index')

def home(request, m_user_id):
	moodify_user = get_object_or_404(MoodifyUser, id=m_user_id)
	access_token = moodify_user.access_token
	refresh_token = moodify_user.refresh_token
	if not access_token:
		messages.error(request, 'Access token does not exist.')
		return redirect('index')
	else:
		top_tracks = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT + '/top/tracks', headers={'Authorization': 'Bearer ' + access_token}).json()
		form = MatchForm()


		context = {
			'id': user_id,
			'access_token': access_token,
			'refresh_token': refresh_token,
			'display_name': moodify_user.display_name,
			'email': moodify_user.user.email,
			'spotify_id': moodify_user.spotify_id,
			'profile': moodify_user.spotify_profile_url,
			'images': moodify_user.spotify_image,
			'top_tracks': top_tracks,
			'form': form
		}
		return render(request, 'base/home.html', context)

def refresh_token(request, user_id):
	moodify_user = get_object_or_404(MoodifyUser, id=user_id)
	rt = moodify_user.refresh_token
	if not rt:
		messages.error(request, 'Refresh token does not exist.')
		return redirect('index')
	d = {'grant_type': 'refresh_token', 'refresh_token': rt, 'client_id': client_id, 'client_secret': client_secret}
	r = requests.post(SPOTIFY_ACCOUNTENDPOINT + '/api/token', data=d)

	if r.status_code == requests.codes.ok:
		response = r.json()
		moodify_user.access_token = response['access_token']
		return redirect('home', username)
	else:
		messages.error(request, 'Error: ' + str(r.status_code))
		return redirect('index')

def matches(request, user_id):
	moodify_user = get_object_or_404(MoodifyUser, id=user_id)
	if request.method == 'GET':
		form = MatchForm(request.GET)
		if form.is_valid():

			valence = float(form.cleaned_data['user_input'])

			access_token = moodify_user.access_token

			top_tracks = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT + '/top/tracks/?limit=50', headers={'Authorization': 'Bearer ' + access_token}).json()

			ids = ''
			for track in top_tracks['items']:
				ids = ids + track['id'] + ','

			ids = ids[:-1]
			audio_features = requests.get(SPOTIFY_APIENDPOINT + '/v1/audio-features/?ids=' + ids, headers={'Authorization': 'Bearer ' + access_token}).json()

			matches = {}
			for track in audio_features['audio_features']:
				print(track['valence'])
				if (valence-0.05) < track['valence'] < (valence+0.05):
					matches[track['id']] = 1

			tracks = []
			for track in top_tracks['items']:
				if track['id'] in matches:
					tracks.append(track)

			context = {'tracks': tracks, 'id': user_id, 'images': moodify_user.spotify_image}	
			return render(request, 'base/matches.html', context)
	messages.error(request, 'Bad form submission')
	return redirect('home')


	
