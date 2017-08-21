#!/usr/bin/env python
# -*- coding: utf-8 -*-

from transitions import Machine
from aenum import Enum

class AfterSaleWorkflow(object):
    
    #  状态 = [已创建,     等待售后审批，          售后专员已审核，      等待负责人审批，        负责人已审批，     ]
    status = [
                'created', 'service_approving'， 'service_approved', 'manager_reviewing', 'manager_reviewed',
                'chief_reviewing', 'chief_reviewed', 'finance_reviewing', 'finance_reviewed'
             ]

    class WorkflowStatus(Name)
    
    def __init__():
        pass        

    