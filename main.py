from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import data
from datetime import datetime
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def get_response(data):
    return json.dumps(data), 200, {'Content Type': 'application/json; charset=utf-8'}

# Создае модель User(может быть как исполнителем так и заказчиком в зависимости от 'role')
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    
   
    def to_dict(self):
        """
        Функция, которая из объекта сделает словарь. 
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        """
        Функция, которая из объекта сделает словарь. 
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        """
        Функция, которая из объекта сделает словарь. 
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

# Создаем таблицы
with app.app_context():
    db.create_all()
    
    # Проходим циклом по 'users' в файле 'data'. И создаем новые колонки в таблице. 
    for user_data in data.users:
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()
    # Проходим циклом по 'orders' в файле 'data'. И создаем новые колонки в таблице.
    for order_data in data.orders:
        #Функция получает сторку и формат и выдает данные в фомате datetime.
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()

    for offer_data in data.offers:
        new_offer = Offer(**offer_data)
        db.session.add(new_offer)
        db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        res = [user.to_dict() for user in users]
        return get_response(res)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(**user_data)
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    user = User.query.get(uid)
    if request.method == 'GET':
        return get_response(user)
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.role = user_data['role']
        user.phone = user_data['phone']
        user.email = user_data['email']
        user.age = user_data['age']
        db.session.add(user)
        db.session.commit()
        return '', 204


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        res = []
        for order in orders:
            ord_dict = order.to_dict()
            ord_dict['start_date'] = str(ord_dict['start_date'])
            ord_dict['end_date'] = str(ord_dict['end_date'])
            res.append(ord_dict)

        return get_response(res)
    elif request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(**order_data)
        db.session.commit()
        return '', 201


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    order = Order.query.get(oid)
    if request.method == 'GET':
        ord_dict = order.to_dict()
        ord_dict['start_date'] = str(ord_dict['start_date'])
        ord_dict['end_date'] = str(ord_dict['end_date'])
        return get_response(order)
    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order.first_name = order_data['first_name']
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    offer = Offer.query.get(oid)
    if request.method == 'GET':
        return get_response(offer)
    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer.order_id = offer_data['order_id']
        # offer.customer_id = offer_data['customer_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        res = [offer.to_dict() for offer in offers]
        return get_response(res)
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(**offer_data)
        db.session.commit()
        return '', 201


if __name__ == "__main__":
    app.run()
