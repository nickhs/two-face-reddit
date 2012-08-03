from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./crusade.db'
db = SQLAlchemy(app)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    instance_id = db.Column(db.String(10))

    created = db.Column(db.DateTime, default=datetime.datetime.now())
    modified = db.Column(db.DateTime, onupdate=datetime.datetime.now())

    def __init__(self, username, password, instance_id=None):
        self.username = username
        self.password = password
        self.instance_id = instance_id

    def __repr__(self):
        return "<%s>" % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(100), unique=True)
    
    created = db.Column(db.DateTime, default=datetime.datetime.now())
    modified = db.Column(db.DateTime, onupdate=datetime.datetime.now())

    commands = db.relationship('Command', backref='post')

    def __init__(self, post_id=None, title=None):
        self.post_id = post_id
        self.title = title


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15))
    status = db.Column(db.String(15))
    description = db.Column(db.String(100))

    created = db.Column(db.DateTime, default=datetime.datetime.now())
    modified = db.Column(db.DateTime, onupdate=datetime.datetime.now())

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


if __name__ == '__main__':
    app.run()

