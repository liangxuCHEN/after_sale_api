#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests, json, sys

def fake_waixie():
    required_field = {
        "type": "order_type",
        "customer_name": "成都市金虎家俱有限公司",
    }
    optional_field = {
        "material_number": "sku2017082411541503546850",
        "material_supplier_name": "成都市金虎家俱有限公司",
        "creater_name": "陈俊文",
        "abnormal_products": [{"skuCode":"LS19ZH0303003", "remark":"fuckme"}, {"skuCode":"LS19ZH0320009", "remark":"fuck2me"}],
        "duty_report": {"abnormal_type": 12}
    }
    after_filled = {
        "saler_name": u"陈俊文"
    }

    required_field.update(optional_field)
    required_field.update(after_filled)

    return required_field

def simple_post_test():
    resp = requests.post('http://192.168.3.172:5050/api/v1/afterservice/orders', json=fake_waixie())
    #resp = requests.post('http://localhost:5050/api/v1/afterservice/orders', json=fake_waixie())
    print resp.json()

def simple_get_test(*params):
    if len(params) >= 1:
        resp = requests.get('http://localhost:5050/api/v1/afterservice/orders?%s' % "&".join(params))
    else:
        resp = requests.get('http://localhost:5050/api/v1/afterservice/orders')
        
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders')
    print resp.json()

def simple_put_test():
    data = fake_waixie()
    data['serial_number'] = 'SH201707040001'
    data['operation'] = 'done'
    data['operator_name'] = 'christmas father'
    resp = requests.put('http://192.168.3.172:5050/api/v1/afterservice/orders/1', json=data)
    #resp = requests.put('http://localhost:5050/api/v1/afterservice/orders/10', json=data)

    print resp.json()
def simple_get_one_test():
    #resp = requests.get('http://192.168.3.172:5050/api/v1/afterservice/orders/5')
    resp = requests.get('http://localhost:5050/api/v1/afterservice/orders/5')
    print resp.json()

def simple_get_journals_test():
    resp = requests.get('http://192.168.3.172:5050/api/v1/afterservice/orders/journals')
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders/journals')
    print resp.json()

def simple_delete_test():
    resp = requests.delete('http://localhost:5050/api/v1/afterservice/orders/8')
    print resp.json()

def simple_get_rank_test():
    resp = requests.get('http://localhost:5050/api/v1/afterservice/dutyreports/abnormalrank')
    print resp.json()

# 更加细化的测试


if __name__ == "__main__":
    method = sys.argv[1]
    params = sys.argv[2:]
    print "&".join(params)
    if len(params) >= 1:
        globals()["_".join(["simple", method, "test"])](*params)
    else:
        globals()["_".join(["simple", method, "test"])]()