from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from strata.models import StrataServer

class StrataAppServersView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    redirect_field_name = 'next'
    template_name = 'strata/servers.html'

    model = StrataServer

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(StrataAppServersView, self).get_context_data(**kwargs)
        # Add in a QuerySet of last 20 tasks
        context['server_role'] = 'app'
        return context

    def get_queryset(self):
        return StrataServer.objects.filter(role='app').order_by('name')

class StrataAssentisServersView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    redirect_field_name = 'next'
    template_name = 'strata/servers.html'

    model = StrataServer

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(StrataAssentisServersView, self).get_context_data(**kwargs)
        # Add in a QuerySet of last 20 tasks
        context['server_role'] = 'Assentis'
        return context

    def get_queryset(self):
        return StrataServer.objects.filter(role='ass').order_by('name')