#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, url_for, request, jsonify, Response
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
import os, json
base_dir = os.path.abspath(os.path.dirname(__name__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///%s' % os.path.join(base_dir, '../data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager = Manager(app)
db = SQLAlchemy(app)
mirgrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

"""
粗糙试用版本，主要提供线上对接用api，顺便拿点数据，
试试部署方案，由于还有其他相关工作内容的整合，拖着点时间
"""

class Waixie(db.Model):
    __tablename__ = 'Waixies' 
    id = db.Column(db.Integer, primary_key=True, nullable=False)  
    serial_number = db.Column(db.String(14), unique=True)
    type = db.Column(db.String(20))
    customer = db.Column(db.String(20))
    material_number = db.Column(db.String(20))
    saler_name = db.Column(db.String(20))
    expired_status = db.Column(db.String(20))
    material_supplier = db.Column(db.String(20))
    summited_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Waixie %(id)d>" % self

    def to_json(self):
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'type': self.type,
            'customer': self.customer,
            'material_number': self.material_number,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'saler_name': self.saler_name,
            'expired_status': self.expired_status,
            'summited_at': self.summited_at,
            'material_supplier': self.material_supplier
        }

@app.route('/')
def api_root():
    return 'Welcome, app for sale_service opened now!'

@app.route('/sales')
def api_sales():
    return "List of %s<total: %d>" % (url_for('api_sales'), len(Waixie.query.all()))

@app.route('/sales/<sale_id>')
def api_sale(sale_id):
    return "List of sale record#%s change" % sale_id

@app.route('/api/v1/waixies', methods = ["POST", "GET"])
def api_waixies():
    try:
        if request.headers['Content-Type'] == 'application/json':
            data = request.json
            if request.method == 'POST':
                entity = Waixie(**data)
                db.session.add(entity)
                db.session.commit()
                return jsonify({"message": "ok"}), 200
            else:
                raise Exception("HTTP meothd wrong")
        else:
            return jsonify({"message": "wrong data type"}), 400        
    except Exception as e:
        if request.method == 'GET':
            entities = Waixie.query.all()
            return jsonify(waixies = [e.to_json() for e in entities]), 200
        return jsonify({"message": e}), 400

@app.route('/api/v1/waixies/<int:field_id>/update', methods = ["POST"])
def api_waixies_update(field_id):
    try:
        if request.headers['Content-Type'] == 'application/json':
            data = request.json
            if request.method == 'POST':
                entity_id = field_id
                Waixie.query.filter_by(id=field_id).update(data)
                db.session.commit()
                return jsonify({"message": "ok"}), 200

            else:
                raise Exception("HTTP meothd wrong")
        else:
            return jsonify({"message": "wrong data type"}), 400
    except Exception as e:
        return jsonify({"message": e}), 400

if __name__ == "__main__":
    #manager.run()
    app.run(host='0.0.0.0', debug=True, port=5050)
