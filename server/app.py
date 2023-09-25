#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

     def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return ({'message': 'Missing username or password'}), 422

        existing_user = User.query.filter(User.username==username).first()
        if existing_user:
            return ({'message': 'User already exists'}), 422

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return user.to_dict(), 201
        
class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return user.to_dict(), 200
        else:
            return {'error': '401 Unauthorized'}, 401
        

class Login(Resource):
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')

        user = User.query.filter(User.username == username).first()

        if user:
            if user.authenticate(password):

                session['user_id'] = user.id
                return user.to_dict(), 200

        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
     def delete(self):
        
        if session.get('user_id'):
            
            session['user_id'] = None
            
            return {}, 204
        
        return {'error': '401 Unauthorized'}, 401


# START OF LATEST
class RecipeIndex(Resource):
    def get(self):
        if not session['user_id']:
            return ({"error":"unauthorized"}, 401)
        else:
            user_id = session['user_id']
            recipes = [recipe.to_dict() for recipe in Recipe.query.filter(Recipe.user_id == user_id).all()]
            return recipes, 200
        
    def post(self):
        json = request.get_json()
        if not session.get('user_id'):
            return ({"error":"unauthorized"}, 401)
        else:
            try:
                new_recipe = Recipe(
                    title = json['title'],
                    instructions = json['instructions'],
                    minutes_to_complete = json['minutes_to_complete'],
                    user_id = session['user_id'],
                    )
            
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            except IntegrityError as e:
                db.session.rollback()
                return ({"error":"unprocessable entity"}, 422)
# END OF LATEST

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
