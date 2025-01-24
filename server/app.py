#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify  
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()

        response_dict = [restaurant.to_dict(only=('address', 'id', 'name')) for restaurant in restaurants]

        response = make_response(response_dict, 200)
        return response
    

api.add_resource(Restaurants, '/restaurants')

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()

        if restaurant:
            response_dict = restaurant.to_dict()
            response = make_response(response_dict, 200)
            return response
        response_dict = {
            "error": "Restaurant not found"  
        }
        response = make_response(response_dict, 404)
        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()

            response_dict = dict()
            response = make_response(response_dict, 204)
            return response
        
        response_dict = {
            "error": "Restaurant not found"  
        }
        response = make_response(response_dict, 404)
        return response
    
api.add_resource(RestaurantById, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()

        response_dict = [pizza.to_dict(only=('id', 'ingredients', 'name')) for pizza in pizzas]
        response = make_response(response_dict, 200)
        return response
    

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']
            price = data['price']

            new_restaurant_pizza = RestaurantPizza(
                restaurant_id = restaurant_id,
                pizza_id = pizza_id,
                price = price
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            response_dict = new_restaurant_pizza.to_dict()
            response = make_response(response_dict, 201)
            return response
        
        except ValueError:
            response_dict = {
                "errors" : ["validation errors"]
            }

            response = make_response(response_dict, 400)
            return response
        
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)