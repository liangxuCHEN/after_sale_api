#!/usr/bin/env python
# -*- coding:utf-8 -*-
from transitions import Machine
from .main import WorkflowStatus, AfterServiceStatus, workflow_status, after_service_status, after_service_trigger

class Workflow(object):
    
    workflow_status = workflow_status
    status = after_service_status

    def __init__(self, name):
        self.name = name
        self.kitten_rescued = 0
        self.flow = Machine(model=self, states=Workflow.status, initial='created', transitions=after_service_trigger)
