"""Walk creator."""

import sqlalchemy
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify, Response
from flask_debugtoolbar import DebugToolbarExtension

from model import Landmark, User, Rating, Walk, WalkLandmarkLink, LandmarkImage, UserSaved, connect_to_db, db

import os
import json
import bcrypt
import requests

import smtplib
from email.mime.text import MIMEText

from mapbox import Geocoder
from geopy.distance import vincenty

from datetime import date


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ["FLASK_SECRET_KEY"]
accessToken = os.environ["MAPBOX_API_KEY"]
googleKey = os.environ["GOOGLE_API_KEY"]

# Raise an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

# ================================================================================
#  Registration, Login, and User Profile
# ================================================================================

# use colorbox for login and registration modals

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
            return "An account has already been created for this email."

        # Add user to user database
        else:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()

            # add user_id to session variable, to login user automatically 
            session['user_id'] = user.user_id
            session['waypoints'] = []
            user_id = user.user_id
            message = "Your account has been created."
            return redirect('/map')
            # return redirect(url_for('/map', message=message))

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

        if possible_user and possible_user.verify_password(password):

            # add user_id to session variable and initialize waypoints key
            session['user_id'] = possible_user.user_id
            session['waypoints'] = []
            user_id = possible_user.user_id
            message = "You are logged in!"
            return redirect('/map')
            # return redirect(url_for('/map', message=message))

        else:
            return "Verify email and password entered is correct."

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """Removes user_id from the session"""

    session.pop('user_id', None)
    session.pop('waypoints', None)
    message = "Logged out."

    return redirect('/')


@app.route('/profile')
def show_user():
    """Return page showing details:  walks, landmarks rated, scores."""

    user = User.query.filter_by(user_id=session.get('user_id')).first()
    ratings = user.ratings
    
    # import pdb; pdb.set_trace()

    walks = user.walks
    # for walk in walks:
    #     origin = Landmark.query.filter(Landmark.landmark_id == walk.origin).first()
    #     origin = origin.landmark_name

    #     destination = Landmark.query.filter(Landmark.landmark_id == walk.destination).first()
    #     destination = destination.landmark_name
        
    #     metaWalks = {
    #         "walk_id": walk.walk_id,
    #         "metadata": {
    #             "origin": origin,
    #             "destination": destination,
    #             "datetime": walk.log_datetime,
    #             "duration": walk.duration,
    #             "distance": walk.distance
    #             }
    #         }

    saved = UserSaved.query.filter_by(user_id=session.get('user_id')).all()

    # import pdb; pdb.set_trace()

    return render_template('profile.html', 
                            user=user, 
                            ratings=ratings, 
                            walks=walks,
                            # metaWalks=metaWalks,
                            saved=saved)


# ================================================================================
#  Initial map rendering
# ================================================================================

@app.route('/map')
def display_map():
    """Display the initial map"""

    waypoints = session['waypoints']

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
                        # for landmark in Rating.query.order_by(Rating.user_score.desc()).limit(20)
                        # for landmark in Landmark.query.order_by(Landmark.ratings.user_score.desc()).limit(20)
                        # FIXME
                        ]
                    }

    return jsonify(initial_landmarks_geojson)


@app.route('/landmarks.geojson')
def landmarks_json():
    """Send landmark data for map layer as Geojson from database."""

    features = []


    for landmark in Landmark.query.all():
        # get the first image of a landmark, if any
        image = ""
        if len(landmark.images) > 0:
            image = landmark.images[0].imageurl 
        # get the average rating of a landmark
        avg_rating = ""
        rating_scores = [r.user_score for r in landmark.ratings]
        if len(rating_scores) > 0:
            avg_rating = float(sum(rating_scores))/len(rating_scores)
        
        features.append({
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
                        "id": landmark.landmark_id,
                        'image': image,
                        'avg_rating': avg_rating,
                        })
    
    landmarks_geojson = {
                        "type": "FeatureCollection",
                        "features": features,
                        }

    return jsonify(landmarks_geojson)


