"""Utility file to seed landmarks database from SFgov data in seed_data/"""

from sqlalchemy import func
from model import Landmark, User, Rating, Walk, WalkLandmarkLink
from datetime import datetime

from model import connect_to_db, db
from server import app
import json


def load_civic_art():
    """Load civic art from sfgov_civic_art.json into database."""

    print "Civic Art"

    # Delete all rows in table, so we won't try and duplicate records if re-seeding
    Landmark.query.delete()

    with open('seed_data/sfgov_civic_art.json') as data_file:    
        data_file2 = data_file.read()
        data = json.loads(data_file2)

    # remove first item in list (field headings)
    data['data'].pop(0)

    for art in data['data']:
        artist = art[11]
        landmark_lat = json.loads(art[15])['coordinates'][1]
        landmark_lng = json.loads(art[15])['coordinates'][0]
        display_dimensions = art[14]
        location_description = art[16]
        medium = art[17]
        landmark_name = art[19]

        landmark = Landmark(
                      landmark_artist=artist,
                      landmark_lat=landmark_lat,
                      landmark_lng=landmark_lng,
                      landmark_display_dimensions=display_dimensions,
                      landmark_location_description=location_description,
                      landmark_medium=medium,
                      landmark_name=landmark_name)

        db.session.add(landmark)

    db.session.commit()


def load_parks():
    """Load parks from sfgov_parks.json into database."""

    print "Parks and Rec"

    # Delete all rows in table, so we won't try and duplicate records if re-seeding
    # Will delete in above function load_civic_art()
    # Landmark.query.delete()

    with open('seed_data/sfgov_parks.json') as data_file:    
        data_file2 = data_file.read()
        data = json.loads(data_file2)

    # remove first item in list (field headings)
    data['data'].pop(0)

    for park in data['data']:
      if (park[18][1] != None) and (park[18][2] != None):
        landmark_lat = park[18][1]
        landmark_lng = park[18][2]
        display_dimensions = park[15]
        landmark_description = park[9]
        landmark_name = park[8]

        landmark = Landmark(
                      landmark_lat=landmark_lat,
                      landmark_lng=landmark_lng,
                      landmark_display_dimensions=display_dimensions,
                      landmark_description=landmark_description,
                      landmark_name=landmark_name)

        db.session.add(landmark)

    db.session.commit()


def load_users():
    """Load seed users with random data generator."""
    # https://www.mockaroo.com/
    
    print "Users"

    # Start with newly generated users when re-seeding
    # User.query.delete()

    with open('seed_data/MOCK_DATA_users.json') as data_file:
      data_file2 = data_file.read()
      data = json.loads(data_file2)
   
    for user in data:
      email = user["email"]
      password = user["password"]

      user = User(
                  email=email,
                  password=password)

      db.session.add(user)

    db.session.commit()


def load_ratings():
    """Load seed ratings with random data generator."""
    # https://www.mockaroo.com/
    
    print "Ratings"

    #Start with newly generated users when re-seeding
    Rating.query.delete()

    with open('seed_data/MOCK_DATA_ratings.json') as data_file:
      data_file2 = data_file.read()
      data = json.loads(data_file2)

    for rating in data:
      landmark_id = rating['landmark_id']
      user_id = rating['user_id']
      user_score = rating['user_score']
      
      user_notes_for_landmark = None
      if user_notes_for_landmark:
        user_notes_for_landmark = rating['user_notes_for_landmark']

      rating = Rating(
                    landmark_id=landmark_id,
                    user_id=user_id,
                    user_score=user_score,
                    user_notes_for_landmark=user_notes_for_landmark)

      db.session.add(rating)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    # Import different types of data
    load_civic_art()
    load_parks()
    load_users()
    load_ratings()
  