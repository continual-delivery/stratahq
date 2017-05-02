from ..models import Server
from django import template
from django.utils.formats import mark_safe

register = template.Library()


@register.filter(name='puppet_role_badge')
def puppet_role_badge(server):
    if server.puppet_role() is not None:
        return mark_safe('<span class="badge badge-primary">%s</span>' % server.puppet_role())


@register.filter(name='puppet_env_badge')
def puppet_env_badge(server):
    if server.puppet_environment() is not None:
        return mark_safe('<span class="badge badge-primary">%s</span>' % server.puppet_environment())


@register.filter(name='status_badge')
def status_badge(server):
    if server.status is not None:
        if server.status == 'live':
            return mark_safe('<span class="badge badge-danger">%s</span>' % server.get_status_display())
        else:
            return mark_safe('<span class="badge badge-primary">%s</span>' % server.get_status_display())
    else:
        return ''

