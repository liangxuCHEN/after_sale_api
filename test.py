#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests, json, sys

def fake_waixie():
    required_field = {
        "type": "单据类型",
        "customer": "客户",
        "expired_status": "超时时效",
    }
    optional_field = {
        "material_number": "物料编号",
        "material_supplier": "原材料供应商"
    }
    after_filled = {
        "saler_name": "售后专员",
        "summited_at": "提交时间"
    }

    required_field.update(optional_field)

    return required_field

def simple_post_test():
    resp = requests.post('http://localhost:5050/api/v1/waixies', json=fake_waixie())
    print resp.json()

def simple_get_test():
    resp = requests.get('http://localhost:5050/api/v1/waixies')
    print resp.json()

def simple_put_test():
    data = fake_waixie()
    data['material_number'] = 'SH201707040001'
    resp = requests.post('http://localhost:5050/api/v1/waixies/1/update', json=data)
    print resp.json()

if __name__ == "__main__":
    try:
        method = sys.argv[1]
        globals()["_".join(["simple", method, "test"])]()

    #simple_post_test()
    except Exception as e:
        simple_get_test()