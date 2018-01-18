import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()
file_name = 'sadiu.jpg'
with io.open(file_name, 'rb') as image_file:
	content = image_file.read()
image = types.Image(content=content)
response = client.face_detection(image=image)
try:
	valence = response.face_annotations[0].joy_likelihood
except IndexError:
	exit('lolz fail')
print(valence is "VERY_UNLIKELY")