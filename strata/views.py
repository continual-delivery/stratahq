from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from assets.models import _SERVER_STATUSES, ServerRoleTask
from .models import StrataServer
from .forms import ServerForm

class StrataServerView(LoginRequiredMixin, generic.ListView):
    """
    Base Server view as many of our views / forms are the same with minor changes
    """
    login_url = '/login'
    redirect_field_name = 'next'
    template_name = 'strata/servers.html'
    model = StrataServer
    server_form = ServerForm()

class StrataAppServersView(StrataServerView):
    """
    Strata App Server view
    """
    queryset = StrataServer.objects.filter(role='app').order_by('name')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(StrataAppServersView, self).get_context_data(**kwargs)
        # Add in a QuerySet of last 20 tasks
        context['server_role'] = 'app'
        context['server_form'] = self.server_form
        context['server_statuses'] = _SERVER_STATUSES
        context['server_tasks'] = ServerRoleTask.objects.get(role='app').tasks.all()
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        server = StrataServer.objects.get(pk=request.POST.get('pk'))
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/strata/servers/app/#%s' % server.name)




class StrataAssentisServersView(StrataServerView):
    """
    Assentis Server view
    """
    queryset = StrataServer.objects.filter(role='ass').order_by('name')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(StrataAssentisServersView, self).get_context_data(**kwargs)
        # Add in a QuerySet of last 20 tasks
        context['server_role'] = 'Assentis'
        return context