@app.route('/saved.geojson')
def saved_landmarks_json():
    """Send landmark data for saved landmarks layer as Geojson from database."""

    features = []
    saved = []
    user_id = session['user_id']
   
    landmarks = UserSaved.query.filter(UserSaved.user_id==user_id).all()
    for landmark in landmarks:
        landmark = Landmark.query.filter(Landmark.landmark_id==landmark.landmark_id).first()
        if landmark:

            image = ""
            if len(landmark.images) > 0:
                image = landmark.images[0].imageurl 
            
            avg_rating = ""
            rating_scores = [r.user_score for r in landmark.ratings]
            if len(rating_scores) > 0:
                avg_rating = float(sum(rating_scores))/len(rating_scores)

            features.append({
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
                            "id": landmark.landmark_id,
                            'image': image,
                            'avg_rating': avg_rating,
                            })
    
    saved_geojson = {
                        "type": "FeatureCollection",
                        "features": features,
                        }

    return jsonify(saved_geojson)


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



@app.route('/geocode', methods=['POST'])
def geocode():
    """User inputs address.  Convert to geojson lat_long coordinates and add to session."""

    place = request.form.get("place")

    if place[:9] == 'landmark:':
        landmark = Landmark.query.filter(Landmark.landmark_id == int(place[10:])).first()
        data = {
            "place_name": landmark.landmark_name,
            "coordinates": [landmark.landmark_lat, landmark.landmark_lng]
        }

    else:
        bbox = '-122.556125,37.705107,-122.338846,37.838462' # bounding box within which to limit results
     
        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/%s.json?proximity=-122.4194,37.7749&bbox=%s&access_token=%s" % (place[5:], bbox, accessToken)
        response = requests.get(url)
      
        response = response.json()
        place_name = response['features'][0]['place_name']
        coordinates = response['features'][0]['geometry']['coordinates']
        data = {
            "place_name": place_name,
            "coordinates": coordinates
        }
        
    session['waypoints'].append(data)

    return jsonify(data)


@app.route('/autocomplete')
def autocomplete():
    """User inputs text, and database will suggest places from landmarks database."""

    term = request.args.get('term')

    # Phase 2: keep cache keys based on search fragments, mem cache to improve responsiveness and diminish load
    landmarks = Landmark.query.filter(Landmark.landmark_name.ilike('%' + term + '%')).limit(10).all()
    possibilities = []
    bbox = '-122.556125,37.705107,-122.338846,37.838462' # bounding box within which to limit results
    # import pdb; pdb.set_trace()

    if landmarks:
        for landmark in landmarks:
            data = {
                'value': 'landmark: ' + str(landmark.landmark_id),
                'label': landmark.landmark_name.title()
            }
            possibilities.append(data)
    
    else:  # if no db results, search mapbox places with autocomplete
        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/%s.json?proximity=-122.4194,37.7749&bbox=%s&access_token=%s" % (term, bbox, accessToken)
        response = requests.get(url)
        response = response.json()

        for feature in response['features']:
            data = {
                'value': 'api: ' + feature['place_name'],
                'label': feature['place_name']
            }
            possibilities.append(data)

    if not possibilities:
        possibilities = ['No results']

    possibilities = possibilities[:10]

    return Response(json.dumps(possibilities),  mimetype='application/json')



@app.route('/add_destination', methods=['POST'])
def add_destination():
    """Add a new destination to the session from popup marker."""

    # users submitting from popup will have landmark_id
    landmark_id = request.form.get("landmark_id")

    # access attributes of the model Landmark object from db
    if landmark_id:
        destination = Landmark.query.filter(Landmark.landmark_id == landmark_id).first()
        place_name = destination.landmark_name
        coordinates = [destination.landmark_lng, destination.landmark_lat]

    # http://stackoverflow.com/questions/23889107/sending-array-data-with-jquery-and-flask
    # users saving from popup will have full geojson object
    else:
        coordinates = request.form.getlist("coordinates[]")
        place_name = request.form.get("place_name")

    # format all users into data dictionary with 2 keys
    data = {
        "place_name": place_name,
        "coordinates": coordinates
    }
    print data
    if 'waypoints' in session:
        # mapbox.Directions limits routes to 25 places of interest
        if len(session['waypoints']) < 25:
            if data in session['waypoints']:
                return "Already added."
            else: 
                session['waypoints'].append(data)
        else:
            return "Only 25 places can be included in a trip."

    else:
        session['waypoints'] = [data]
    
    return jsonify(data)


@app.route('/save_destination', methods=['POST'])
def save_destination():
    """User does not add destination to their trip, but saves the destination as a favorite."""

    # users submitting from popup will have landmark_id
    landmark_id = request.form.get("landmark_id")
    user_id = session['user_id']

    # Create a possible_saved object to query if user_id AND landmark_id is in the user_saved table
    possible_saved = UserSaved.query.filter(UserSaved.user_id == user_id, UserSaved.landmark_id == landmark_id).first()
    
    # If this saved destination does not yet exist for this user, we will add to the session database.
    if possible_saved:
        return "This destination has already been saved."
    else:
        # Instantiate new saved destination to add to the user_saved table
        new_saved = UserSaved(landmark_id=landmark_id, 
                              user_id=user_id)
        db.session.add(new_saved)
        db.session.commit()
        return "Destination saved."



