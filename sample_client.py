import requests
import json
import os


def enroll(user, file):
	print("Enrollment of " + user + " with file " + file)
	url = "http://127.0.0.1:5000/enroll"

	payload = { 'identifier': user }

	files = {
		'json': (None, json.dumps(payload), 'application/json'),
		'image': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
	}
	r = requests.post(url=url, files=files)
	response = json.loads(r.content)
	print('Error: "{}"'.format(response['error']))
	print("\n\n")


def authenticate(user, file):
	print("Authentication of " + user + " with file " + file)
	url = "http://127.0.0.1:5000/authenticate"

	payload = { 'identifier': user }

	files = {
		'json': (None, json.dumps(payload), 'application/json'),
		'image': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
	}

	r = requests.post(url=url, files=files)
	response = json.loads(r.content)
	print('Error: "{}"'.format(response['error']))
	print('Match: "{}"'.format(response['match']))
	print("\n\n")


# Enroll user Al_Gore.
enroll("Al_Gore", "Al_Gore_0001.jpg") 

# Authenticate user Al_Gore with a genuine image and an imposter image.
authenticate("Al_Gore", "Al_Gore_0002.jpg") # Genuine
authenticate("Al_Gore", "Abdullah_Gul_0001.jpg") # Imposter