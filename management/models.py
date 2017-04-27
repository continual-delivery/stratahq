from django.db import models
from django.contrib.auth.models import User, Group

_TEAMS = (
    ('strata', 'Strata Admin'),
    ('devs', 'Development Teams'),
    ('webs', 'Web Services'),
    ('server', 'Server Team'),
)

class Customer(models.Model):
    """A customer. A dev squad is also considered a customer."""
    name = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(max_length=16, unique=True)
    environments = models.ManyToManyField('Environment', through='CustomerEnvironment')

    def __str__(self):
        return self.name

# Environment - dev, uat, prd
class Environment(models.Model):
    """An environment such as dev, uat or live."""
    name = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(max_length=8, unique=True)
    agent_tag = models.CharField(max_length=64, default='none')
    api_proxy = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CustomerEnvironment(models.Model):
    """A customer can have many environments. This model allows us to extend that relationship and add extra data"""
    customer = models.ForeignKey('Customer', to_field='short_name')
    environment = models.ForeignKey('Environment', to_field='short_name')
    # Auto-generated on save
    name = models.CharField(max_length=64, blank=True, unique=True)

    class Meta:
        ordering = ['customer', 'environment']

    def __str__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        self.name = '%s_%s' % (self.customer.short_name, self.environment.short_name)
        super(CustomerEnvironment, self).save(*args, **kwargs)


class Team(models.Model):
    """This model holds the users / groups assigned to teams"""
    team = models.CharField(unique=True, max_length=32, choices=_TEAMS)
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return '%s' % self.get_team_display()