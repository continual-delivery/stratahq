from django.contrib import admin
from django import forms
from django.utils.formats import mark_safe
from adminsortable2.admin import SortableInlineAdminMixin

# Register your models here.
from assets.models import Server
from assets.services import tcp_connectivity, managed_servers
from .models import StrataServer, StrataApplication, StrataApplicationStack, \
    SortableStrataApplication, StrataCustomerStack

@admin.register(StrataServer)
class StrataServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_ip', 'owner', 'role', 'puppet_role', 'environment', 'puppet_environment',
                    '_nodemanager', '_adminserver','_servers',)
    list_filter = ('environment', 'owner',)


    def _nodemanager(self, obj):
        return tcp_connectivity(obj.connect_to(), obj.nodemanager_port)
    _nodemanager.boolean = True

    def _adminserver(self, obj):
        return tcp_connectivity(obj.connect_to(), obj.adminserver_port)
    _adminserver.boolean = True

    def _servers(self, obj):
        srv_json = managed_servers(obj.connect_to())
        html = '<table>'
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


@admin.register(StrataApplication)
class StrataApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'description', 'nexus_url', 'default_port',
                    'default_ssl_port', 'default_jmx_port',)


class SortableStrataApplicationInline(SortableInlineAdminMixin, admin.TabularInline):
    classes = ('extrapretty',)
    model = SortableStrataApplication
    extra = 1

@admin.register(StrataApplicationStack)
class ApplicationStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'valid_target', 'description', '_applications')
    inlines = (SortableStrataApplicationInline,)

    def _applications(self, obj):
        html=""
        for a in obj.applications():
            html+='%s<br />' % a.name
        return mark_safe(html)


class StrataCustomerStackForm(forms.ModelForm):
    class Meta:
        model = StrataCustomerStack
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StrataCustomerStackForm, self).__init__(*args, **kwargs)
        try:
            if bool(self.instance.stack) and bool(self.instance.customer_environment):
                self.fields['servers'].queryset = Server.objects.filter(
                    role=self.instance.stack.valid_target,
                    environment=self.instance.customer_environment.environment
                )
        except:
            self.fields['servers'].queryset = Server.objects.none()


@admin.register(StrataCustomerStack)
class StrataCustomerStackAdmin(admin.ModelAdmin):
    form = StrataCustomerStackForm
    list_display = ('name', 'customer', 'environment', 'version', 'previous_version', '_servers')
    list_filter = ('customer', 'environment', 'stack')
    filter_horizontal = ('servers',)

    def _servers(self, obj):
        html=""
        for s in obj.servers.all():
            html+='%s<br />' % s.name
        return mark_safe(html)