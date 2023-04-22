import requests
import json
import os

## ENROLL ##
print("Enrollment")
url = "http://127.0.0.1:5000/enroll"
file = 'Al_Gore_0001.jpg'

payload = { 'identifier': 'Al_Gore' }

files = {
    'json': (None, json.dumps(payload), 'application/json'),
    'image': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
}

r = requests.post(url=url, files=files)
response = json.loads(r.content)
print('Error: "{}"'.format(response['error']))

## AUTHENTICATE ##
print("\n\n\nAuthentication")
url = "http://127.0.0.1:5000/authenticate"
file = 'Al_Gore_0002.jpg'

payload = { 'identifier': 'Al_Gore' }

files = {
    'json': (None, json.dumps(payload), 'application/json'),
    'image': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
}

r = requests.post(url=url, files=files)
response = json.loads(r.content)
print('Error: "{}"'.format(response['error']))
print('Match: "{}"'.format(response['match']))