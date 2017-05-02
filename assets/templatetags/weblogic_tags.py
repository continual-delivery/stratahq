from ..services import tcp_connectivity, managed_servers
from django import template
from django.utils.formats import mark_safe

register = template.Library()

@register.filter(name='tcp_health')
def tcp_health(host, port):
    html = ""
    if tcp_connectivity(host, port):
        html += '<i class="fa fa-check-circle fa-1x text-success" aria-hidden="true"></i>'
    else:
        html += '<i class="fa fa-times-circle fa-1x text-danger" aria-hidden="true"></i>'
    return mark_safe(html)

@register.filter(name='get_managed_servers')
def get_managed_servers(host):
    srv_json = managed_servers(host)
    html = "<table>"
    if isinstance(srv_json, list):
        for s in srv_json:
            # Create a row but sort out CSS to make table rows smaller
            html += '<tr><th style="all:unset; padding-right:5px;"><strong>%s</strong></th>' \
                    '<td style="all: unset; padding-right:5px;">%s</td>' \
                    '<td style="all: unset; padding-right:5px;">%s</td></tr>' % (s['name'],
                                                                                 s['state'],
                                                                                 s['health'])
    else:
        html += '<tr><th style="all:unset; padding-right:5px;"><strong>%s</strong></th></tr>' % srv_json
    html += "</table>"
    return mark_safe(html)
