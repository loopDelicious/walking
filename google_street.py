"""Utility file to pull images via Google Street View API and host via Imgur Image Upload API.
Seed only once so as not to exceed rate limits."""

import sqlalchemy
from model import Landmark, User, Rating, Walk, WalkLandmarkLink, LandmarkImage, connect_to_db, db

from flask import Flask, render_template, redirect, request, flash, session, jsonify, Response
from server import app
import os
import json
import time
import requests  

app = Flask(__name__)

googleKey = os.environ["GOOGLE_API_KEY"]


def load_art_images():
  """Load civic art lat-lng coordinates from SF open data.  
  Pull images from Google Street View API from location coordinates."""

  print "Civic Art"

  # Delete all rows in table, so we won't try and duplicate records if re-seeding
  LandmarkImage.query.delete()

  with open('seed_data/sfgov_civic_art.json') as data_file:    
      data_file2 = data_file.read()
      data = json.loads(data_file2)

  # remove first item in list (field headings)
  data['data'].pop(0)

  for art in data['data']:
      # retrieve lat-lng coordinates
      landmark_lat = json.loads(art[15])['coordinates'][1]
      landmark_lng = json.loads(art[15])['coordinates'][0]
      coordinates = "%s,%s" % (landmark_lat, landmark_lng)
      # query landmark object and retrieve landmark_id
      landmark = Landmark.query.filter(Landmark.landmark_lat==landmark_lat, Landmark.landmark_lng==landmark_lng).first()
      landmark_id = landmark.landmark_id

      # formulating url to retrieve Google Street View image
      # width/height in pixels
      size = '300x200'
      google_url = "https://maps.googleapis.com/maps/api/streetview?location=%s&size=%s&key=%s" % (coordinates, size, googleKey)
  
      # post request to imgur image upload API (who makes call to Google with authorization)
      headers = {
        'Authorization': 'Client-ID 462d3619fb2210d'
        }
      imgur_response = requests.post('https://api.imgur.com/3/image', data = {'image':google_url}, headers=headers)
      imageurl = imgur_response.json()['data']['link']

      landmarkImage = LandmarkImage(
                              landmark_id=landmark_id,
                              landmark_coordinates=coordinates,
                              imageurl=imageurl)
    
      db.session.add(landmarkImage)
      db.session.commit()
      # sleep so as not to exceed rate limits of >5 imgur uploads per second
      time.sleep(10)
  return 


def load_parks_images():
  """Load park lat-lng coordinates from SF open data.  
  Pull images from Google Street View API from location coordinates."""

  print "Parks and Rec"
  
  with open('seed_data/sfgov_parks.json') as data_file:    
    data_file2 = data_file.read()
    data = json.loads(data_file2)
    
    # remove first item in list (field headings)
    data['data'].pop(0)

    for park in data['data']:
      if (park[18][1] != None) and (park[18][2] != None):
        # retrieve lat-lng coordinates
        landmark_lat = park[18][1]
        landmark_lng = park[18][2]
        coordinates = "%s,%s" % (landmark_lat, landmark_lng)
        # query landmark object and retrieve landmark_id
        landmark = Landmark.query.filter(Landmark.landmark_lat==landmark_lat, Landmark.landmark_lng==landmark_lng).first()
        landmark_id = landmark.landmark_id

        # formulating url to retrieve Google Street View image
        # https://developers.google.com/maps/documentation/streetview/intro#introduction
        # width/height in pixels
        size = '300x200'
        google_url = "https://maps.googleapis.com/maps/api/streetview?location=%s&size=%s&key=%s" % (coordinates, size, googleKey)
    
        # post request to imgur image upload API (who makes call to Google with authorization)
        # https://api.imgur.com/endpoints/image
        headers = {
          'Authorization': 'Client-ID 462d3619fb2210d'
          }
        imgur_response = requests.post('https://api.imgur.com/3/image', data = {'image':google_url}, headers=headers)
        imageurl = imgur_response.json()['data']['link']

        landmarkImage = LandmarkImage(
                                landmark_id=landmark_id,
                                landmark_coordinates=coordinates,
                                imageurl=imageurl)
      
        db.session.add(landmarkImage)
        db.session.commit()
        # sleep so as not to exceed rate limits of >5 imgur uploads per second
        time.sleep(10)
  return 


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

load_art_images()
load_parks_images()