# @app.route('/remove_destination', methods=['POST'])
# def remove_destination():
#     """User removes destination from their trip planning."""

#     landmark_id = request.form.get('landmark_id"')
#     landmark = Landmark.query.filter(Landmark.landmark_id == landmark.id).first()
#     landmark_name = landmark.landmark_name

#     waypoints  = request.session['waypoints']

#     if landmark_name in waypoints['place_name']:
#         waypoints.remove(landmark)
#         return "Destination removed."



@app.route('/origin_and_destination')
def return_origin_and_destination():
    """Return origin and destination from session's waypoints key."""

    waypoints = session['waypoints']

    if len(waypoints) <= 1:
        return 'Please enter at least 2 destinations for your trip.'
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

    waypoints = session['waypoints']
    route_list = []

    # add error if no waypoints added yet, OR don't show button until at least 2 waypoints

    for waypoint in waypoints:
        lng = str(waypoint['coordinates'][0]) 
        lat = str(waypoint['coordinates'][1]) 
        pair = lng + ',' + lat
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


# @app.route('/check_in_waypoints')
# def check_if_location_in_waypoints():
#     """Return True if location is in session waypoints."""

#     landmark_id = request.form.get('landmark_id"')
#     import pdb; pdb.set_trace()
#     landmark = Landmark.query.filter(Landmark.landmark_id == landmark_id).first()
#     landmark_name = landmark.landmark_name

#     waypoints = request.session['waypoints']

#     if landmark_name in waypoints['place_name']:
#         return True


@app.route('/clear', methods=['POST'])
def clear_waypoints():
    """Clear waypoints from session."""

    session['waypoints'] = []

    return "Cleared"


@app.route('/email_directions', methods=['POST'])
def email_directions():
    """User requests email directions to be sent to their phone via smtplib."""

    steps = request.form.get("email_message")

    user_id = session['user_id']
    user = User.query.filter(User.user_id==user_id).first()
    user_email = str(user.email)

    # python smartlib
    sender = 'joycelin79@gmail.com'
    receiver = [user_email]
    message = """From: From <%s>
    To: To <%s>
    Subject: Walking Directions

    %s
    """ % (sender, receiver, steps)

    # remember to start up a local SMTP server with Python
    # http://stackoverflow.com/questions/5619914/sendmail-errno61-connection-refused
    # python -m smtpd -n -c DebuggingServer localhost:1025
    try:
        s = smtplib.SMTP('localhost', 1025)
        print s
        s.sendmail(sender, receiver, message)
        s.quit()
        result = "Email sent."

    except smtplib.SMTPException:
        result = "Error: unable to send email"

    return result


# ================================================================================
#  Landmark interactions: landmark ratings, walk score, user notes, images
# ================================================================================


@app.route('/landmarks/<int:landmark_id>', methods=['GET'])
def show_landmark(landmark_id):
    """Show the details of a particular landmark."""

    # Querying landmarks table to get landmark object
    landmark = Landmark.query.get(landmark_id)

    user_id = session.get('user_id')
    user_score = None
    # if user has previously submitted a rating
    if user_id:
        user_rating = Rating.query.filter_by(
                                            landmark_id=landmark_id, 
                                            user_id=user_id
                                            ).first()
        if user_rating:
            user_score = user_rating.user_score

    else:
        user_rating = None

    # import pdb; pdb.set_trace()

    # Get the average rating of a landmark, and user reviews
    ratings = Rating.query.filter_by(landmark_id=landmark_id).all()
    rating_scores = [r.user_score for r in ratings]
    reviews = [r.user_notes_for_landmark for r in ratings]

    prediction = None

    if len(rating_scores) > 0:
        avg_rating = float(sum(rating_scores))/len(rating_scores)
    else:
        avg_rating = 0

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(landmark)

    # getting ratings from landmark object since tables are joined by db.relationship
    ratings = landmark.ratings

    images = LandmarkImage.query.filter_by(landmark_id=landmark_id).all()

    return render_template('landmark_details.html', 
                            landmark=landmark, 
                            ratings=ratings,
                            user_rating=user_rating,
                            reviews=reviews,
                            user_score=user_score,
                            prediction=prediction,
                            average=avg_rating,
                            images=images,
                            )
                          


