# -*- coding: utf-8 -*-

from flask import render_template
from flask import Blueprint
from pymongo import MongoClient

main = Blueprint('controllers', __name__)

def db_init():
    client = MongoClient()
    db = client.ones
    collection = db.one
    return collection

coll = db_init()


@main.route('/')
def ones_view():
    ones = list(coll.find().sort('_id',-1).limit(6))
    return render_template('ones.html', ones=ones)


@main.route('/ones/<id>')
def previous_ones_view(id):
    i = coll.find_one({'titulo': id})
    id = coll.find_one({'titulo':id})['_id']
    c = coll.find({"_id": {"$gt": id}}).count()
    if c < 1:
        ones = list(coll.find({"_id": {"$lt": id}}).sort("_id", -1).limit(5))
        ones.insert(0,i)
    else:
        count = c - 6
        ones = list(coll.find({"_id": {"$gt": id}}).sort("_id", -1).skip(count).limit(6))
    return render_template('ones.html', ones=ones)

@main.route('/one/<id>')
def next_ones_view(id):
    id = coll.find_one({'titulo': id})['_id']
    ones = list(coll.find({"_id": {"$lt": id}}).sort("_id", -1).limit(6))
    return render_template('ones.html', ones=ones)


