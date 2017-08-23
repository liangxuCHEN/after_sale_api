#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests, json, sys

def fake_waixie():
    required_field = {
        "type": "order_type",
        "customer_guid": "ACGUNDAM",
        "creater_guid": "creater_guid",
    }
    optional_field = {
        "material_number": "物料编号",
        "material_supplier_guid": "原材料供应商"
    }
    after_filled = {
        "saler_name": "售后专员",
        "summited_at": "提交时间"
    }

    required_field.update(optional_field)

    return required_field

def simple_post_test():
    resp = requests.post('http://192.168.3.172:5050/api/v1/afterservice/orders', json=fake_waixie())
    #resp = requests.post('http://localhost:5050/api/v1/afterservice/orders', json=fake_waixie())
    print resp.json()

def simple_get_test():
    resp = requests.get('http://192.168.3.172:5050/api/v1/afterservice/orders')
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders')
    print resp.json()

def simple_put_test():
    data = fake_waixie()
    data['serial_number'] = 'SH201707040001'
    resp = requests.put('http://192.168.3.172:5050/api/v1/afterservice/orders/1', json=data)
    #resp = requests.put('http://localhost:5050/api/v1/afterservice/orders/1', json=data)
    print resp.json()

def simple_get_one_test():
    resp = requests.get('http://192.168.3.172:5050/api/v1/afterservice/orders/1')
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders/1')
    print resp.json()

def simple_get_journals_test():
    resp = requests.get('http://192.168.3.172:5050/api/v1/afterservice/orders/journals')
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders/journals')
    print resp.json()

if __name__ == "__main__":
    method = sys.argv[1]
    globals()["_".join(["simple", method, "test"])]()