#!/usr/bin/env python3

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS, cross_origin
import time
import random
import face_recognition
import os
import json
import numpy as np
import cv2

################# CONFIGURATION ################
host = "0.0.0.0"
port = 5000
use_template_protection = False
################################################

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return "Hello world!"

@app.route('/enroll', methods=['POST'])
def enroll():
	response = dict()
	response['error'] = 'Unknown error'
	data = json.loads(request.form['json'])
	identifier = data.get('identifier')	
	fs = request.files.get('image')
	if fs and identifier:
		file_bytes = np.fromstring(fs.read(), np.uint8)
		img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
		embeddings = get_largest_embedding(img)
		if len(embeddings) > 0:
			name = "embeddings_" + identifier + ".npy"
			np.save(name, embeddings)
			response['error'] =  ''
		else:
			response['error'] = 'Unable to locate face'
	else:
		response['error'] = 'Invalid request - Missing image or identifier'
	return jsonify(response)
	
	
@app.route('/authenticate', methods=['POST'])
def authenticate():
	response = dict()
	response['error'] = 'Unknown Error'
	response['match'] = False
	data = json.loads(request.form['json'])
	identifier = data.get('identifier')	
	fs = request.files.get('image')
	if fs and identifier:
		file_bytes = np.fromstring(fs.read(), np.uint8)
		img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
		embeddings = get_largest_embedding(img)
		if len(embeddings) > 0:
			name = "embeddings_" + identifier + ".npy"
			if os.path.exists(name):
				response['match'] = check_match(name, embeddings)
				response['error'] =  ''
			else:
				response['error'] = "User not enrolled"
		else:
			response['error'] = 'Unable to locate face'
	else:
		response['error'] = 'Invalid request - Missing image or identifier'
	return jsonify(response)
	

def check_match(name, embeddings):
	if use_template_protection:
		return False # To be implemented
	else:
		enrolled_embeddings = np.load(name)
		match = bool(face_recognition.compare_faces([enrolled_embeddings], embeddings)[0])
		return match


def get_largest_embedding(image):
	face_locations = face_recognition.face_locations(image)
	if len(face_locations) == 0:
		return []
	biggest_ind = -1
	maxsize = -1
	i = 0
	for (top, right, bottom, left) in face_locations:
		size = abs((top-bottom) * (right-left))
		if size > maxsize:
			maxsize = size
			biggest_ind = i
		i += 1
	face_encodings = face_recognition.face_encodings(image, [face_locations[biggest_ind]])
	return face_encodings[0]    

if __name__ == '__main__':    
    app.run(debug=True, host=host, port=port)
