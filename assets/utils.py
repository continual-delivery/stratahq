import socket, os, sys, signal
from django.core.cache import cache
# Various hacks or functions that don't really fit anywhere else

def timedgethostbyname(hostname, timeout=1):
    """Get an IP address with a 2 second timeout. Usual is 5 or 10 second DNS request timeout."""
    ckey = '%s_lookup' % hostname
    pid = os.fork()
    if pid == 0:
        cache.set(ckey, None, timeout)
        # 1 second timeout
        signal.alarm(timeout)
        try:
            address = socket.gethostbyname(hostname)
        except:
            return None
        cache.set(ckey, address, timeout)
    else:
        os.wait()
        return cache.get(ckey)
