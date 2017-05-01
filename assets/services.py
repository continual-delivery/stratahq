from django.core.cache import cache

# Services are standalone things that don't really fit in a Model or view. A global variable from cache or an API
# call could be services.

try:
    _JENKINS_JOBLIST = cache.get('jenkins_joblist')
except:
    _JENKINS_JOBLIST = ()


def all_jobs():
    l = []
    if _JENKINS_JOBLIST is not None:
        l.extend(_JENKINS_JOBLIST)
    # Add other joblists here
    return l

def tcp_connectivity(server, port):
    ckey = 'tcp:%s:%d' % (server, port)
    if cache.get(ckey) is 200:
        return True
    else:
        return False

def managed_servers(server):
    ckey = 'weblogic:%s:managedservers' % server
    try:
        return cache.get(ckey)['body']['items']
    except:
        return 'Error: %s' % str(cache.get(ckey))
