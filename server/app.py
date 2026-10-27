#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):

    def post(self):
        json = request.get_json() or {}
        username = json.get('username')
        password = json.get('password')

        if not username or not password:
            return {'error': 'Username and password are required'}, 422

        user = User(username=username)
        # The setter hashes the password before it is stored
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        # Log the new user in right away
        session['user_id'] = user.id

        return UserSchema().dump(user), 201

class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')
        user = db.session.get(User, user_id) if user_id else None

        if user:
            return UserSchema().dump(user), 200

        return {}, 204

class Login(Resource):

    def post(self):
        json = request.get_json() or {}
        username = json.get('username')
        password = json.get('password') or ''

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):

    def delete(self):
        session['user_id'] = None
        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
