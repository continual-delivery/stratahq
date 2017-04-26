from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import WeblogicServer
import requests
from django.core.cache import cache
from stratahq.celery import app

# Weblogic tasks
@shared_task
def get_nodemanager_health():
    for wls in WeblogicServer.objects.all():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.nodemanager_port

        check_tcp.apply_async(args=(proxy, host, port,),)

@shared_task
def get_adminserver_health():
    for wls in WeblogicServer.objects.all():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.adminserver_port

        check_tcp.apply_async(args=(proxy, host, port,),)


@shared_task
def get_managed_servers():
    for wls in WeblogicServer.objects.all():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.adminserver_port
        user = wls.adminserver_user
        pwd = wls.adminserver_pass

        r = requests.get('http://apiprx:3000/weblogic/http/weblogic/8001/management/tenant-monitoring/servers', auth=( user, pwd))
        if r.status_code == 200:
            print(r.body)
        else:
            pass


#http_proxy="" curl --header "Accept:application/json" http://weblogic:admin_password@localhost:3000/weblogic/http/weblogic/8001/management/tenant-monitoring/servers

@shared_task()
def check_tcp(prxy, server, port):
    ckey = 'tcp:%s:%d' % (server, port,)
    r = requests.get('%s/tcp/%s/%s' % (prxy, server, port,))
    cache.set(ckey, r.status_code, timeout=35)

app.conf.beat_schedule = {
    'nodemanager-health': {
        'task': 'assets.tasks.get_nodemanager_health',
        'schedule': 30.0,
    },
    'adminserver-health': {
        'task': 'assets.tasks.get_adminserver_health',
        'schedule': 30.0,
    },
    'managedservers-health': {
         'task': 'assets.tasks.get_managed_servers',
         'schedule': 30.0,
    },
}