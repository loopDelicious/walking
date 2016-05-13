"""Walk creator."""

import sqlalchemy
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import Landmark, User, Rating, Walk, WalkLandmarkLink, connect_to_db, db
import os
import urllib2
import geocoder


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ["FLASK_SECRET_KEY"]


# Raise an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/registration', methods=["GET"])
def display_registration_form():
    """Displays form for users to register an account."""

    return render_template('registration.html')


@app.route('/registration', methods=["POST"])
def process_registration_form():
    """Processes registration when user provides email and password."""

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

@app.route('/login', methods=["GET"])
def display_login_form():
    """Displays form fo
    r users to login"""

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def process_login():
    """Process login from User, redirect to homepage"""

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


@app.route('/logout')
def logout():
    """Removes user_id from the session"""

    session.pop('user_id', None)
    flash("Logged out.")

    return redirect('/')



@app.route('/map')
def display_map():
    """Display the initial map"""

    return render_template('mapbox.html')


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




@app.route('/geocode')
def geocode_address_to_coordinates():
    """User inputs address.  Convert to geojson lng_lat coordinates
    via server-side Google Geocoding API request."""

    address = request.args.get("address")
    url="https://maps.googleapis.com/maps/api/geocode/json?address=%s" % address
    response = urllib2.urlopen(url)
    address_json = response.read()

    if address_json["status"] == "OK":
        coordinates = address_json["geometry"]["location"]
        address_data = {
            "status": "OK",
            "coordinates": coordinates}
    else:
        flash("Location not found.")
        address_data = {"status": "location not found"}

    return jsonify(address_data)

# @app.route('/set_origin', methods=['GET'])
# def set_origin():
#     """Add origin as first waypoint in the session."""

#     origin = request.args.get("origin")


#     // when user press enter after typed in address, start findAddress process
#     $('#type-address').keypress(function(e) {
#       if(e.which == 13) {
#         var address = $(this).val();
#         console.log(address);
#         $('#wait').css("display", "block");
#         $.get('/geocode_address', {'address': address}, findAddress);
#         console.log("Finished toAddress");

#       }
#     });


@app.route('/add_waypoint', methods=['GET'])
def add_waypoint():
    """Add a new waypoint to the session."""

    waypoint = request.args.get("landmark_id")

    if "waypoints" in session:
        # mapbox.Directions limits routes to 25 places of interest
        if len(session['waypoints']) < 25:
            if waypoint in session['waypoints']:
                return "Already added."
            else: 
                session['waypoints'].append(waypoint)
                return "Added."
        else:
            return "Only 25 places can be included in a trip."
    else:
        session['waypoints'] = [waypoint]
        return "Added."
    print session['waypoints']


# @app.route('/route_directions')
# def get_directions_geojson():
#     """Get directions via Mapbox Directions API with all the waypoints in the session."""

#     waypoints_list = session['waypoints']
#     coordinates = []

#     for waypoint in waypoints_list:
#         landmark = Landmark.query.filter_by(landmark_id=waypoint).one()
#         lng = landmark.landmark_lng 
#         lat = landmark.landmark_lat
#         pair = lng + ', ' + lat + '; '
#         coordinates.append(pair)

#     url = "https://api.mapbox.com/directions/v5/mapbox.walking/" + coordinates

#     response = requests.get(url)
#     response = response.json()
#     route = response['routes'][0]

#     return jsonify(route)


# @app.route('/clear')
# def clear_waypoints():
#     """Clear waypoints from session."""

#     session['waypoints'] = []

#     return "Route is cleared."


# https://github.com/terriwong/weekend-wanderlust/blob/master/server.py
# dan:  add waypoint in sequential order and update travel time per added waypoint
    

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


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
