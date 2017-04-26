from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import WeblogicServer
import requests
from django.core.cache import cache
from stratahq.celery import app
from logging import log


# Weblogic tasks
@shared_task
def get_nodemanager_health():
    """Scheduled task to get nodemanager health in the background"""
    for wls in WeblogicServer.objects.all().iterator():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.nodemanager_port

        # Using a separate task we can asynchronously get all WLS nodemanager's health's
        check_tcp.apply_async(args=(proxy, host, port,),)


@shared_task
def get_adminserver_health():
    """Scheduled task to get adminserver health in the background"""
    for wls in WeblogicServer.objects.all().iterator():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.adminserver_port

        # Using a separate task we can asynchronously get all WLS adminserver's health's
        check_tcp.apply_async(args=(proxy, host, port,),)


@shared_task
def get_managed_servers():
    """Scheduled task to get the managed servers on each WLS server"""
    for wls in WeblogicServer.objects.all().iterator():
        proxy = wls.environment.api_proxy
        host = wls.connect_to()
        port = wls.adminserver_port
        user = wls.adminserver_user
        pwd = wls.adminserver_pass
        headers = {'Accept': 'application/json'}

        if wls.adminserver_ssl:
            scheme = 'https'
        else:
            scheme = 'http'

        ckey = 'weblogic:%s:managedservers' %  host

        uri = '%s/weblogic/%s/%s/%d/management/tenant-monitoring/servers' % (proxy, scheme, host, port)

        # Getting info and updating the cache can be an asynchronous operation
        get_weblogic_api.apply_async(args=(ckey, user, pwd, headers, uri))


@shared_task
def get_weblogic_api(ckey, user, pwd, headers, uri):
    """ Generic task to get data from the weblogic API and cache it for use elsewhere"""
    try:
        r = requests.get(uri, auth=(user, pwd), headers=headers, timeout=5)
        if r.status_code == 200:
            # We store the whole dict response here. You should extract the bits you need further up
            cache.set(ckey, r.json(), timeout=180)
        else:
            cache.set(ckey, r.status_code, timeout=180)
    except Exception as e:
        cache.set(ckey, 'ERROR', timeout=180)
        log.error(str(e))


@shared_task
def check_tcp(prxy, server, port):
    """ Generic task to check TCP port connectivity and cache it for use elsewhere"""
    ckey = 'tcp:%s:%d' % (server, port,)
    r = requests.get('%s/tcp/%s/%s' % (prxy, server, port,))
    cache.set(ckey, r.status_code, timeout=35)


# Scheduled tasks
app.conf.beat_schedule = {
    'nodemanager-health': {
        'task': 'assets.tasks.get_nodemanager_health',
        'schedule': 30,
    },
    'adminserver-health': {
        'task': 'assets.tasks.get_adminserver_health',
        'schedule': 30,
    },
    'managedservers-health': {
         'task': 'assets.tasks.get_managed_servers',
         'schedule': 30,
    },
}