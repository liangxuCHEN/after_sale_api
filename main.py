#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Here be dragons
#1 the foreign key with no performance imporving in sqlserver, so you got me
#2 the production_database is tooooo fuck me up
#3 the mother fucker flask is not as friendly as rails treated
#4 why can they pay me off each day so i would fuck up right now
#5 is it talking can deal with the deadline problem
#6 why i come, come for what??
#7 the mother fucker is that you should treat 2 workflow like 1
from flask import Flask, url_for, request, jsonify, Response
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from workflows.AfterService import Workflow, WorkflowStatus, AfterServiceStatus
from transitions import MachineError
from datetime import datetime, date, timedelta
import os, json, pdb
from aenum import Enum



base_dir = os.path.abspath(os.path.dirname(__name__))
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


if os.environ["FLASK_ENV"] == "development":
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "mssql+pymssql://sa:NTDgun123@localhost:1433/model?charset=utf8"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        "mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER?charset=utf8"
    #    "mssql+pymssql://sa:NTDgun123@localhost:1433/model?charset=utf8"
    #    'sqlite:///%s' % os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = \
         "mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER?charset=utf8"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager = Manager(app)
db = SQLAlchemy(app)
mirgrate = Migrate(app, db)
api = Api(app)
manager.add_command('db', MigrateCommand)

"""
粗糙试用版本，主要提供线上对接用api，顺便拿点数据，
试试部署方案，由于还有其他相关工作内容的整合，拖着点时间
外协即是waixie，然后sqlalchemy这东西的查询优化会很作死
"""
# 责任报告的异常类别
ABNORMALPRODUCT = ["emergency", "normal", "ignored"]
AbnormalRank = Enum('workflow', ' '.join(ABNORMALPRODUCT))


# 还原表结构, 从思考到直接放弃
class Product(db.Model):
    __tablename__ = 'T_PRT_AllProduct'
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.Unicode(None))
    skuCode = db.Column(db.Unicode(None))
    itemCode = db.Column(db.Unicode(None))

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
    supplierName = db.Column(db.Unicode(None))
    IsLogisticSupplier = db.Column(db.Boolean)
    AfterSalerId = db.Column(db.Integer)

    def to_json(self):
        return {
            "supplierName": self.supplierName
        }


class User(db.Model):
    __tablename__ = 'T_SYS_User'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.Unicode(None))
    dptNames = db.Column(db.Unicode(None))
    dptIds = db.Column(db.Unicode(None))

    def to_json(self):
        return {
            "id": self.id,
            "user_name": self.userName,
            "dpt_names": self.dptNames,
            "dpt_ids": self.dptIds
        }

# 以下是新表 Todo: 处理一下db.String的问题
class Workflow_t(db.Model):
    __tablename__ = 'T_AS_Workflow'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(100))
    type = db.Column(db.Unicode(100))
    service_status = db.Column(db.Integer, nullable=False)
    workflow_status = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    __mapper_args__ = {
        'polymorphic_identity': 'workflow',
        'polymorphic_on': type
    }

    def __repr__(self):
        return "%(__class__.__name__)s(type=%(type)r, order_id=%(order_id)r, name=%(name)r,\
                 service_status=%(service_status)r, workflow_status=%(workflow_status)r)" % self

class AfterServiceWorkflow(Workflow_t):
    __tablename__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'AfterService_WaixieOrder'
    }

    # def __repr__(self):
    #     return "%(__class__.__name__)s(type=%(type)r, order_id=%(order_id)r, name=%(name)r,\
    #              service_status=%(service_status)r, workflow_status=%(workflow_status)r)" % self

class DeductionOrder(db.Model):
    __tablename__ = "T_AS_DeductionOrder"
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Unicode(100))
    supplier_name = db.Column(db.Unicode(100))
    supplier_id = db.Column(db.Integer)
    


class DutyReport(db.Model):
    __tablename__ = "T_AS_DutyReport"
    id = db.Column(db.Integer, primary_key=True)
    abnormal_type = db.Column(db.Integer)
    abnormal_reason = db.Column(db.UnicodeText)
    publishment = db.Column(db.UnicodeText)
    publish_to = db.Column(db.Unicode(50))
    compensation = db.Column(db.Integer)
    duty_to_id = db.Column(db.Integer)
    duty_to = db.Column(db.Unicode(100))
    # 缺了个责任判定日期
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    order_id = db.Column(db.Integer)

    def to_json(self):
        
        return {
            "id": self.id,
            "abnormal_type": self.abnormal_type,
            "abnormal_reason": self.abnormal_reason,
            "publishment": self.publishment,
            "publish_to": self.publish_to,
            "compensation": self.compensation,
            "duty_to_id": self.duty_to_id,
            "duty_to": self.duty_to
        }
        

