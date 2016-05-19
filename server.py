"""Walk creator."""

import sqlalchemy
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import Landmark, User, Rating, Walk, WalkLandmarkLink, connect_to_db, db

import os
import json
import requests

from mapbox import Geocoder


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ["FLASK_SECRET_KEY"]
accessToken = os.environ["MAPBOX_API_KEY"]

# Raise an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

# ================================================================================
#  Registration, Login, and User Profile
# ================================================================================


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """Processes registration when user provides email and password, or 
    displays the form."""

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        # Create a possible user object to query if the user's email is in the users table.
        # If this user doesn't yet exist, query will return None.
        possible_user = User.query.filter_by(email=email).first()

        if possible_user:
            flash("An account has already been created for this email.")
            return redirect('/login')

        # Add user to user database
        else:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()

            # add user_id to session variable, to login user automatically 
            session['user_id'] = user.user_id
            user_id = user.user_id
            flash("Your account has been created.")
            return redirect('/map')

    else:
        return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Processes login when user provides email and password, or
    displays the login form."""

    if request.method == 'POST':

        email = request.form.get("email")
        password = request.form.get("password")
        
        # Create a possible user object to query if the user's email is in the users table.
        # If this user doesn't yet exist, query will return None.
        possible_user = User.query.filter_by(email=email).first()

        if possible_user and possible_user.password == password:

            # add user_id to session variable 
            session['user_id'] = possible_user.user_id
            flash("You are logged in!")
            user_id = possible_user.user_id

            return redirect('/map')
        else:
            flash("Verify email and password entered is correct.")
            return redirect('/login')

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """Removes user_id from the session"""

    session.pop('user_id', None)
    flash("Logged out.")

    return redirect('/')


@app.route('/profile')
def show_user():
    """Return page showing details:  walks, landmarks rated, scores."""

    user = User.query.filter_by(user_id=session.get('user_id')).first()

    ratings = user.ratings
    walks = user.walks
    
    return render_template('profile.html', 
                            user=user, 
                            ratings=ratings, 
                            walks=walks)


# ================================================================================
#  Initial map rendering
# ================================================================================

@app.route('/map')
def display_map():
    """Display the initial map"""

    waypoints = []

    return render_template('mapbox.html', 
                            waypoints=waypoints)


@app.route('/initial_landmarks.geojson')
def initial_landmarks_json():
    """Pull a limited set of landmarks for initial map display."""

    initial_landmarks_geojson = {
                        "type": "FeatureCollection",
                        "features": [
                            {
                            "type": "Feature",
                            "properties": {
                                "name": landmark.landmark_name,
                                "description": landmark.landmark_description,
                                "artist":  landmark.landmark_artist,
                                "display-dimensions": landmark.landmark_display_dimensions,
                                "location-description": landmark.landmark_location_description,
                                "medium": landmark.landmark_medium
                                },
                            "geometry": {
                                "coordinates": [
                                    landmark.landmark_lng,
                                    landmark.landmark_lat],
                                "type": "Point"
                            },
                            "id": landmark.landmark_id
                            }
                        for landmark in Landmark.query.limit(20)
                        ]
                    }

    return jsonify(initial_landmarks_geojson)


@app.route('/landmarks.geojson')
def landmarks_json():
    """Send landmark data for map layer as Geojson from database."""

    landmarks_geojson = {
                        "type": "FeatureCollection",
                        "features": [
                            {
                            "type": "Feature",
                            "properties": {
                                "name": landmark.landmark_name,
                                "description": landmark.landmark_description,
                                "artist":  landmark.landmark_artist,
                                "display-dimensions": landmark.landmark_display_dimensions,
                                "location-description": landmark.landmark_location_description,
                                "medium": landmark.landmark_medium
                                },
                            "geometry": {
                                "coordinates": [
                                    landmark.landmark_lng,
                                    landmark.landmark_lat],
                                "type": "Point"
                            },
                            "id": landmark.landmark_id
                            }
                        for landmark in Landmark.query.all()
                        ]
                    }

    return jsonify(landmarks_geojson)


# ================================================================================
#  Map interaction
# ================================================================================

@app.route('/has_origin')
def has_origin():
    """Prompt user to enter an origin or explore if no destinations have been added to session."""

    origin = {
        'status': False
    }

    if len(session['waypoints']) > 0:
        origin['status'] = True

    return jsonify(origin)


# FIXME /add_destination so address input and popup selection both work



@app.route('/geocode', methods=['POST'])
def geocode():
    """User inputs address.  Convert to geojson lat_long coordinates and add to session."""

    destination = request.form.get("destination")

    # check if in database first???
 
    # geocoder = Geocoder()
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/%s.json?access_token=%s" % (destination, accessToken)
    response = requests.get(url)
    # import pdb; pdb.set_trace()
    response = response.json()
    place_name = response['features'][0]['place_name']
    coordinates = response['features'][0]['geometry']['coordinates']
    data = {
        "place_name": place_name,
        "coordinates": coordinates
    }
    
    session['waypoints'].append(data)

    return jsonify(data)


@app.route('/add_destination', methods=['POST'])
def add_destination():
    """Add a new destination to the session from popup marker."""

    landmark_id = request.form.get("landmark_id")
 
    # import pdb; pdb.set_trace();
    destination = Landmark.query.filter(Landmark.landmark_id == landmark_id).first()
    
    # FIXME destination.landmark_name

    place_name = destination.landmark_name
    coordinates = [destination.landmark_lng, destination.landmark_lat]

    data = {
        "place_name": place_name,
        "coordinates": coordinates
    }

    if 'waypoints' in session:
        # mapbox.Directions limits routes to 25 places of interest
        if len(session['waypoints']) < 25:
            if data in session['waypoints']:
                flash("Already added.")
            else: 
                session['waypoints'].append(data)
                print session['waypoints']
                flash("Added.")
        else:
            flash("Only 25 places can be included in a trip.")

    else:
        session['waypoints'] = [data]
        print session['waypoints']
        flash("Added.")
    
    return jsonify(data)



@app.route('/save_destination', methods=['POST'])
def save_destination():
    """User does not add destination to their trip, but saves the destination for later."""

    landmark_id = request.form.get("landmark_id")

    destination = Landmark.query.filter(Landmark.landmark_id == landmark_id).first()

    if 'saved' in session:
        session['saved'].append(destination)

    else:
        session['saved'] = destination

    return jsonify(destination)




@app.route('/origin_and_destination')
def return_origin_and_destination():
    """Return origin and destination from session's waypoints key."""

    waypoints_list = session['waypoints']

    if len(waypoints_list) <= 1:
        flash('Please enter at least 2 destinations for your trip.')
    else:
        origin = session['waypoints'][0]
        destination = session['waypoints'][-1]

    data = {
        "origin": origin,
        "destination": destination
    }

    return jsonify(data)



