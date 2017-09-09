API测试环境：192.168.3.172:5050

## 启动程序

```
python main.py
```

## API 访问方式
* POST  http://192.168.3.172:5050/api/v1/afterservice/orders   售后单创建

```
data = {
"type": "售后单订单类型", //必填
"customer_name": "被告供应商名称", //必填
"accuser_name": "原告供应商名称编号", //必填
"creater_name": "创建⼈"， //必填
"reason": "异常原因", //必填
"remark": "异常描述" //必填
}
```

* GET  http://192.168.3.172:5050/api/v1/afterservice/orders?
status=&workflow_status=&creater_name=&page=&per_page=   售后单访问



## 详细API文档说明在API_doc.pdf

[api 文档](http://192.168.1.115:7500/after_sale_api)