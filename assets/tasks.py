from __future__ import absolute_import, unicode_literals
from celery import shared_task, Task
from .models import WeblogicServer
import requests
from django.core.cache import cache
from stratahq.celery import app
import jenkins
from stratahq.settings import JENKINS


# Jenkins tasks
class JenkinsTask(Task):
    _master = None

    @property
    def master(self):
        if self._master is None:
            self._master = jenkins.Jenkins(JENKINS['SERVER'], username=JENKINS['USER'], password=JENKINS['KEY'])
        return self._master


@app.task(base=JenkinsTask)
def run_jenkins_job(job_name, parameters={}):
    pass

@app.task(base=JenkinsTask)
def update_jenkins_joblist():
    """
    This background task runs to keep a dict of job names.
    """
    jobs = []
    for job in update_jenkins_joblist.master.get_jobs():
        """
        a job looks like this:
        {
	        '_class': 'hudson.model.FreeStyleProject',
	        'name': 'some-task',
	        'url': 'http://jenkins:8080/job/some-task/',
	        'color': 'blue',
	        'fullname': 'some-task'
        }
        """
        j = {}
        j[job['name']] = job['fullname']
        
        jobs.append(j.copy())

    cache.set('jenkins_joblist', jobs, 600)


# Weblogic tasks - Probably need a refactor here...?
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
    'jenkins-jobslist': {
        'task': 'assets.tasks.update_jenkins_joblist',
        'schedule': 300,
    },
}