class AbnormalProduct(db.Model):
    __tablename__ = "T_AS_AbnormalProduct"
    id = db.Column(db.Integer, primary_key=True)
    skuCode = db.Column(db.Unicode(100)) #对应的外键
    product_id = db.Column(db.Integer) 
    waixieOrder_id = db.Column(db.Integer)    #
    remark = db.Column(db.UnicodeText)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # WaixieOrder = db.relationship("WaixieOrder",
    #         primaryjoin="db.remote()"
    #     )

    def to_json(self):
        product_entity = Product.query.filter_by(skuCode = self.skuCode).first()
        return {
            "id": self.id,
            "skuCode": self.skuCode,
            "remark": self.remark,
            "product_itemName": product_entity.itemName if product_entity is not None else "",
            "waixieOrder_id": self.waixieOrder_id
        }

class WaixieOrder(db.Model):
    __tablename__ = 'T_AS_WaixieOrder'
    id = db.Column(db.Integer, primary_key=True)  
    serial_number = db.Column(db.Unicode(14)) #单据编号
    type = db.Column(db.Unicode(100)) #单据类型
    expired_status = db.Column(db.Unicode(100)) #过期状态
    summited_at = db.Column(db.DateTime)    #提交时间
    material_number = db.Column(db.Unicode(100))    #物料编号
    status = db.Column(db.Integer, nullable=False)  #审批状态
    workflow_status = db.Column(db.Integer, nullable=False) #流程状态
    remark = db.Column(db.UnicodeText)  #异常描述
    
    material_supplier_id = db.Column(db.Integer) # 保留原有的表结构, 供应商表id
    material_supplier_name = db.Column(db.Unicode(100))
    customer_id = db.Column(db.Integer) #客户id， user表id
    customer_name = db.Column(db.Unicode(100))
    creater_id = db.Column(db.Integer) #创建者id, user表id
    creater_name = db.Column(db.Unicode(100))
    saler_id = db.Column(db.Integer)     #销售者id, user表id
    saler_name = db.Column(db.Unicode(100))
    reason = db.Column(db.Unicode(20)) #原因
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()) 
    # abnormal_products = db.relationship("AbnormalProduct", backref="T_PRT_AbnormalProduct", 
    #                                     lazy='dynamic')
    # jouranls = db.relationship('WorkflowJournal', backref='T_AfterService_Workflows',
    #                             lazy='dynamic')
    # workflow = db.relationship(Workflow,
    #                 primaryjoin=db.remote(Workflow.order_id) == \
    #                     db.foreign(id)
    #             )


    def __init__(self, *args, **kwargs):
        today = date.today()
        datetime_today = datetime.strptime(str(today),'%Y-%m-%d') 
        count = len(WaixieOrder.query.filter(
            WaixieOrder.created_at >= datetime_today,
            WaixieOrder.created_at <= datetime_today + timedelta(days=1)
        ).all()) + 1
        self.serial_number = "SH%s%s" %(datetime_today.strftime('%Y%m%d'), '{:0>4}'.format(count))
        super(WaixieOrder, self).__init__(*args, **kwargs)


    def to_json(self):
        self.abnormal_products = AbnormalProduct.query.filter_by(waixieOrder_id = self.id)
        self.duty_report = DutyReport.query.filter_by(order_id = self.id).all()
        self.customer = Supplier.query.filter_by(id=self.customer_id).first() or Supplier.query.filter_by(supplierName=self.customer_name).first()
        
        self.material_supplier = Supplier.query.filter_by(id=self.material_supplier_id).first() or Supplier.query.filter_by(supplierName=self.material_supplier_id).first()
        self.creater = User.query.filter_by(id=self.creater_id).first() or User.query.filter_by(userName=self.creater_name).first()
        if self.material_supplier:
            self.saler = User.query.filter_by(id=self.saler_id if self.saler_id else self.material_supplier.AfterSalerId).first()
        else:
            self.saler = None
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'type': self.type,
            'customer_name': self.customer.supplierName if self.customer is not None else "",
            'material_supplier_name': self.material_supplier.supplierName if self.material_supplier is not None else "",
            'creater_name': self.creater.userName if self.creater is not None else "",
            'material_number': self.material_number,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at is not None else "",
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at is not None else "",
            'expired_status': self.expired_status,
            'summited_at': self.summited_at.strftime("%Y-%m-%d %H:%M:%S") if self.summited_at is not None else "",
            'status': AfterServiceStatus(self.status).name,
            'workflow_status': WorkflowStatus(self.workflow_status).name,
            'abnormal_porducts': [e.to_json() for e in self.abnormal_products],
            'duty_report': [e.to_json() for e in self.duty_report],
            'remark': self.remark,
            'saler': self.saler.userName if self.saler else "",
            "reason": self.reason
        }

