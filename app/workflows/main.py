#!/usr/bin/env python
# -*- coding:utf-8 -*-

from aenum import Enum

__author__ = "chenyj"

"""
流程状态 = 
进行中， 已完成， 已取消(撤销)， 已过期(超时)
"""
workflow_status = ['in_progress', 'done', 'cancel', 'overdue']
WorkflowStatus = Enum('workflow', ''.join(workflow_status))

"""
售后服务订单状态 = 
已创建, 等待售后专员审核， 售后专员已审核， 等待负责人审批， 负责人已审批
（小碗)等待主管审批， 主管已审批， 等待财务审批， 财务已审批 
"""
after_service_status = [
    'created', 'service_approving', 'service_approved', 'manager_reviewing', 'manager_reviewed', 'chief_reviewing',
    'chief_reviewed', 'finance_reviewing', 'finance_reviewed'
    ]
AfterServiceStatus = Enum('after_service_status', " ".join(after_service_status))

after_service_trigger = [
    {'trigger': 'done', 'source':'created', 'dest': 'service_approving'},
    {'trigger': 'done', 'source':'service_approving', 'dest': 'service_approved'},
    {'trigger': 'done', 'source':'service_approved', 'dest': 'manager_reviewing'},
    {'trigger': 'done', 'source':'manager_reviewing', 'dest': 'manager_reviewed'},
    {'trigger': 'done', 'source':'manager_reviewed', 'dest': 'chief_reviewing'},
    {'trigger': 'done', 'source':'chief_reviewing', 'dest': 'chief_reviewed'},
    {'trigger': 'done', 'source':'chief_reviewed', 'dest': 'finance_reviewing'},
    {'trigger': 'done', 'source':'finance_reviewing', 'dest': 'finance_reviewed'}
]