@app.route('/rate_landmark', methods=["POST"])
def rate_landmark():
    """User rates landmark from the landmark details page."""

    score = request.form.get("score")
    landmark_id = request.form.get("landmark_id")
    user_id = session['user_id']


    # Create a possible_rating object to query if user_id AND landmark_id is in the ratings table
    possible_rating = Rating.query.filter(Rating.user_id == user_id, Rating.landmark_id == landmark_id).first()
    
    # If this score does not yet exist, we will add to the session database.
    # If this score already exists, we will update the value of the existing score.
    if possible_rating:
        possible_rating.user_score = score
        db.session.commit()
        return "Your rating has been updated."
    else:
        # Instantiate new rating to add to the user database 
        new_rating = Rating(user_score=score, 
                            landmark_id=landmark_id, 
                            user_id=user_id)
        db.session.add(new_rating)
        db.session.commit()
        return "Rating saved."

        # FIXME return average score or reload page?


@app.route('/notes_landmark', methods=["POST"])
def add_notes_to_rating():
    """User saves notes to db when rating landmark from the landmark details page."""

    score = request.form.get("score")
    notes = request.form.get("notes")

    landmark_id = request.form.get("landmark_id")
    user_id = session['user_id']

    possible_notes = Rating.query.filter(Rating.user_id == user_id, Rating.landmark_id == landmark_id).first()    

    if possible_notes:
        possible_notes.user_notes_for_landmark = notes
        db.session.commit()
        return "Your review has been updated."
    else:
        new_notes = Rating(user_score=score,
                           user_notes_for_landmark=notes,
                           landmark_id=landmark_id,
                           user_id=user_id)

        db.session.add(new_notes)
        db.session.commit()
        return "Review saved."

@app.route('/add_image', methods=["POST"])
def add_image():
    """User uploads a new landmark image, and inserts into db."""

    imageURL = request.form.get("imageURL")
    landmark_id = request.form.get("landmark_id")

    new_image = LandmarkImage(landmark_id=landmark_id, 
                              imageurl=imageURL)

    db.session.add(new_image)
    db.session.commit()

    return "Success"

# ================================================================================
#  Database performance filters: highest rated, closest landmarks
# ================================================================================

# @app.route('/highest_rated.geojson')
def query_highest_rated_landmarks():
    """Limit db query searches and API calcs by this filter:  highly rated landmarks."""

    best_landmarks = []
    cutoff = 3.7  # best_landmarks are at least rated this score (inclusive)

    for landmark in Landmark.query.all():

        rating_scores = [r.user_score for r in landmark.ratings]
        if len(rating_scores) > 0:
            avg_rating = float(sum(rating_scores))/len(rating_scores)
            if avg_rating >= cutoff:
                best_landmarks.append(landmark)

        # use jsonify when returning an object / dict to JS turf.nearest  
        # typeerror cannot convert dict update sequence element - need to call by specific keys on JS

    # return jsonify(best_landmarks)

        # use list when returning a list to a python function
    return best_landmarks
        

def query_closest_destinations(coordinates): 
    """Helper function to query database calculating estimated distance between 2 points."""

    nearest = []

    best_landmarks = query_highest_rated_landmarks()

    for landmark in best_landmarks:
        subset_id = Landmark.query.filter(Landmark.landmark_id == landmark.landmark_id).first()
        landmark_coordinates = (landmark.landmark_lat, landmark.landmark_lng)
        
        if vincenty(coordinates, landmark_coordinates).miles < 0.25:
            nearest.append(landmark)

    return nearest


@app.route('/other_favorites', methods=["GET"])
def suggest_other_favorites():
    """User is viewing landmark details page, and app suggests another highly rated
    destination that is nearby."""

    landmark_id = request.args.get("landmark_id")
    landmark = Landmark.query.filter_by(landmark_id=landmark_id).first()
    coordinates = (landmark.landmark_lat, landmark.landmark_lng)
    
    suggestions = query_closest_destinations(coordinates)

    data = []

    for suggestion in suggestions:

        suggestion_view = {
                    'landmark_name': suggestion.landmark_name,
                    'landmark_id': suggestion.landmark_id,
                    'landmark_coordinates': (suggestion.landmark_lat, suggestion.landmark_lng),
                    'landmark_description': suggestion.landmark_description,
                    # http://stackoverflow.com/questions/394809/does-python-have-a-ternary-conditional-operator
                    'landmark_image': suggestion.images[0].imageurl if len(suggestion.images) > 0 else None
                    }

        if coordinates == suggestion_view['landmark_coordinates']:
            pass
        else:
            data.append(suggestion_view)
        # data.append(suggestion_view)
    # http://stackoverflow.com/questions/12435297/how-do-i-jsonify-a-list-in-flask
    return Response(json.dumps(data),  mimetype='application/json')
    
            
