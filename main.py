#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, url_for, request, jsonify, Response
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api, Resource, reqparse
import os, json

base_dir = os.path.abspath(os.path.dirname(__name__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
       "mssql+pymssql://sa:NTDgun123@localhost:1433/model?charset=utf8"
#        "mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER?charset=utf8"
#        'sqlite:///%s' % os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager = Manager(app)
db = SQLAlchemy(app)
api = Api(app)
mirgrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

"""
粗糙试用版本，主要提供线上对接用api，顺便拿点数据，
试试部署方案，由于还有其他相关工作内容的整合，拖着点时间
"""

class Waixie(db.Model):
    __tablename__ = 'T_AfterService_Workflows'
    id = db.Column(db.Integer, primary_key=True)  
    serial_number = db.Column(db.String(14)) #单据编号
    type = db.Column(db.String(20)) #单据类型
    customer_guid = db.Column(db.String(20)) #客户
    creater_guid = db.Column(db.String(20))
    saler_name = db.Column(db.String(20))
    expired_status = db.Column(db.String(20))
    summited_at = db.Column(db.DateTime)
    material_number = db.Column(db.String(20))
    material_supplier_guid = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    workflow_status = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(20))

    def to_json(self):
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'type': self.type,
            'customer_guid': self.customer_guid,
            'material_number': self.material_number,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'saler_name': self.saler_name,
            'expired_status': self.expired_status,
            'summited_at': self.summited_at,
            'material_supplier_guid': self.material_supplier_guid,
            'status': self.status,
            'workflow_status': self.workflow_status
        }

class WorkflowJournal(db.Model):
    __tablename__ = 'T_Workflow_Journals'
    id = db.Column(db.Integer, primary_key=True)
    # Todo: find the way to mock the polymorphic
    workflow_id = db.Column(db.Integer, nullable=False)
    workflow_type = db.Column(db.String(20))
    source = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    trigger = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def to_json(self):
        return {
            'id': self.id,
            'workflow_type': "game",
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
                entity = Waixie(status=1,workflow_status=1, **data)
                db.session.add(entity)
                db.session.commit()
                return jsonify({"message": "ok", "data": entity.to_json()}), 200
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


class OrderAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("creater_guid", type=unicode, location="json")
        self.reqparser.add_argument("type", type=unicode, location="json")
        self.reqparser.add_argument("customer_guid", type=unicode, location="json")
        self.reqparser.add_argument("serial_number", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_guid", type=unicode, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        self.reqparser.add_argument("operation", type=unicode, location="json")
        super(OrderAPI, self).__init__()

    def get(self, id):
        entity = Waixie.query.get(id)
        if entity is None:
            return {"message": "no this order record", "status": 404}, 200
        else:
            return {"message": "ok", "data": entity.to_json(), "status": 0}, 200
    def put(self, id):
        args = self.reqparser.parse_args()
        flag = args["operation"]
        del args["operation"]
        Waixie.query.filter_by(id=id).update(args)
        db.session.commit()
        return {"message": "ok"}, 200
    
class OrderListAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("customer_guid", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_guid", type=unicode, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")

        super(OrderListAPI, self).__init__()

    def get(self):
        entities = Waixie.query.all()
        return {"message": "ok", "data": [e.to_json() for e in entities], "status": 0}, 200
    def post(self):
        args = self.reqparser.parse_args()
        entity = Waixie(status=1,workflow_status=1,**args)
        db.session.add(entity)
        db.session.commit()

        return {"message": "ok", "status": 0}, 200

class OrderJournalListAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        
        super(OrderJournalListAPI, self).__init__()

    def get(self):
        #params = request.args
        entities = WorkflowJournal.query.all()
        return {"message": "ok", "data":[e.to_json() for e in entities], "status":0}, 200


api.add_resource(OrderAPI, '/api/v1/afterservice/orders/<int:id>', endpoint='afterservice_order')
api.add_resource(OrderListAPI, '/api/v1/afterservice/orders', endpoint='afterservice_orders')
api.add_resource(OrderJournalListAPI, '/api/v1/afterservice/orders/journals', endpoint="afterservice_order_journals")

if __name__ == "__main__":
    manager.run()
    #app.run(host='0.0.0.0', debug=True, port=5050)
