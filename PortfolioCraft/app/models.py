from flask_login import UserMixin
from datetime import datetime
from . import db 

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)
    links = db.Column(db.String(300), nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    
class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    resume_data = db.Column(db.Text, nullable=True)
    generated_html = db.Column(db.Text, nullable=True)
    theme = db.Column(db.String(50), nullable=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sections = db.relationship('CustomSection', backref='portfolio', lazy=True, cascade='all, delete-orphan')


class CustomSection(db.Model):
    __tablename__ = 'custom_sections'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    section_title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, default=0)
    