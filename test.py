#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests, json, sys

def fake_waixie():
    required_field = {
        "accuser_name": "测试公司",
        "creater_name": "测试",
        "saler_name": "sh",
        "reason": "test",
    }
    optional_field = {
        #"material_number": "sku2017082411541503546850",
        #"material_supplier_name": "成都市金虎家俱有限公司",
        #"creater_name": "陈俊文",
        
                                                                                                                                                           "duty_report": {"abnormal_type": 12}
    }
    after_filled = {
        #"reason": u"陈俊文"
    }

    required_field.update(optional_field)
    required_field.update(after_filled)

    return required_field

def simple_post_test():
    #resp = requests.post('http://192.168.3.172:5050/api/v1/afterservice/orders', json=fake_waixie())

    resp = requests.post('http://localhost:5050/api/v1/afterservice/orders', json=fake_waixie())
    print resp.json()

def simple_get_test(*params):
    if len(params) >= 1:
        resp = requests.get('http://localhost:5050/api/v1/afterservice/orders?%s' % "&".join(params))
    else:
        resp = requests.get('http://localhost:5050/api/v1/afterservice/orders')
        
    #resp = requests.get('http://localhost:5050/api/v1/afterservice/orders')
    print resp.json()


def simple_put_test():
    data = {}
    #data['serial_number'] = 'SH201707040001'
    data['operation'] = 'reject'
    #data['operation'] = 'reject'
    data['operator_name'] = 'test'
    data['remark'] = "123455555"
    #data['material_supplier_name'] = "东莞市景盛家具有限公司"
    #data['saler_name'] = "东莞市"
    #resp = requests.put('http://192.168.3.172:5050/api/v1/afterservice/orders/143', json=data)
    resp = requests.put('http://localhost:5050/api/v1/afterservice/orders/618', json=data)

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
def simple_get_ab_test():
    resp = requests.get('http://localhost:5050/api/v1/afterservice/orders/2/abnormal-products')
    print resp.json()

def simple_post_ab_test():
    resp = requests.post('http://localhost:5050/api/v1/afterservice/orders/2/abnormal-products', json={"product_list": [{}]})
    print resp.json()

def simple_put_ab_test():
    resp = requests.put('http://localhost:5050/api/v1/afterservice/orders/2/abnormal-products/11', json={"remark": "game"})
    print resp.json()


def simple_delet_test():
    resp = requests.delete('http://localhost:5050/api/v1/afterservice/deductionOrder/35')
    print resp.json()


def push_message():
    url = 'http://113.105.237.98:8806/outapply/PushMsg/pushms'
    resp = requests.post(url, json={"username": 'cs1,cs1', 'msg': 'have a nice day'})
    print resp.json()

if __name__ == "__main__":
    # method = sys.argv[1]
    # params = sys.argv[2:]
    # print "&".join(params)
    # if len(params) >= 1:
    #     globals()["_".join(["simple", method, "test"])](*params)
    # else:
    #     globals()["_".join(["simple", method, "test"])]()
    #simple_get_test()
    simple_put_test()
    #push_message()
    #simple_post_test()