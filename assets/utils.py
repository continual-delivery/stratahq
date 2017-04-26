import socket, os, sys, signal
from django.core.cache import cache
# Various hacks or functions that don't really fit anywhere else

def timedgethostbyname(hostname):
    """Get an IP address with a 1 second timeout. Usual is 5 or 10 second DNS request timeout."""
    ckey = '%s_lookup' % hostname
    pid = os.fork()
    print(pid)
    if pid == 0:
        cache.set(ckey, None, 2)
        # 1 second timeout
        signal.alarm(1)
        try:
            address = socket.gethostbyname(hostname)
        except:
            return None
        cache.set(ckey, address, 2)
    else:
        os.wait()
        return cache.get(ckey)
