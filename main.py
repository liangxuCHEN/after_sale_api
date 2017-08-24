#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, url_for, request, jsonify, Response
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api, Resource, reqparse
from workflows.AfterService import Workflow, WorkflowStatus, AfterServiceStatus
from transitions import MachineError
from datetime import datetime, date, timedelta
import os, json

base_dir = os.path.abspath(os.path.dirname(__name__))
app = Flask(__name__)
if os.environ["FLASK_ENV"] == "development":
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "mssql+pymssql://sa:NTDgun123@localhost:1433/model?charset=utf8"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER?charset=utf8"
#        "mssql+pymssql://sa:NTDgun123@localhost:1433/model?charset=utf8"
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
外协即是waixie
"""

# 还原表结构, 从思考到直接放弃
class Product(db.Model):
    __tablename__ = 'T_PRT_AllProduct'
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(None))
    skuCode = db.Column(db.String(None))
    itemCode = db.Column(db.String(None))

    def to_json(self):
        return {
            "id": self.id,
            "item_name": self.itemName,
            "sku_code": self.skuCode,
            "item_code": self.itemCode
        }

class Supplier(db.Model):
    __tablename__ = "T_PRT_SupplierBasicInfo"
    id = db.Column(db.Integer, primary_key=True)
    supplierName = db.Column(db.String(None))


class User(db.Model):
    __tablename__ = 'T_SYS_User'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(None))
    dptNames = db.Column(db.String(None))
    dptIds = db.Column(db.String(None))

    def to_json(self):
        return {
            "id": self.id,
            "user_name": self.userName,
            "dpt_names": self.dptNames,
            "dpt_ids": self.dptIds
        }

# 以下是新表 Todo: 处理一下db.String的问题
class AbnormalProduct(db.Model):
    __tablename__ = "T_PRT_AbnormalProduct"
    id = db.Column(db.Integer, primary_key=True)
    skuCode = db.Column(db.String(100))
    waixieid = db.Column(db.Integer, db.ForeignKey('T_AfterService_Workflows.id'))
    remark = db.Column(db.Text)

    def to_json(self):
        product_entity = Product.query.filter_by(skuCode = self.skuCode).first()
        return {
            "id": self.id,
            "skuCode": self.skuCode,
            "remark": self.remark,
            "product_itemName": product_entity.itemName
        }


class Waixie(db.Model):
    __tablename__ = 'T_AfterService_Workflows'
    id = db.Column(db.Integer, primary_key=True)  
    serial_number = db.Column(db.String(14)) #单据编号
    type = db.Column(db.String(100)) #单据类型
    expired_status = db.Column(db.String(100))
    summited_at = db.Column(db.DateTime)
    material_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    workflow_status = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.Text)
    
    material_supplier_id = db.Column(db.Integer) # 保留原有的表结构, 供应商表id
    customer_id = db.Column(db.Integer) #客户id， user表id
    creater_id = db.Column(db.Integer) #创建者id, user表id
    saler_id = db.Column(db.Integer)     #销售者id, user表id
    abnormal_products = db.relationship("AbnormalProduct", backref="T_PRT_AbnormalProduct", 
                                        lazy='dynamic')
    jouranls = db.relationship('WorkflowJournal', backref='T_AfterService_Workflows',
                                lazy='dynamic')

    def __init__(self, *args, **kwargs):
        today = date.today()
        datetime_today = datetime.strptime(str(today),'%Y-%m-%d') 
        count = len(Waixie.query.filter(
            Waixie.created_at >= datetime_today,
            Waixie.created_at <= datetime_today + timedelta(days=1)
        ).all()) + 1
        self.serial_number = "SH%s%s" %(datetime_today.strftime('%Y%m%d'), '{:0>4}'.format(count))
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        super(Waixie, self).__init__(*args, **kwargs)


    def to_json(self):
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'type': self.type,
            'customer_id': self.customer_id,
            'material_number': self.material_number,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%s") if self.created_at is not None else "",
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%s") if self.updated_at is not None else "",
            'saler_id': self.saler_id,
            'expired_status': self.expired_status,
            'summited_at': self.summited_at.strftime("%Y-%m-%d %H:%M:%s") if self.summited_at is not None else "",
            'material_supplier_id': self.material_supplier_id,
            'status': AfterServiceStatus(self.status).name,
            'workflow_status': WorkflowStatus(self.workflow_status).name,
            'abnormal_porducts': [e.to_json() for e in self.abnormal_products]
        }

class WorkflowJournal(db.Model):
    __tablename__ = 'T_Workflow_Journals'
    id = db.Column(db.Integer, primary_key=True)
    # Todo: find the way to mock the polymorphic
    workflow_id = db.Column(db.Integer, db.ForeignKey('T_AfterService_Workflows.id'))
    workflow_type = db.Column(db.String(100))
    source = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    trigger = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    operator_name = db.Column(db.String)

    def to_json(self):
        return {
            'id': self.id,
            'workflow_type': self.workflow_type,
            'source': self.source,
            'dest': self.destination,
            'trigger': self.trigger,
            'remark': self.remark,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%s") if self.created_at is not None else "",
        }

# 后面就是业务逻辑了
@app.route('/')
def api_root():
    return 'Welcome, app for sale_service opened now!'

@app.route('/sales')
def api_sales():
    return "List of %s<total: %d>" % (url_for('api_sales'), len(Waixie.query.all()))

@app.route('/sales/<sale_id>')
def api_sale(sale_id):
    return "List of sale record#%s change" % sale_id

@app.route('/test')
def api_test():
    return jsonify({"message": "ok", "data":[e.to_json() for e in User.query.all()]})

@app.route('/data/fack')
def api_post_user():
    datetime_str = datetime.now().strftime("%Y%m%d%H%M%s")
    user_entity = User(userName="mac%s" %datetime_str)
    product_entity = Product(skuCode="sku%s" %datetime_str, itemName="name%s" %datetime_str)
    supplier_entity = Supplier(supplierName="supplier%s" %datetime_str)

    db.session.add_all([user_entity, product_entity, supplier_entity])
    db.session.commit() 
    return "fack date add one"  


class OrderAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("type", type=unicode, location="json")
        self.reqparser.add_argument("customer_id", type=unicode, location="json")
        self.reqparser.add_argument("serial_number", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_name", type=unicode, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        self.reqparser.add_argument("operation", type=unicode, location="json")
        self.reqparser.add_argument("operator_name", type=unicode, location="json")

        super(OrderAPI, self).__init__()

    def get(self, id):
        entity = Waixie.query.get(id)
        if entity is None:
            return {"message": "no this order record", "status": 404}, 200
        else:
            return {"message": "ok", "data": entity.to_json(), "status": 0}, 200

    # 有待完善的逻辑重点
    def put(self, id):
        args = self._order_put_params()
        flag = args["operation"]
        del args["operation"]
        operator_name = args["operator_name"]
        del args["operator_name"]
        #Waixie.query.filter_by(id=id).update(args)
        entity = Waixie.query.get(id)
        if entity is None:
            return {"message": "no this order record", "status": 404}, 200
        else:
            flow = Workflow("temp", entity.status, entity.workflow_status)
            try:
                # 主流程控制，从制定到放弃
                if flow.workflow.state is not "in_progress":
                    return {"message": "invalid operaton, call developer for more", "status":500}  
                elif flag is not None:
                    source = flow.status_code()
                    flow.trigger(flag)
                    destination = flow.status_code()
                    jouranl = WorkflowJournal(source=source, destination=destination, workflow_id=entity.id, trigger=flag, operator_name=operator_name)
                    db.session.add(jouranl)
                    args["status"] = flow.status_code()
            except MachineError as e:
                flow.workflow.done()
                args["workflow_status"] = flow.workflow.status_code()
            Waixie.query.filter_by(id=id).update(args)
            db.session.commit()
        return {"message": "ok", "status": 0}, 200

    def delete(self, id):
        entity = Waixie.query.get(id)
        if entity is not None and entity.status == AfterServiceStatus["waitting"].value:
            db.session.delete(entity)
            db.session.commit()
            return {"message": "ok", "status": 0}, 200
        else:
            return {"message":"invalid operation", "status": 500}

    def _order_put_params(self):
        args = self.reqparser.parse_args()

        # 客户与供应商的关系未知
        # if args.customer_name is not None:
        #     args.customer_id = User.query.filter_by(userName=args.customer_name).first().id
        if args.material_supplier_name is not None:
            material_supplier = Supplier.query.filter_by(supplierName=args.material_supplier_name).first()
            if material_supplier is not None: args.material_supplier_id = material_supplier.id
            del args["material_supplier_name"]
        return args

class OrderListAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        #self.reqparser.add_argument("customer_name", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("creater_name", type=unicode, location="json")
        self.reqparser.add_argument("creater_id", type=int, location="json")
        self.reqparser.add_argument("material_supplier_name", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_id", type=int, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        # 列表改在request中处理
        #self.reqparser.add_argument("abnormal_products", type=list, location="json")

        self.reqparser_get = reqparse.RequestParser()
        self.reqparser_get.add_argument("status", type=unicode)
        self.reqparser_get.add_argument("workflow_status", type=unicode)
        self.reqparser_get.add_argument("creater_name", type=unicode)
        super(OrderListAPI, self).__init__()

    def get(self):
        args = self.reqparser_get.parse_args()
        if args.status is not None or args.creater_name is not None or args.workflow_status is not None:
            query = Waixie.query.join(User, Waixie.creater_id==User.id)
            if args.workflow_status is not None:
                query = query.filter(Waixie.workflow_status == WorkflowStatus[args.workflow_status].value)
            if args.status is not None:
                query = query.filter(Waixie.status == AfterServiceStatus[args.status].value)
            if args.creater_name is not None:
                query = query.filter(User.userName == args.creater_name) 
            entities = query.all()

        else:
            entities = Waixie.query.all()
        return {"message": "ok", "data": [e.to_json() for e in entities], "status": 0}, 200

    def post(self):
        args = self._order_post_params()
        
        entity = Waixie(**args)
        if request.json["abnormal_products"] is not None:
            abnormal_products = request.json["abnormal_products"]
            for product in abnormal_products:
                entity_product = AbnormalProduct(skuCode=product["skuCode"], remark=product["remark"])
                entity.abnormal_products.append(entity_product)

        db.session.add(entity)
        db.session.commit()
        return {"message": "ok", "data": entity.to_json(), "status": 0}, 200

    def _order_post_params(self):
        args = self.reqparser.parse_args()
        args.status = AfterServiceStatus["waitting"].value
        args.workflow_status = WorkflowStatus['in_progress'].value

        # 客户与供应商的关系未知
        # if args.customer_name is not None:
        #     args.customer_id = User.query.filter_by(userName=args.customer_name).first().id
        if args.creater_name is not None:
            creater = User.query.filter_by(userName=args.creater_name).first()
            if creater is not None: args.creater_id = creater.id
            del args["creater_name"]
        if args.material_supplier_name is not None:
            material_supplier = Supplier.query.filter_by(supplierName=args.material_supplier_name).first()
            if material_supplier is not None: args.material_supplier_id = material_supplier.id
            del args["material_supplier_name"]
        return args

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
    if os.environ["FLASK_ENV"] == "development":
        #manager.run()
        app.run(host='0.0.0.0', debug=True, port=5050)
    else:
        app.run(host='0.0.0.0', debug=True, port=5050)