class WorkflowJournal(db.Model):
    __tablename__ = 'T_AS_Workflow_Journals'
    id = db.Column(db.Integer, primary_key=True)
    # Todo: find the way to mock the polymorphic
    workflow_id = db.Column(db.Integer)
    workflow_type = db.Column(db.String(100))
    source = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    trigger = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
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
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at is not None else "",
        }

##################
# 后面就是业务逻辑了
@app.route('/')
def api_root():
    return 'Welcome, app for sale_service opened now!'

@app.route('/sales')
def api_sales():
    return "List of %s<total: %d>" % (url_for('api_sales'), len(WaixieOrder.query.all()))

@app.route('/sales/<sale_id>')
def api_sale(sale_id):
    return "List of sale record#%s change" % sale_id

@app.route('/test')
def api_test():
    return jsonify({"message": "ok", "data":[e.to_json() for e in User.query.all()]})

@app.route('/data/fack')
def api_post_user():
    datetime_str = datetime.now().strftime("%Y%m%d%H%M")
    user_entity = User(userName=u"小白")
    product_entity = Product(skuCode="sku%s" %datetime_str, itemName="TheWorld")
    supplier_entity = Supplier(supplierName=u"供应一组")

    db.session.add_all([user_entity, product_entity, supplier_entity])
    db.session.commit() 
    return "fack date add one"  

@app.route('/api/v1/afterservice/supplier_user_matcher')
def api_supplier_user_matcher():
    query = db.session.query(Supplier, User).outerjoin(User, User.id == Supplier.AfterSalerId)
    if "key_word" in request.args:
        key_word = request.args["key_word"]
        query_list = [
                        getattr(Supplier, "supplierName").like(u"%{}%".format(key_word)),
                        getattr(User, "userName").like(u"%{}%".format(key_word)),
                    ]
        query = query.filter(db.or_(*query_list))
    
    if "page" in request.args and "per_page" in request.args:
        page = int(request.args["page"])
        per_page = int(request.args["per_page"])
        entity_pairs = query.paginate(page, per_page).items
    else:
        entity_pairs = query.all()

    res = [
            {
                "supplier_name": entity_supplier.supplierName if entity_supplier is not None else "",
                "afterservice_salername": entity_user.userName if entity_user is not None else ""
            } for (entity_supplier, entity_user) in entity_pairs
        ] 
    return jsonify({"data":res, "message":"ok", "status":0}), 200

class OrderAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("type", type=unicode, location="json")
        #self.reqparser.add_argument("customer_id", type=unicode, location="json")
        #self.reqparser.add_argument("serial_number", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_name", type=unicode, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        self.reqparser.add_argument("operation", type=unicode, location="json")
        self.reqparser.add_argument("operator_name", type=unicode, location="json")
        self.reqparser.add_argument("abnormal_products", type=list, location="json")
        self.reqparser.add_argument("duty_report", type=dict, location="json")

        super(OrderAPI, self).__init__()

    def get(self, id):
        entity = WaixieOrder.query.get(id)
        if entity is None:
            return {"message": "no this order record", "status": 404}, 200
        else:
            return {"message": "ok", "data": entity.to_json(), "status": 0}, 200

    # 有待完善的逻辑重点
    def put(self, id):
        args = self._order_put_params()
        # 使用了reqparser后可以防止过度防御
        flag = args["operation"]
        del args["operation"]
        operator_name = args["operator_name"]
        del args["operator_name"]
        remark = args["remark"] if args["remark"] else ""
        del args["remark"]

        #WaixieOrder.query.filter_by(id=id).update(args)
        entity = WaixieOrder.query.get(id)
        if entity is None:
            return {"message": "no this order record", "status": 404}, 200
        else:
            flow = Workflow("temp", entity.status, entity.workflow_status)
            try:
                # 莫名其妙的更新改动
                if args.abnormal_products is not None:
                    abnormal_products = request.json["abnormal_products"]
                    for product in abnormal_products:
                        entity_product = AbnormalProduct(skuCode=product["skuCode"], remark=product["remark"], waixieOrder_id=entity.id)
                        db.session.add(entity_product)
                del args["abnormal_products"]
                
                if args.duty_report is not None:
                    duty_reports = request.json["duty_report"] if type(request.json["duty_report"]) is list else [request.json["duty_report"]] 
                    for report in duty_reports:
                        report["order_id"] = entity.id
                        entity_report = DutyReport(**report)
                        db.session.add(entity_report)
                del args["duty_report"]

                # 主流程控制，从制定到放弃
                if flow.workflow.state is not "in_progress":
                    return {"message": "invalid operaton, call developer for more", "status": 500}
                elif flag is not None:
                    source = flow.status_code()
                    flow.trigger(flag)
                    if flow.state == "service_approving":
                        args["summited_at"] = datetime.now()
                    destination = flow.status_code()
                    journal = WorkflowJournal(source=source, destination=destination, workflow_id=entity.id, trigger=flag, operator_name=operator_name, remark=remark)
                    
                    db.session.add(journal)
                    args["status"] = flow.status_code()
                    if flow.state == "end":
                        flow.workflow.done()
                        args["workflow_status"] = flow.workflow.status_code()
            except MachineError as e:
                return {"message": "invalid operation", "status":0, "data":{}}
            WaixieOrder.query.filter_by(id=id).update(args)
            db.session.commit()
            entity = WaixieOrder.query.get(id)
        return {"message": "ok", "status": 0, "data":entity.to_json()}, 200

    def delete(self, id):
        entity = WaixieOrder.query.get(id)
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
        res = {}
        for key, item in args.items():
            if item: res[key] = item
        return res

