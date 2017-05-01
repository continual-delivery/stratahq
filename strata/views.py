from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from management.models import Customer, Environment, CustomerEnvironment
from assets.models import TaskHistory, Server, Application

class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    redirect_field_name = 'next'
    template_name = 'home/index.html'
    context_object_name = 'latest_task_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return TaskHistory.objects.order_by('-start_time')[:5]