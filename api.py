#!/usr/bin/env python3

from flask import Flask, render_template_string, request, jsonify
from fuzzy_extractor import FuzzyExtractor
from flask_cors import CORS, cross_origin
from hashlib import sha512
import time
import random
import face_recognition
import os
import json
import numpy as np
import cv2

################### CONFIGURATION ###################
host = "0.0.0.0"
port = 5000
use_template_protection = True
num_bits_per_feature = 20000
locker_size = 400
lockers = 4500
#####################################################

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
fe = FuzzyExtractor()


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
			enroll_user(name, embeddings)
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


def enroll_user(name, embeddings):
	if use_template_protection:
		w = get_w_from_embeddings(embeddings, num_bits_per_feature)
		r, p = fe.gen(w, locker_size=locker_size, lockers=lockers, confidence=None)
		hashed_record = sha512(r).digest()
		np.save(name, (hashed_record, p), allow_pickle=True)
	else:
		np.save(name, embeddings)


def check_match(name, embeddings):
	if use_template_protection:
		(hashed_record, p) = np.load(name, allow_pickle=True)
		w_prime = get_w_from_embeddings(embeddings, num_bits_per_feature)
		r_prime = fe.rep(w_prime, p)
		if r_prime == None:
			return False
		hashed_record_prime = sha512(r_prime).digest()
		return hashed_record == hashed_record_prime
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


def normalize_embeddings(embeddings):
	global_emb_min = -1
	global_emb_max = 1
	normalized_embeddings = (embeddings - global_emb_min) / (global_emb_max - global_emb_min)
	normalized_embeddings = np.clip(normalized_embeddings, 0, 1)
	return normalized_embeddings


def get_w_from_embeddings(embeddings, num_bits_per_feature):
	normalized_embeddings = normalize_embeddings(embeddings)
	w = []
	for val in normalized_embeddings:
		thresholds = np.linspace(0, 1, num_bits_per_feature + 2)[1:-1]
		bits = val > thresholds
		w.extend(bits)
	return np.array(w)

if __name__ == '__main__':    
    app.run(debug=True, host=host, port=port)
