#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymssql
from contextlib import closing

LINK = "mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER?charset=utf8"
CONNECTION = {
    "host": "192.168.1.253:1433",
    "user": "BS-Prt",
    "password": '123123',
    "database": "BSPRODUCTCENTER",
    "charset": "utf8"
}


class SqlHelper(object):
    def __init__(self):
        self._conn = pymssql.connect(**CONNECTION)
        self._cur = self._conn.cursor()
        if not self._cur:
            raise Exception("Database setting wrong")
        self._conn.close()

    def exec_query(self, sql):
        with closing(pymssql.connect(**CONNECTION)) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
        return res

    def find_supplier_by_name(self, **kwargs):
        return self.exec_query(
            "select Id, SupplierName from  T_PRT_SupplierBasicInfo  where IsLogisticSupplier=1"
        )

    def find_saler_by_name(self, **kwargs):
        # todo: fix the bug
        query = " and ".join([ "=".join(e) for e in kwargs.items()])
        print "select Id, UserName from t_sys_user where " + query if len(query) > 0 else  "select Id, UserName from t_sys_user"
        return self.exec_query(
            "select Id, UserName from t_sys_user where " + query if len(query) > 0 else  "select Id, UserName from t_sys_user"
        )

    def find_product_by_name(self, **kwargs):
        return self.exec_query(
            "select * from T_PRT_AllProduct"
        )

    def find_user_type(self, user):
        return self.exec_query(
            "select * from V_SaleAfteTypePerson where UserName='%s'" % user
        )


if __name__ == '__main__':
    sql = SqlHelper()
    res = sql.find_user_type(u'何正杰'.encode('utf-8'))
    print res