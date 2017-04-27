from django.contrib import admin

from .models import Customer, Environment, CustomerEnvironment, Team
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_celery_results.models import TaskResult

# Hide all these
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


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('users', 'groups')
    list_display = ('team', '_users', '_groups',)


    def _users(self, obj):
        user_count = obj.users.count()
        if user_count == 1:
            return '%d User' % user_count
        else:
            return '%d Users' % user_count


    def _groups(self, obj):
        group_count = obj.groups.count()
        if group_count == 1:
            return '%d Group' % group_count
        else:
            return '%d Groups' % group_count