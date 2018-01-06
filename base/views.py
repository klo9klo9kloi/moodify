from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse

import base64, requests, math, random

client_id = 'cd960552ab404a439a6b8f100caed209'
client_secret = 'b7dac5ea25cb4fe798887ea15a9b57ce'
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
	state = generateRandomString(16) 
	cookies = {state_key: state}
	# p = {'client_id': client_id, 'response_type': 'code', 'redirect_uri': 'http://127.0.0.1:8000/home/', 'show_dialog': True, 'state': state}
	# r = requests.get(SPOTIFY_ACCOUNTENDPOINT + '/authorize', params=p, cookies=cookies, allow_redirects=True)
	# return redirect(r.url)
	url = SPOTIFY_ACCOUNTENDPOINT + '/authorize/?response_type=code&state=' + state + '&redirect_uri=' + login_redirect + '&show_dialog=True&client_id=' + client_id + '&scope=' + scope
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
			return redirect('/home/?access_token=' + response['access_token'] + '&refresh_token=' + response['refresh_token'])
		else:
			messages.error(request, 'Error: '+ str(r.status_code))
			return redirect('index')

def home(request):
	access_token = request.GET.get('access_token', None)
	refresh_token = request.GET.get('refresh_token', None)
	if not access_token:
		messages.error(request, 'Access token does not exist.')
		return redirect('index')
	else:
		user_info = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT, headers={'Authorization': 'Bearer ' + access_token}).json()
		top_tracks = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT + '/top/tracks', headers={'Authorization': 'Bearer ' + access_token}).json()

		context = {
			'access_token': access_token,
			'refresh_token': refresh_token,
			'display_name': user_info['display_name'],
			'email': user_info['email'],
			'id': user_info['id'],
			'country': user_info['country'],
			'external_urls': user_info['external_urls'],
			'href': user_info['href'],
			'images': user_info['images'],
			'top_tracks': top_tracks
		}
		return render(request, 'base/home.html', context)

def refresh_token(request, rt):
	if not rt:
		messages.error(request, 'Refresh token does not exist.')
		return redirect('index')
	d = {'grant_type': 'refresh_token', 'refresh_token': rt, 'client_id': client_id, 'client_secret': client_secret}
	r = requests.post(SPOTIFY_ACCOUNTENDPOINT + '/api/token', data=d)

	if r.status_code == requests.codes.ok:
		response = r.json()
		return redirect('/home/?access_token=' + response['access_token'] + '&refresh_token=' + rt)
	else:
		messages.error(request, 'Error: ' + str(r.status_code))
		return redirect('index')

# def home(request):
# 	code = request.GET.get('code', None)
# 	state = request.GET.get('state', None)
# 	error = request.GET.get('error', None)
# 	storedState = request.COOKIES.get(state_key, None) if request.COOKIES else None

# 	if (state is None) or (state != storedState):
# 		print('state_mismatch')
# 		return redirect('index')
# 	else:
# 		request.COOKIES[state_key] = None
# 		d = {'code': code, 'redirect_uri': login_redirect, 'grant_type': 'authorization_code', 'client_id': client_id, 'client_secret': client_secret}
# 		r = requests.post(SPOTIFY_ACCOUNTENDPOINT + '/api/token', data=d)

# 		if r.status_code == requests.codes.ok:
# 			response = r.json()

# 			user_info = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT, headers={'Authorization': 'Bearer ' + response['access_token']}).json()
# 			top_tracks = requests.get(SPOTIFY_APIENDPOINT + ME_ENDPOINT + '/top/tracks', headers={'Authorization': 'Bearer ' + response['access_token']}).json()

# 			context = {
# 				'access_token': response['access_token'],
# 				'refresh_token': response['refresh_token'],
# 				'expires_in': response['expires_in'],
# 				'display_name': user_info['display_name'],
# 				'email': user_info['email'],
# 				'id': user_info['id'],
# 				'country': user_info['country'],
# 				'external_urls': user_info['external_urls'],
# 				'href': user_info['href'],
# 				'images': user_info['images'],
# 				'top_tracks': top_tracks
# 			}
# 			return render(request, 'base/home.html', context)
# 		else:
# 			print(r.status_code)
# 			return redirect('index')
	

	
