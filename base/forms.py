from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class MatchForm(forms.Form):
	user_input = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="How are you feeling today? (input float between 0.0 and 1.0)", max_length=50)

class LoginForm(AuthenticationForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Username", max_length=20)
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Password", max_length=50)

class RegisterForm(UserCreationForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Username", max_length=20)
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Password", max_length=50)
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Re-enter Password", max_length=50)
	email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Email", help_text='Must match your Spotify account email!')