#     weight by number of user scores
#     sqlalchemy include dynamic calculation, pivot table in postgres? materialized table? k-dimensional tree
#         enumerate

# def calc_true_distance(origin, destination):
#     """Helper function to use Google Distance Matrix API to more accurately calculate walking distance between 2 points."""

#     url = 'https://maps.googleapis.com/maps/api/distancematrix/json?mode=walking&origins=%s&destinations=%s&key=%s' % (origin, destination, googleKey)
    
#     response = requests.get(url)
#     response = response.json()

#     distance = response['rows'][0]['elements'][0]['distance']['value']
#     # response in meters (0.5 miles = 805 meters)
#     return distance


# @app.route('/find_nearby')
# def find_nearby_destination_on_route():
#     """User has at least 1 selected destination, and is looking for a highly 
#     rated, nearby attraction to add to their trip."""
    
#     suggestions = []

#     # FIXME: use session['waypoints'] or polyline???
#     # FIXME: is there a better way to do this besides n*m nested for loops?
#     landmark = Landmark.query.filter(Landmark.ratings.user_score > 3).order_by(desc(Landmark.ratings.user_score)).all()

#     for item in session['waypoints']:
#         coordinates = (item['coordinates'][0], item['coordinates'][1])
#         for landmark in landmarks:
#             l_coord = (landmark.landmark_lat, landmark.landmark_lng)
#         if calc_true_distance(coordinates, l_coord) < 0.25:
#             suggestions.append(item)
#         
#         else:
#             return "No items match your criteria."

#     return suggestions

    # order_by highest rated landmarks, and return a list of up to 3 suggestions

# ================================================================================
#  Save and display walks
# ================================================================================

@app.route('/save_walk', methods=['POST'])
def save_walk():
    """User saves a constructed walk to the db."""

    user_id = session['user_id']

    origin_name = request.form.get('origin')
    origin = Landmark.query.filter(Landmark.landmark_name==origin_name).first()
    origin_id = origin.landmark_id

    destination_name = request.form.get('destination')
    destination = Landmark.query.filter(Landmark.landmark_name==destination_name).first()
    destination_id = destination.landmark_id

    log_datetime = date.today()
    duration = request.form.get("duration")
    distance = request.form.get("distance")

    # Instantiate new saved walk to add to the walks table
    new_saved = Walk(user_id=user_id, 
                     origin=origin_id,
                     destination=destination_id,
                     log_datetime=log_datetime,
                     duration=duration,
                     distance=distance
                    )
    db.session.add(new_saved)
    db.session.commit()
    return "Walk saved."

@app.route('/clear_a_saved', methods=['POST'])
def clear_saved():
    """Delete saved landmark from UserSaved table."""

    saved_id=request.form.get('saved_id')
    UserSaved.query.filter_by(saved_id=saved_id).delete()

    db.session.commit()

    return "Saved landmark deleted."


@app.route('/clear_walk', methods=['POST'])
def clear_walk():
    """Delete walk from saved walks table."""

    walk_id = request.form.get('walk_id')
    # import pdb; pdb.set_trace()
    Walk.query.filter_by(walk_id=walk_id).delete()

    db.session.commit()

    return "Walk deleted."


# ================================================================================
#  Jinja custom filters, custom debugger 
# ================================================================================

@app.template_filter('date')
def datetimeformat(value, format='%A, %b-%d-%Y'):
    """Custom Jinja filter to format date."""

    return value.strftime(format)

@app.template_filter('time')
def durationformat(value):
    """Custom Jinja filter to format duration."""
    
    result = '%.2f' % value
    return result

@app.template_filter('distance')
def distanceformat(value):
    """Custom Jinja filter to format distance."""
    
    result = '%.1f' % value
    return result


@app.route('/debugger')
def display_debug_message():
    """Display session and preserves dictionary format in bootbox alert."""

    return jsonify(session)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()
    # app.run(host='0.0.0.0')
