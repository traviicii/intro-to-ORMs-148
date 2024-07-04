from flask import Flask, jsonify, request
# Flask class - gives us all the tools that we need to create a flask application (web application) by creating an instance of the Flask class
# jsonify - Converts data into JSON
# request - allows us to interact with HTTP method requests as objects
from flask_sqlalchemy import SQLAlchemy
# SQLAlchemy - ORM to connect and relate Python classes to database tables
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# DeclarativeBase - gives us the base model functionality to create the classes as models for our database tables, also tracks the meta data for our tables and classes
# Mapped - Maps a class attribute to a table column (or relationship)
# mapped_column - sets our columns and allows us to add any constraints we might need (unique, nullable, primary_key)
from flask_marshmallow import Marshmallow
# Marshmallow - allows us to create schema to validate, serialize, and deserialize JSON data
from datetime import date
# date - use this to create datetime objects
from typing import List
# List - is used to create a relationship the will return a list of objects
from marshmallow import ValidationError, fields
# fields - lets us set a schema field which includes data types and constraints
from sqlalchemy import select, delete
# select - acts as our SELECT FROM query 
# delete - act as our delete query

app = Flask(__name__) # creating an instance of the Flask class for our app to use

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ecom'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class= Base)
ma = Marshmallow(app)

class Customer(Base):
    __tablename__ = "customer" # make your class name the same as the tablename, and the table name should be exactly how it is in your database

    # Mapping our class attributes to our table columns
    id: Mapped[int] = mapped_column(primary_key= True)
    customer_name: Mapped[str] = mapped_column(db.String(75), nullable= False)
    email: Mapped[str] = mapped_column(db.String(150))
    phone: Mapped[str] = mapped_column(db.String(16))
    # address: Mapped[str] = mapped_column(db.String(150))

    # Create a one-many relationship to Orders table
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='customer') # back populates ensures that both ends of this relationship have access to this information

order_products = db.Table(
    "order_products",
    Base.metadata, # allow this table to locate the foreign keys from the Base class
    db.Column('order_id', db.ForeignKey('orders.id'), primary_key= True),
    db.Column('product_id', db.ForeignKey('products.id'), primary_key= True)
)

class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key= True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable= False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customer.id'))

    # create our many-one relationship to the customer table
    customer: Mapped['Customer'] = db.relationship(back_populates='orders')
    # create a many-many relationship to Products through our association table order_products
    products: Mapped[List['Products']] = db.relationship(secondary=order_products)

class Products(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key= True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable= False)
    price: Mapped[float] = mapped_column(db.Float, nullable= False)


with app.app_context():
    # db.drop_all() # drops (deletes) all tables in the database
    db.create_all() # First checks if a table exists already, and then creates the tables that it couldn't find, if it finds a table with the same name it doesn't reconstruct or modify it


#================= Marshmallow Data Validation Schema =========================#

# Define schema to validate customer data
class CustomerSchema(ma.Schema):
    id = fields.Integer(required= False)
    customer_name = fields.String(required= True)
    email = fields.String()
    phone = fields.String()

    class Meta:
        fields = ('id', 'customer_name', 'email', 'phone')

class OrderSchema(ma.Schema):
    id = fields.Integer(required= False)
    order_date = fields.Date(required= False)
    customer_id = fields.Integer(required= True)

    class Meta:
        fields = ('id', 'order_date', 'customer_id', 'items') # items will be a list of product id's associated with an order

class ProductSchema(ma.Schema):
    id = fields.Integer(required= False)
    product_name = fields.String(required= True)
    price = fields.Float(required= True)

    class Meta:
        fields = ('id', 'product_name', 'price')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many= True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many= True)

product_schema = ProductSchema()
products_schema = ProductSchema(many= True)


@app.route('/')
def home():
    return "Welcome to this wild ride on the Flask SQLAlchemy rollercoaster!"


#============ CRUD Operations =================#

# get all customer using a GET method
@app.route("/customers", methods= ['GET'])
def get_customers():
    query = select(Customer) # SELECT * FROM customer
    result = db.session.execute(query).scalars() # Execute our query, and convert each row object into a scalar object (python useable)
    customers = result.all() # packs all objects into a list

    return customers_schema.jsonify(customers)

# get a single customer, also with a GET method, dynamic route
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first() # .first() simply grabs the first object from the data returned from execute

    if result is None:
        return jsonify({'Error': "Customer not found!"}), 404
    
    return customer_schema.jsonify(result)


# create customers with a POST request
@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({e.messages}), 400

    new_customer = Customer(customer_name= customer_data['customer_name'], email= customer_data['email'], phone= customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"Message": "New customer added successfully!"}), 201

# Update a user with a PUT request
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):

    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalar()
    if result is None:
        return jsonify({"Error": "Customer not found"}), 404
    
    customer = result
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.commit()
    return jsonify({"Message": "Customer details have been updated!"})

# Delete a customer with a DELETE request
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    query = delete(Customer).where(Customer.id == id) # DELETE FROM customer WHERE id == id

    result = db.session.execute(query)

    if result.rowcount == 0:
        return jsonify({"Error": "Customer not found"})
    
    db.session.commit()
    return jsonify({"Message": "Customer successfully deleted! Wow!!"}), 200

#============ Product Interactions ===================#

# route to create/add new products with a POST request
@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Products(product_name= product_data['product_name'], price= product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"Message": "New product successfully added!"}), 201
    

#================ Order Interactions ====================#

# create/place a new order with a POST request
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Orders(order_date= date.today(), customer_id= order_data['customer_id'])

    for item_id in order_data['items']:
        query = select(Products).where(Products.id == item_id)
        item = db.session.execute(query).scalar()
        new_order.products.append(item)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({"Message": "New order placed!"}), 201

# Get items in an order by order id with GET
@app.route("/order_items/<int:id>", methods=['GET'])
def order_items(id):
    query = select(Orders).filter(Orders.id == id)
    order = db.session.execute(query).scalar()

    return products_schema.jsonify(order.products)


if __name__ == "__main__":
    app.run(debug= True)
