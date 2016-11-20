from flask import render_template, jsonify,request, abort
from . import main
from flask_login import login_required
from ..decorators import admin_required
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
collection = client.hackathon.post_arrival

@main.route('/rail/id/<id>')
def rail_detail(id):
    return render_template('main/detail.html', id=id, type="Rail")

@main.route('/truck/id/<id>')
def truck_detail(id):
    return render_template('main/detail.html', id=id, type="Truck")

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/user')
@login_required
def user():
    return render_template('index.html')

@main.route('/chassis')
@login_required
def chassis():
    return render_template('main/chassis.html')


@main.route('/labor')
@login_required
def labor():
    return render_template('main/labor.html')


@main.route('/rail')
@login_required
def rail():
    return render_template('main/rail.html')

def jsondata(size, condition, projection):
    cursor = collection.find(condition, projection).limit(size)
    data = {}
    list = []
    for entry in cursor:
        list.append(entry)
    data['data'] = list
    return jsonify(data)

def jsondata_for_railAnd_truck_inbound(condition):
    projection = {
        '_id': 0,
        'Container #': 1,
        'Container Size Type': 1,
        'Quantity': 1,
        'Expected Availability': 1,
        'Inland Point': 1,
        'Load Port': 1,
        'Unload Port': 1
    }
    return jsondata(15, condition, projection)

def jsondata_for_railAnd_truck_outbound(condition):
    projection = {
        '_id': 0,
        'Container #': 1,
        'Container Size Type': 1,
        'Quantity': 1,
        'Inland Point': 1,
        'Load Port': 1,
        'Unload Port': 1
    }
    return jsondata(15, condition, projection)

@main.route('/rail/inbound', methods=['GET'])
def rail_inbound():
    condition = {'Mode of Exit':'Rail'}
    return jsondata_for_railAnd_truck_inbound(condition)

@main.route('/rail/outbound', methods=['GET'])
def rail_outbound():
    condition = {'Mode of Entry':'Rail'}
    return jsondata_for_railAnd_truck_outbound(condition)

@main.route('/truck')
@login_required
def truck():
    return render_template('main/truck.html')

@main.route('/truck/inbound', methods=['GET'])
def truck_inbound():
    condition = {'Mode of Exit':'Truck'}
    return jsondata_for_railAnd_truck_inbound(condition)

@main.route('/truck/outbound', methods=['GET'])
def truck_outbound():
    condition = {'Mode of Entry':'Truck'}
    return jsondata_for_railAnd_truck_outbound(condition)


@main.route('/cargo')
@login_required
def cargo():
    return render_template('main/cargo.html')

@main.route('/cargo/detail')
def cargo_detail():
    return render_template('main/CargoDetail.html')


@main.route('/terminal')
@login_required
def terminal():
    return render_template('main/terminal.html')


@main.route('/shipline/inbound')
@login_required
def shipline():
    return render_template('main/shipline.html')

@main.route('/shipline/outbound')
@login_required
def shipline_outbound():
    return render_template('main/shipline_outbound.html')

@main.route('/shipline')
@login_required
def shipline_detail():
    return render_template('main/shipline_detail.html')

@main.route('/api/shipline', methods=['POST'])
def create_shipline():
    if request.json is None:
        abort(400)
    data = {
        'id': request.json['id'],
        'user': request.json['user'],
        'body': request.json['body']
    }
    print(type(data))
    json = jsonify(data)
    collection.insert(data)
    return json, 201

@main.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('main/administrator.html')
