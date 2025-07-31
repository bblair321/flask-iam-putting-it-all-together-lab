# app.py
from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, User, Recipe

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        test_config.get('SQLALCHEMY_DATABASE_URI') if test_config else 'sqlite:///app.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = test_config.get('TESTING', False) if test_config else False

    db.init_app(app)
    Migrate(app, db)

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400

        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({"error": "Username already taken"}), 409

        new_user = User(
            username=data['username'],
            password=data['password'],
            image_url=data.get('image_url'),
            bio=data.get('bio')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
        if user:
            session['user_id'] = user.id
            return jsonify({"message": "Login successful"}), 200
        return jsonify({"error": "Invalid credentials"}), 401

    return app

app = create_app()
