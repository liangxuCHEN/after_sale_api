#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fabfile for Django
------------------

Only for Ubuntu/Debian
"""
__author__ = "louis_chen"

from fabric.api import env, local, require, sudo, settings, abort, run, cd, prompt
from fabric.contrib import files
import time

env.project_name = "afterservice_backend"
env.repository = "http://192.168.1.115/liangxuCHEN/after_sale_api.git"



def localhost():
    """
    Use the local test server
    """
    env.hosts = ['localhost']
    env.user = 'louis'
    env.path = '/home/%(user)s/deployment/%(project_name)s' % env
    env.virtualenv = "venv2017"


def webserver():
    """
    Use the remote server
    """
    env.hosts = ["192.168.3.172"]
    env.user = 'django'
    env.path = '/home/%(user)s/deployment/%(project_name)s' % env
    env.virtualenv = "venv2017"


def webserver_root():
    """
    Use the remote server
    """
    env.hosts = ['192.168.3.172']
    env.user = 'ls'
    #env.path = '/home/%(user)s/deployment/%(project_name)s' % env
    #env.virtualenv = "venv2017"


def update_project():
    """
    更新项目
    """
    
    webserver()
    require('hosts', provided_by=[webserver])
    require('path')

    if files.exists(env.path):
        run("cd %(path)s; git checkout master;git pull" % env,pty=True)
    else:
        run("git clone %(repository)s %(path)s;cd %(path)s;git checkout master;" %
            env, pty=True)


def kill_running_project():
    require('hosts', provided_by=[webserver])
    require('path')
    with cd(env.path):
        pids = run("ps -aux | grep 'gun.conf main.app'|grep -v 'grep'|awk '{print $2'}")
        pid_list = pids.split('\r\n')
        for i in pid_list:
            run('kill -9 %s' % i)


def stop_port():
    """
    断开端口
    """
    #require('hosts', provided_by=[webserver_root])
    sudo('fuser -k %s/tcp' % env.app_port)


def start_server_test():
    """
    新开服务
    """
    webserver()
    require('hosts', provided_by=[webserver])
    require('path')
    #webserver_root()
    env.app_port = '6060'
    update_project()
    #stop_port()
    with cd(env.path):
        run('screen -d -m Waixie_test gunicorn -c gun.conf main:app')


def start_server():
    """
    新开服务
    """
    webserver()
    #webserver_root()
    env.app_port = '5050'
    update_project()
    #stop_port()
    with cd(env.path):
        run('screen -d -m Waixie gunicorn -c gun.conf main:app')

def local_update():
    local(env.path)
    env.release = time.strftime('%Y%m%d%H%M%S')
    local('git add . ;git ci -m "auto update %(release)s"' % env)
    local('git push')
    update_project()


def local_start_server():
    local(env.path)
    local('gunicorn -c gun_test.conf main:app')


def kill_server(p_name):
    webserver()
    with cd(env.path):
        pids = run("ps -aux|grep '%s'|grep -v 'grep'|awk '{print $2}'" % p_name)
        pid_list = pids.split('\r\n')
        scrpit = ' '.join(pid_list[:-1])
        with settings(warn_only=True):
            run('kill -9 %s' % scrpit)


def restart_server():
    webserver()
    update_project()
    with cd(env.path):
        kill_server()
        run('gunicorn -c gun.conf main:app')


def restart_server_test():
    webserver()
    update_project()
    with cd(env.path):
        kill_server('gun_test')
        run('gunicorn -c gun_test.conf main:app')

