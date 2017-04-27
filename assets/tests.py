from django.test import TestCase
from django.core.cache import cache
from .utils import timedgethostbyname

# Create your tests here.

class UtilsTests(TestCase):
    def test_timedgethostbyname_nosuchname(self):
        """
        timedgethostbyname() stores IP's in Django cache. A none existing key should return None.
        """
        hostname = 'nosuchname'
        timedgethostbyname(hostname, 5)
        ckey = '%s_lookup' % hostname
        ip = cache.get(ckey)

        self.assertEqual(ip, None)

    def test_timedgethostbyname_localhost(self):
        """
        timedgethostbyname() should cache an IP for a hostname passed to it
        """
        hostname = 'localhost'
        timedgethostbyname(hostname, 5)
        ckey = '%s_lookup' % hostname
        ip = cache.get(ckey)

        self.assertEqual(ip, '127.0.0.1')