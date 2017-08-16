#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
--------------
Too Simple Now
--------------
SECERT_KEY
FLASK_ADMIN
DEV_DATABASE_URL
"""
import os
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECERT_KEY') or '1e4cbec1-39e0-43b8-92fd-03013469ef08'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASK_MAIL_SUBJECT_PREFIX = '[YYchenyj]'
    FLASK_MAIL_SENDER = 'FLASK Admin <15622100628@163.com>'
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN') or 'chenyj'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    #MAIL_SERVER = ''
    #MAIL_PORT = 587
    #MAIL_USE_TLS = True
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'data.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mssql+pymssql://BS-Prt:123123@192.168.1.253:1433/BSPRODUCTCENTER'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}