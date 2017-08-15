#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests, json

def fake_waixie():
    required_field = {
        "type": "单据类型",
        "customer": "客户",
        "saler_name": "售后专员",
        "expired_status": "超时时效",
    }
    optional_field = {
        "material_number": "物料编号",
        "material_supplier": "原材料供应商"
    }
    after_filled = {
        "summited_at": "提交时间"
    }

    return required_field

def simple_test():
    resp = requests.post('http://localhost:5050/api/v1/waixies', json=fake_waixie())
    print resp

if __name__ == "__main__":
    simple_test()