"""Models and database functions for Walking project."""

from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Connection to the PostgreSQL database through the Flask-SQLAlchemy library.
# On this, we can find the `session` object, where we do most of our interactions.

db = SQLAlchemy()

##############################################################################
# Model definitions

class Landmark(db.Model):
    """Landmarks that will be rated by users."""

    __tablename__ = "landmarks"

    landmark_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    landmark_name = db.Column(db.String(100), nullable=True)
    landmark_description = db.Column(db.String(300), nullable=True)
    landmark_lat = db.Column(db.Float, nullable=False)
    landmark_lng = db.Column(db.Float, nullable=False)

    # FIXME upload pics of landmarks (user uploaded or google images?)
    # FIXME add yelp rooftop parks and online stairwells, or landmark_type
    
    # Applicable to CIVIC ART data set:
    landmark_artist = db.Column(db.String(100), nullable = True)
    landmark_display_dimensions = db.Column(db.String(100), nullable = True)
    landmark_location_description = db.Column(db.String(100), nullable = True)
    landmark_medium = db.Column(db.String(150), nullable = True)

    # general_walk_score = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<Landmark landmark_id=%s landmark_name=%s landmark_description=%s location=%s>" % (self.landmark_id, 
            self.landmark_name, self.landmark_description, self.location)


class User(db.Model):
    """User of walking website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(70), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    salt = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<User user_id=%s email=%s saved=%s>" % (self.user_id, self.email, self.saved)
           
    def __init__(self, email, password):
        """Instantiate a user object within the User class with salted passwords."""

        self.email = email
        self.salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), self.salt.encode('utf8'))

    def verify_password(self, password):
        """Verify user's password, a method that can be called on a user."""

        password_hash = bcrypt.hashpw(password.encode('utf8'), self.salt.encode('utf8'))

        if self.password_hash == password_hash:
            return True
        else:
            return False


class Rating(db.Model):
    """Ratings score of landmark given by users."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    landmark_id = db.Column(db.Integer, db.ForeignKey('landmarks.landmark_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user_score = db.Column(db.Integer, nullable=False)
    user_notes_for_landmark = db.Column(db.String(700), nullable=True)

    # Define relationship to user
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to landmark
    landmark = db.relationship("Landmark", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<Rating rating_id=%s landmark_id=%s user_id=%s user_score=%s user_notes_for_landmark=%s>" % (self.rating_id, 
            self.landmark_id, self.user_id, self.user_score, self.user_notes_for_landmark)


class Walk(db.Model):
    """Walks that will be created by users."""

    __tablename__ = "walks"

    # FIXME do I need a walks table?  or should i stick to landmarks?

    walk_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    origin_lat = db.Column(db.Float, nullable=False)
    origin_lng = db.Column(db.Float, nullable=False)
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lng = db.Column(db.Float, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)

    #Define relationship to user
    user = db.relationship("User", backref=db.backref("walks", order_by=walk_id))

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<Walk walk_id=%s user_id=%s origin_geocode=%s destination_geocode=%s start_datetime=%s end_datetime=%s>" % (self.walk_id, 
            self.user_id, self.origin_geocode, self.destination_geocode, self.start_datetime, self.end_datetime)


class WalkLandmarkLink(db.Model):
    """Association table connecting walks to landmarks with unique constraint."""

    __tablename__ = "walk_landmark_link"

    # add user_id? unique primary key? OR polyline list of waypoints?
    walk_id = db.Column(db.Integer, db.ForeignKey('walks.walk_id'), primary_key=True)
    landmark_id = db.Column(db.Integer, db.ForeignKey('landmarks.landmark_id'), primary_key=True)
    # UniqueConstraint('walk_id', 'landmark_id')

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<WalkLandmarkLink walk_id=%s landmark_id=%s>" % (self.walk_id, self.landmark_id)


class LandmarkImage(db.Model):
    """Landmark images uploaded by users or uploaded from static data set."""

    __tablename__ = "landmark_images"

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    landmark_id = db.Column(db.Integer, db.ForeignKey('landmarks.landmark_id'))
    landmark_coordinates = db.Column(db.String(50), nullable=True)
    imageurl = db.Column(db.String(255), nullable=False)

    # Define relationship to landmark
    landmark = db.relationship("Landmark", backref=db.backref('images'))

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<LandmarkImage image_id=%s landmark_id=%s imageurl=%s>" % (self.image_id, self.landmark_id, self.imageurl)


class UserSaved(db.Model):
    """Saved destinations as favorited by users."""

    __tablename__ = "user_saved"

    saved_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    landmark_id = db.Column(db.Integer, db.ForeignKey('landmarks.landmark_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # Define relationship to landmark
    landmark = db.relationship("Landmark", backref=db.backref('saved'))
    # Define relationship to user
    user = db.relationship("User", backref=db.backref('saved'))

    def __repr__(self):
        """Provide helpful representation when printed, for human readability."""

        return "<UserSaved saved_id=%s landmark_id=%s user_id=%s>" % (self.saved_id, self.landmark_id, self.user_id)

    def __init__(self, landmark_id, user_id):
        """Instantiate a user object within the User class with salted passwords."""

        self.landmark_id = landmark_id
        self.user_id = user_id
        self.saved = []


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///landmarks'
    db.app = app
    db.init_app(app)



if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

