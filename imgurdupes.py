"""Utility file to remove null-type images from Imgur image urls in db."""

from sqlalchemy import func
from model import Landmark, User, Rating, Walk, WalkLandmarkLink, LandmarkImage, UserSaved

from model import connect_to_db, db
from server import app
import json
import requests


def remove_no_image():
    """Remove Imgur imageurls where Google Street View API has returned null-type images."""

    print "removing no-image images"

    with open('joyce-imgur-hashes') as hashes:
      for h in hashes:
        h = h.strip()
        LandmarkImage.query.filter(LandmarkImage.imageurl.like('%' + h + '%')).delete(synchronize_session='fetch') 
        # http://stackoverflow.com/questions/7892618/sqlalchemy-delete-subquery
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    remove_no_image()