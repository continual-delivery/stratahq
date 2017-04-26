from django.contrib import admin
from django.utils.formats import mark_safe

# Register your models here.
from .models import Server, WeblogicServer, PuppetRole, HypervisorHost, Application, ApplicationStack, TaskHistory


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_ip', 'owner', 'status', 'role', 'puppet_role',
                    'environment', 'puppet_environment',)
    list_filter = ('role', 'environment', 'owner', 'status', 'os',)

    # We basically want to prevent servers from being manipulated here altogether
    # They should be managed from specific applications admin pages
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(ServerAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    # We want to make ALL fields readonly on this view.
    def get_readonly_fields(self, request, obj=None):
        return [ f.name for f in self.model._meta.fields ]


@admin.register(WeblogicServer)
class WeblogicServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_ip', 'is_virtual', 'virtual_host', 'edition', 'status', 'owner', 'environment',
                    '_nodemanager', '_adminserver', '_servers',)
    list_filter = ('role', 'environment', 'owner', 'status', 'os',)


    def _nodemanager(self, obj):
        return obj.nodemanager_health()
    _nodemanager.boolean = True

    def _adminserver(self, obj):
        return obj.adminserver_health()
    _adminserver.boolean = True

    def _servers(self, obj):
        srv_json = obj.managed_servers()
        print(srv_json)

        html = "<table>"
        if isinstance(srv_json, list):
            for s in srv_json:
                html += '<tr><th>%s</th><td>%s</td><td>%s</td></tr>' % (s['name'], s['state'], s['health'])
        else:
            html += '<tr><th>%s</th></tr>' % srv_json
        html += "</table>"
        return mark_safe(html)


    # We basically want to prevent WebLogic servers from being manipulated here altogether
    # They should be managed from specific applications admin pages
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(WeblogicServerAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    # We want to make ALL fields readonly on this view.
    def get_readonly_fields(self, request, obj=None):
        return [ f.name for f in self.model._meta.fields ]


@admin.register(HypervisorHost)
class HypervisorHostAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_ip', 'owner', 'role', 'environment', '_vm_guests',)

    def _vm_guests(self, obj):
        html=""
        for s in obj.guest_servers():
            html+='%s<br />' % s.name
        return mark_safe(html)


@admin.register(PuppetRole)
class PuppetRoleAdmin(admin.ModelAdmin):
    readonly_fields = ('puppet_role',)
    list_display = ('role', 'puppet_role', 'description',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'owner', 'description', 'status', 'nexus_url', 'default_port',
                    'default_ssl_port', 'default_jmx_port',)
    list_filter = ('owner',)

    # We basically want to prevent applications from being manipulated here altogether
    # They should be managed from specific team application admin pages
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    # We want to make ALL fields readonly on this view.
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(ApplicationStack)
class ApplicationStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'owner', 'description',)
    list_filter = ('owner',)

    # We basically want to prevent applications from being manipulated here altogether
    # They should be managed from specific team application admin pages
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(ApplicationStackAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    # We want to make ALL fields readonly on this view.
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'customer_environment', '_servers', 'start_time', 'duration', 'status', 'task_log',)
    list_filter = ('task_name', 'status')

    def _servers(self, obj):
        html=""
        for s in obj.servers.split(','):
            html+='%s<br />' % s
        return mark_safe(html)