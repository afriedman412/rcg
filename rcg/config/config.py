import os
SPOTIFY_ID = os.environ['SPOTIFY_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
LAST_FM_ID = os.environ['LAST_FM_ID']
LAST_FM_SECRET = os.environ['LAST_FM_SECRET']
LAST_FM_USER = os.environ['LAST_FM_USER']
LAST_FM_PW = os.environ['LAST_FM_PW']
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

COLORS = {
    "Male": "#a1c3d1",
    "Female": "#f09933",
    "Non-Binary": "#816f88"
}

GENDERS = ['Male', 'Female', 'Non-Binary']