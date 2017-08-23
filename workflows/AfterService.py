#!/usr/bin/env python
# -*- coding:utf-8 -*-
from transitions import Machine
from .main import WorkflowStatus, AfterServiceStatus, workflow_status, after_service_status, after_service_trigger, workflow_trigger

class SubWorkflow(object):
        def __init__(self, status_code):
            self.kitten_rescued = 0
            that_flow_status = WorkflowStatus(status_code).name
            self.flow = Machine(model=self, states=Workflow.workflow_status, initial=that_flow_status, transitions=workflow_trigger)

        def status_code(self):
            return WorkflowStatus[self.state].value

class Workflow(object):
    
    workflow_status = workflow_status
    service_status = after_service_status

    def __init__(self, name, status_code, flow_status_code):
        self.name = name
        self.kitten_rescued = 0
        
        that_status = AfterServiceStatus(status_code).name
        self.flow = Machine(model=self, states=Workflow.service_status, initial=that_status, transitions=after_service_trigger)
        self.workflow = SubWorkflow(flow_status_code)

    def status_code(self):
        return AfterServiceStatus[self.state].value
