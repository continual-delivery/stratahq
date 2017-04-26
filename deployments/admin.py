from django.contrib import admin
from django.utils.formats import mark_safe

# Register your models here.
from .models import DeploymentHistory


@admin.register(DeploymentHistory)
class DeploymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'customer_environment', 'application_stack', 'from_version', 'to_version',
                    'duration', 'status', '_servers')
    list_filter = ('status', 'application_stack', 'customer_environment')

    def _servers(self, obj):
        html = ""
        for s in obj.servers.split(','):
            html += '%s<br />' % s
        return mark_safe(html)