class WaixieAbnormalProductApi(Resource):
    def __init__(self):
        self.reqparser_put = reqparse.RequestParser()
        self.reqparser_put.add_argument("skuCode", type=unicode, location="json")
        self.reqparser_put.add_argument("remark", type=unicode, location="json")
        super(WaixieAbnormalProductApi, self).__init__()

    def put(self, waixie_id, product_id):
        args = self.reqparser_put.parse_args()
        AbnormalProduct.query.filter_by(id=product_id).update(args)
        db.session.commit()
        return {"message": "ok", "data":{}, "status":0}        

    def get(self, waixie_id, product_id):
        entity = AbnormalProduct.query.get(product_id)
        return {"message": "ok", "data":entity.to_json(), "status":0}

    def delete(self, waixie_id, product_id):
        entity = AbnormalProduct.query.get(product_id)
        db.session.delete(entity)
        db.session.commit()
        return {"message": "ok", "data":{}, "status": 0}

class WaixieAbnormalProductListApi(Resource):
    def __init__(self):
        #考虑到批处理的问题，不用参数解析器了，话说这回连strong parameter都做不到，不适合长期使用
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("skuCode", type=unicode, location="json")
        self.reqparser.add_argument("product_id", type=int, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        self.reqparser.add_argument("product_list", type=list, location="json")
        super(WaixieAbnormalProductListApi, self).__init__()

    def get(self, waixie_id):
        entities = AbnormalProduct.query.filter_by(waixieOrder_id=waixie_id).all()
        return {"message": "ok", "data":[entity.to_json() for entity in entities]}

    def post(self, waixie_id):
        if "product_list" in request.json:
            res = []
            for data in request.json["product_list"]:
                entity_data = {"waixieOrder_id": waixie_id}
                entity_data.update(self._parser_post_param(data))
                res.append(AbnormalProduct(**self._parser_post_param(entity_data)))
            db.session.add_all(res)
            db.session.commit()
        else:
            args = self.reqparser.parse_args()
            args["waixieOrder_id"] = waixie_id
            res = AbnormalProduct(**args)
            db.session.add(res)
            db.session.commit()
            res = [res]
        return {"message": "ok", "data": [entity.to_json() for entity in res], "status":0}

    def _parser_post_param(self, data):
        res = {}
        if "skuCode" in data:
            res["skuCode"] = data["skuCode"]
            product_entity = Product.query.filter_by(skuCode = data["skuCode"]).first()
            if product_entity is not None: res["product_id"] = product_entity.id
        if "product_id" in data:
            res["product_id"] = data["product_id"]
        if "remark" in data:
            res["remark"] = data["remark"]
        if "waixieOrder_id" in data:
            res["waixieOrder_id"] = data["waixieOrder_id"]
        return res

class OrderListAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("customer_name", type=unicode, location="json")
        self.reqparser.add_argument("material_number", type=unicode, location="json")
        self.reqparser.add_argument("creater_name", type=unicode, location="json")
        self.reqparser.add_argument("creater_id", type=int, location="json")
        self.reqparser.add_argument("material_supplier_name", type=unicode, location="json")
        self.reqparser.add_argument("material_supplier_id", type=int, location="json")
        self.reqparser.add_argument("remark", type=unicode, location="json")
        self.reqparser.add_argument("type", type=unicode, location="json")
        self.reqparser.add_argument("reason", type=unicode, location="json")
        # post 必须参数
        self.reqparser_post_required = reqparse.RequestParser()
        self.reqparser_post_required.add_argument("customer_name", type=unicode, location="json")
        self.reqparser_post_required.add_argument("remark", type=unicode, location="json")
        self.reqparser_post_required.add_argument("reason", type=unicode, location="json")
        # post 可选参数
        self.reqparser_post_optional = reqparse.RequestParser()
        self.reqparser_post_optional.add_argument("creater_name", type=unicode, location="json")
        self.reqparser_post_optional.add_argument("material_number", type=unicode, location="json")
        self.reqparser_post_optional.add_argument("creater_id", type=int, location="json")
        self.reqparser_post_optional.add_argument("material_supplier_id", type=int, location="json")
        self.reqparser_post_optional.add_argument("material_supplier_name", type=unicode, location="json")
        # 销售负责人不用传递
        #self.reqparser_post_optional.add_argument("saler_name", type=unicode, location="json")
        #self.reqparser_post_required.add_argument("saler_id", type=unicode, location="json")
        

        self.reqparser_get = reqparse.RequestParser()
        self.reqparser_get.add_argument("status", type=unicode)
        self.reqparser_get.add_argument("workflow_status", type=unicode)
        self.reqparser_get.add_argument("creater_name", type=unicode)
        self.reqparser_get.add_argument("page", type=int)
        self.reqparser_get.add_argument("per_page", type=int)
        super(OrderListAPI, self).__init__()

    def get(self):
        
        args = self.reqparser_get.parse_args()
        if args.status is not None or args.creater_name is not None or args.workflow_status is not None:
            query = WaixieOrder.query.join(User, WaixieOrder.creater_id==User.id)
            if args.workflow_status is not None:
                query = query.filter(WaixieOrder.workflow_status == WorkflowStatus[args.workflow_status].value)
            if args.status is not None:
                query = query.filter(WaixieOrder.status == AfterServiceStatus[args.status].value)
            if args.creater_name is not None:
                query = query.filter(User.userName == args.creater_name) 
        else:
            query = WaixieOrder.query
        
        if args.page and args.per_page:
            entities = query.paginate(args.page, args.per_page).items
        else:
            entities = query.all()

        return {"message": "ok", "data": [e.to_json() for e in entities], "status": 0}, 200

    def post(self):
        args = self._order_post_params()
        required = self.reqparser_post_required.parse_args()
        for value in required.values():
            if value is None: raise Exception("nothing")

        entity = WaixieOrder(**args)
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
            #del args["creater_name"]
        if args.material_supplier_name is not None:
            material_supplier = Supplier.query.filter_by(supplierName=args.material_supplier_name).first()
            if material_supplier is not None: args.material_supplier_id = material_supplier.id
            #del args["material_supplier_name"]
        if args.customer_name is not None:
            customer = Supplier.query.filter_by(supplierName=args.customer_name).first()
            if customer is not None: args.customer_id = customer.id
        return args

class OrderJournalListAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        super(OrderJournalListAPI, self).__init__()
        
    def get(self):
        #params = request.args
        entities = WorkflowJournal.query.all()
        return {"message": "ok", "data":[e.to_json() for e in entities], "status":0}, 200

class DutyReportAPI(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        
        super(DutyReportAPI, self).__init__()
    
    def get(self):
        return {"message": "ok", "data":ABNORMALPRODUCT, "status":0}


api.add_resource(OrderAPI, '/api/v1/afterservice/orders/<int:id>', endpoint='afterservice.order')
api.add_resource(OrderListAPI, '/api/v1/afterservice/orders', endpoint='afterservice.orders')
api.add_resource(OrderJournalListAPI, '/api/v1/afterservice/orders/journals', endpoint="afterservice.order.journals")
api.add_resource(DutyReportAPI, '/api/v1/afterservice/dutyreports/abnormalrank', endpoint="dutyreport.abnormalrank")
api.add_resource(WaixieAbnormalProductListApi, '/api/v1/afterservice/orders/<int:waixie_id>/abnormal-products', endpoint='afterservice.order.abnormal-products')
api.add_resource(WaixieAbnormalProductApi, '/api/v1/afterservice/orders/<int:waixie_id>/abnormal-products/<int:product_id>', endpoint='afterservice.order.abnormal-product')


if __name__ == "__main__":
    if os.environ["FLASK_ENV"] == "development":
        #manager.run()
        app.run(host='0.0.0.0', debug=True, port=5050)
    else:
        app.run(host='0.0.0.0', debug=True, port=5050)