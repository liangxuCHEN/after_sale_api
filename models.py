#!/usr/bin/env python
# -*- coding:utf-8 -*-

from app import db

class Waixie(db.Model):
    __tablename__ = 'Waixies' 
    id = db.Column(db.Integer, primary_key=True)  
    serial_number = db.Column(db.String(14), unique=True)
    type = db.Column(db.String(20))
    customer = db.Column(db.String(20))
    material_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    saler_name = db.Column(db.String(20))
    expired_status = db.Column(db.String(20))
    summited_at = db.Column(da.DateTime)
    material_supplier = db.Column(db.String(20))
