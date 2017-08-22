#!/usr/bin/env python
# -*- coding:utf-8 -*-

from . import db

class Waixie(db.Model):
    __tablename__ = 'T_AfterService_Workflow'
    id = db.Column(db.Integer, primary_key=True)  
    serial_number = db.Column(db.String(14), unique=True) #单据编号
    type = db.Column(db.String(20)) #单据类型
    customer = db.Column(db.String(20)) #客户
    material_number = db.Column(db.String(20))
    saler_name = db.Column(db.String(20))
    expired_status = db.Column(db.String(20))
    summited_at = db.Column(db.DateTime)
    material_supplier = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False)
    workflow_status = db.Column(db.Integer, nullable=False)

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

class WorkflowJournal(db.Model):
    __tablename__ = 'T_Workflow_Journals'
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, nullable=False)
    workflow_type = db.Column(db.String(20))
    source = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.Integer, nullable=False)
    trigger = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'workflow': "name"
    }