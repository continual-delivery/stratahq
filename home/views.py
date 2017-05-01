from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from management.models import Customer, Environment, CustomerEnvironment
from assets.models import TaskHistory, Server, Application

class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    redirect_field_name = 'next'
    template_name = 'home/index.html'

    model = TaskHistory

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in a QuerySet of last 20 tasks
        context['task_list'] = TaskHistory.objects.order_by('-start_time', 'duration')[:20]
        # Add in counts for various server types
        context['server_count'] = Server.objects.count()
        context['customer_count'] = Customer.objects.count()
        context['customer_environment_count'] = CustomerEnvironment.objects.count()
        context['application_count'] = Application.objects.count()
        return context