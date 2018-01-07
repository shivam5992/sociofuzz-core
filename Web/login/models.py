from myapp import db
from flask.ext.login import UserMixin

class User(UserMixin, db.Document):
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    fb_id = db.IntField()
    fb_token = db.StringField()