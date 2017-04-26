from django.contrib import admin

from .models import Customer, Environment, CustomerEnvironment
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_celery_results.models import TaskResult

admin.site.unregister((PeriodicTask, IntervalSchedule, CrontabSchedule, TaskResult,))

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomerEnvironment)
class CustomerEnvironmentAdmin(admin.ModelAdmin):
    readonly_fields = ('name',)
