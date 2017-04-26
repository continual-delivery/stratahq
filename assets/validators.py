from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import re

def is_valid_hostname(hostname):
    """Checks if an FQDN is valid to RFC1123 standards."""
    if len(hostname) > 255:
        raise ValidationError(
            _('Name: %(hostname)s is too long'),
            params={'hostname': hostname},
        )
    if hostname[-1] == ".":
        hostname = hostname[:-1]

    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if all(allowed.match(x) for x in hostname.split(".")) is False:
        raise ValidationError(
            _('%(hostname)s is not a valid RFC1123 hostname'),
            params={'hostname': hostname},
        )

def is_unprivileged_port(port):
    if port < 1024 or port > 65535:
        raise ValidationError(
            _('Port: %(port)d should be between 1024 and 65535'),
            params={'port': port},
        )
