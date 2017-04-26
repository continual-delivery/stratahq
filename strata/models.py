from django.db import models
from django.db.models import Q
from management.models import CustomerEnvironment
from assets.models import Server, WeblogicServer, WindowsServer, TomcatServer, Application, ApplicationStack


class StrataServer(WeblogicServer):
    """
    A Strata server is a WebLogic server
    """

    # Override the default owner here
    def __init__(self, *args, **kwargs):
        super(StrataServer, self).__init__(*args, **kwargs)
        self._meta.get_field('owner').default = 'strata'
        self._meta.get_field('role').default = 'app'



class AssentisServer(TomcatServer):
    """
    An Assentis server runs Tomcat
    """

    # Override the default owner here
    def __init__(self, *args, **kwargs):
        super(AssentisServer, self).__init__(*args, **kwargs)
        self._meta.get_field('owner').default = 'strata'
        self._meta.get_field('role').default = 'ass'


class OrbsServer(WindowsServer):
    """
    An ORBS Server runs on Windows
    """

    # Override the default owner here
    def __init__(self, *args, **kwargs):
        super(OrbsServer, self).__init__(*args, **kwargs)
        self._meta.get_field('owner').default = 'strata'
        self._meta.get_field('role').default = 'orb'


class StrataApplication(Application):
    """
    Applications that belong to the strata team such as: Strata, Echelon, Quotes Engine,
    EDI Engine.
    """

    # Override the default owner here
    def __init__(self, *args, **kwargs):
        super(StrataApplication, self).__init__(*args, **kwargs)
        self._meta.get_field('owner').default = 'strata'

    def __str__(self):
        return self.name

class SortableStrataApplication(models.Model):
    """
    This class stores the deployment ordering for stacks
    """
    application = models.ForeignKey('StrataApplication')
    deploy_order = models.PositiveSmallIntegerField(default=0, null=False, blank=False)
    stack = models.ForeignKey('StrataApplicationStack')

    class Meta:
        ordering = ('deploy_order',)


class StrataApplicationStack(ApplicationStack):
    """
    An application stack is the collection of apps that create together are a deployable unit
    For example, The Strata Application Stack is made up of: nameserver, strata, si, echelon
    """

    def applications(self):
        return [a.application for a in SortableStrataApplication.objects.filter(stack=self.id)]

    # Override the default owner here
    def __init__(self, *args, **kwargs):
        super(StrataApplicationStack, self).__init__(*args, **kwargs)
        self._meta.get_field('owner').default = 'strata'

    def __str__(self):
        return self.name


class StrataCustomerStack(models.Model):
    """
    Each customer gets application stacks with a version
    """
    customer_environment = models.ForeignKey(CustomerEnvironment)
    stack = models.ForeignKey('StrataApplicationStack', related_name='stack')
    servers = models.ManyToManyField(Server, null=True, blank=True)
    version = models.CharField(max_length=16,
                               help_text='Version of the application stack on customer environment')
    previous_version = models.CharField(max_length=16, blank=True, null=True,
                               help_text='Last version of the application stack on customer environment')

    servers = models.ManyToManyField(Server, blank=True)

    # We denormailize, auto-save and index these so we can filter from them and avoid joins and complexity
    customer = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    environment = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    class Meta:
        unique_together = ('customer_environment', 'stack',)

    def name(self):
        return '%s_%s' % (self.customer_environment.name, self.stack.short_name)

    def __init__(self, *args, **kwargs):
        super(StrataCustomerStack, self).__init__(*args, **kwargs)
        self.__version = self.version

    def save(self, *args, **kwargs):
        self.customer = self.customer_environment.customer.name
        self.environment = self.customer_environment.environment.name
        super(StrataCustomerStack, self).save(*args, **kwargs)

    def __str__(self):
        return self.name()