@app.route('/route_directions')
def get_directions_geojson():
    """Get directions via Mapbox Directions API with all the waypoints in the session."""

    # https://github.com/mapbox/intro-to-mapbox/blob/master/demos/directions.html
    # https://github.com/mapbox/mapbox-directions.js
    
    # import pdb; pdb.set_trace();
    waypoints_list = session['waypoints']
    route_list = []

    for waypoint in waypoints_list:
        lng = str(waypoint['coordinates'][0]) 
        lat = str(waypoint['coordinates'][1]) 
        pair = lng + ',' + lat
        # pair = pair[1:-1]
        route_list.append(pair)
 
    route_list = ';'.join(route_list)

    url = "https://api.mapbox.com/directions/v5/mapbox/walking/%s.json?access_token=%s&geometries=geojson&steps=true" % (route_list, accessToken)

    response = requests.get(url)
    response = response.json()

    return jsonify(response)



@app.route('/return_all_waypoints')
def return_all_waypoints():
    """Return all waypoints via get request."""

    waypoints = session['waypoints']

    return jsonify(waypoints)



@app.route('/clear', methods=['POST'])
def clear_waypoints():
    """Clear waypoints from session."""

    session['waypoints'] = []

    return "Cleared"



# ================================================================================
#  Phase 2: landmark ratings, walk score, user notes
# ================================================================================


@app.route('/landmarks/<int:landmark_id>', methods=['GET'])
def show_landmark(landmark_id):
    """Show the details of a particular landmark."""

    # Querying landmarks table to get landmark object
    landmark = Landmark.query.get(landmark_id)
    user_id = session.get('user_id')

    if user_id:
        user_rating = Rating.query.filter_by(
                                            landmark_id=landmark_id, 
                                            user_id=user_id
                                            ).first()
    else:
        user_rating = None

    # Get the average rating of a landmark
    rating_scores = [r.user_score for r in Rating.user_score]
    avg_rating = float(sum(rating_scores))/len(rating_scores)


    # if (not user_rating) and user_id:
    #     user = User.query.get(user_id)
        #     if user:
        #         prediction = user.predict_rating(movie)
    ratings = landmark.ratings

    return render_template('landmark_details.html', 
                            landmark=landmark, 
                            ratings=ratings,
                            user_rating=user_rating,
                            average=avg_rating)
                          


@app.route('/rate_landmark', methods=["POST"])
def rate_landmark():

    score = request.form.get("score")
    landmark_id = request.form.get("landmark_id")
    user_id = session['user_id']


    # Create a possible_rating object to query if user_id AND landmark_id is in the ratings table
    possible_rating = Rating.query.filter(Rating.user_id == user_id, Rating.landmark_id == landmark_id).first()
    
    # If this score does not yet exist, we will add to the session database.
    # If this score already exists, we will update the value of the existing score.
    if possible_rating:
        possible_rating.score = score
        flash("Your rating has been updated.")
    else:
        # Instantiate new rating to add to the user database 
        new_rating = Rating(score=score, 
                            landmark_id=landmark_id, 
                            user_id=user_id)
        db.session.add(new_rating)
        flash("Rating saved.")

    db.session.commit()
    return redirect('/')




@app.route('/debugger')
def display_debug_message():
    """Display session and preserves dictionary format in colorbox alert."""

    return jsonify(session)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
