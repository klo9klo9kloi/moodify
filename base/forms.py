from django import forms

class MatchForm(forms.Form):
	user_input = forms.CharField(label="How are you feeling today? (input float between 0.0 and 1.0)", max_length=100)