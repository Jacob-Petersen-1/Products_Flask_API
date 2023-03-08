from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from marshmallow import post_load, fields, ValidationError
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float)
    inventory_quantity = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.title} - {self.price}'


# Schemas

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "description", "price", "inventory_quantity")

    @post_load
    def create_product(self, data, **kwargs):
        return Product(**data)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Resources


class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)

    def post(self):
        form_data = request.get_json()
        try:
            new_product = product_schema.load(form_data)
            db.session.add(new_product)
            db.session.commit()
        except ValidationError as err:
            return err.messages, 400
        return product_schema.dump(new_product), 201


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return product_schema.dump(product)

    def put(self, product_id):
        product = Product.query.get_or_404(product_id)

        if 'title' in request.json:
            product.title = request.json['title']
        if 'description' in request.json:
            product.description = request.json['description']
        if 'price' in request.json:
            product.price = request.json['price']
        if 'inventory_quantity' in request.json:
            product.inventory_quantity = request.json['inventory_quantity']

        db.session.commit()
        return product_schema.dump(product)

    def delete(self, product_id):
        post = Product.query.get_or_404(product_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204


# Routes
api.add_resource(ProductListResource, '/api/products')
api.add_resource(ProductResource, '/api/products/<int:product_id>')
