import requests
import json
import os


## ENROLL ##
print("Enrollment of Al_Gore_0001")
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


## GENUINE AUTHENTICATION ##
print("\n\n\nAuthentication of Al_Gore_0002")
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


## IMPOSTER AUTHENTICATION ##
print("\n\n\nAuthentication of Abdullah_Gul_0001")
url = "http://127.0.0.1:5000/authenticate"
file = 'Abdullah_Gul_0001.jpg'

payload = { 'identifier': 'Al_Gore' }

files = {
    'json': (None, json.dumps(payload), 'application/json'),
    'image': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
}

r = requests.post(url=url, files=files)
response = json.loads(r.content)
print('Error: "{}"'.format(response['error']))
print('Match: "{}"'.format(response['match']))