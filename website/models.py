from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from website import db

class GPU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100))  # Decreased the length for PostgreSQL
    url = db.Column(db.String(1000))   # Decreased the length for PostgreSQL
    subscriptions = db.relationship('Subscriptions')
    price = db.relationship('Price', backref='gpu', lazy=True)

class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10, 2))  # Use Numeric for currency values in PostgreSQL
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())  # Use server_default
    gpu_id = db.Column(db.Integer, db.ForeignKey('gpu.id'))

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    subscriptions = db.relationship('Subscriptions', backref='users', lazy=True)

class Subscriptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    gpu_id = db.Column(db.Integer, db.ForeignKey('gpu.id'))
    desired_price = db.Column(db.Numeric(10, 2))  # Use Numeric for currency values in PostgreSQL
