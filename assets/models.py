from django.db import models
from management.models import Environment, _TEAMS
from .validators import is_valid_hostname, is_unprivileged_port
from .utils import timedgethostbyname
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from .services import all_jobs

_SERVERROLES = (
    ('app', 'Strata App Server'),
    ('ass', 'Assentis Server'),
    ('orb', 'ORBS Server'),
    ('lb', 'HAProxy Load Balancer'),
    ('ovm', 'OVM Host'),
    ('vm', 'VMWare Host'),
)

_OS = (
    ('el6', 'CentOS 6'),
    ('el7', 'CentOS 7'),
    ('win2k8', 'Windows Server 2008'),
    ('win2k12', 'Windows Server 2012'),
    ('vmware', 'VMWare ESXi'),
    ('ovm', 'Oracle Virtual Machine'),
)

_WEBLOGIC_EDITIONS = (
    ('developer', 'Developer Edition'),
    ('standard', 'Standard Edition'),
    ('enterprise', 'Enterprise Edition'),
)

_TOMCAT_VERSIONS = (
    ('7', 'Tomcat 7'),
    ('8', 'Tomcat 8'),
)

_SERVER_STATUSES = (
    ('blank', 'Needs Provisioning'),
    ('installed', 'OS Installed'),
    ('unnassigned', 'Unassigned'),
    ('live', 'Live System'),
    ('maintenance', 'Out for Maintenance'),
    ('broken', 'Needs Fixing'),
    ('burn', 'Can be Humanely Destroyed'),
    ('decom', 'Decommisioned'),
)

_APPLICATION_STATUSES = (
    ('develop', 'Under Development'),
    ('production', 'In Production'),
    ('retired', 'Retired'),
)

_TASK_STATUSES = (
    ('success', 'SUCCESS'),
    ('running', 'IN PROGRESS'),
    ('failed', 'FAILED'),
    ('rollback', 'ROLLBACK'),
)

class Server(models.Model):
    """
    A server, this is used as a class to extend application specific servers from such as a WebLogic server.
    """
    name = models.CharField(max_length=255, db_index=True, unique=True, validators=[is_valid_hostname],
                            help_text='The FQDN of the server.')
    role = models.CharField(max_length=8, choices=_SERVERROLES)
    owner = models.CharField(max_length=8, choices=_TEAMS, default='server')
    primary_ip = models.GenericIPAddressField(verbose_name='Primary IP', blank=True, null=True, unique=True,
                                              help_text='Usually assigned to eth0 or ens160. Leave blank to try and resolve.')
    environment = models.ForeignKey(Environment)
    status = models.CharField(max_length=32, choices=_SERVER_STATUSES, default='live')
    override_puppet_role = models.CharField(max_length=64, blank=True, null=True)
    override_puppet_environment = models.CharField(max_length=64, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    virtual_host = models.ForeignKey('HypervisorHost', null=True, blank=True)
    os = models.CharField(verbose_name='OS', max_length=8, choices=_OS, null=True, blank=True)
    cpus = models.PositiveSmallIntegerField(default=1)
    cores = models.PositiveSmallIntegerField(default=0)
    ram = models.PositiveSmallIntegerField(default=0)

    class Meta(object):
        ordering = ('name',)

    def clean(self, *args, **kwargs):
        try:
            if self.stratacustomerstack_set.get()[0].environment is not self.environment:
                raise ValidationError(
                    _('Server is in use by: %(customer_stack)s. Cannot move environment.'),
                    params={'customer_stack': self.stratacustomerstack_set.get()},
                )
        except:
            pass

        try:
            if self.stratacustomerstack_set.get()[0].stack.valid_target is not self.role:
                raise ValidationError(
                    _('Server is in use by: %(customer_stack)s. Cannot move environment.'),
                    params={'customer_stack': self.stratacustomerstack_set.get()},
                )
        except:
            pass

        super(Server, self).clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        """If the primary ip address wasn't known, we try to resolve it on save"""
        if self.primary_ip is '':
            self.primary_ip = timedgethostbyname(self.name)

        super(Server, self).save(*args, **kwargs)


    def puppet_role(self):
        """
        Return the Puppet role assigned to this server
        """
        try:
            if self.override_puppet_role is not None:
                return self.override_puppet_role
            else:
                return PuppetRole.objects.all().filter(role=self.role)[0].puppet_role
        except:
            return None

    def puppet_environment(self):
        """
        Return the Puppet environment assigned to this server
        """
        try:
            if self.override_puppet_environment is not None:
                return self.override_puppet_environment
            else:
                return self.environment.short_name
        except:
            return None

    def connect_to(self):
        """
        Returns the primary ip address or the hostname to connect to
        """
        if self.primary_ip is not None:
            return self.name
        else:
            return self.name


    def total_cores(self):
        """
        Total number of cores on this server
        """
        try:
            return self.cpus * self.cores
        except:
            return None

    def __str__(self):
        return self.name


class HypervisorHost(Server):
    """
    A hypervisor host is used for the relationship between host / vm
    and reporting things like WebLogic licences etc... 
    """
    def guest_servers(self):
        return self.server_set.all()

    def __str__(self):
        return self.name


class WeblogicServer(Server):
    """
    Weblogic servers have added WebLogic stuff
    """
    edition = models.CharField(max_length=16, choices=_WEBLOGIC_EDITIONS, default='standard')
    nodemanager_port = models.PositiveSmallIntegerField(validators=[is_unprivileged_port], default=5666)
    nodemanager_ssl = models.BooleanField(default=False)
    adminserver_port = models.PositiveSmallIntegerField(validators=[is_unprivileged_port], default=7001)
    adminserver_ssl = models.BooleanField(default=False)
    adminserver_user = models.CharField(max_length=256, default='weblogic')
    adminserver_pass = models.CharField(max_length=256, default='letmein1')

    def __str__(self):
        return self.name

class WindowsServer(Server):
    """
    Windows servers have Windows stuff
    """

    def __str__(self):
        return self.name


class TomcatServer(Server):
    """
    Tomcat servers have added Tomcat stuff
    """
    version = models.CharField(max_length=8, choices=_TOMCAT_VERSIONS, default='8')

    def __str__(self):
        return self.name


class PuppetRole(models.Model):
    """
    A server's role can be linked to a Puppet role.
    """
    role = models.CharField(max_length=8, choices=_SERVERROLES, unique=True)
    description = models.TextField(max_length=512)
    # Auto-generated on save
    puppet_role = models.CharField(max_length=32, help_text='Autogenerated Puppet role applied to this server')

    def save(self, *args, **kwargs):
        self.puppet_role = '::role::%s' % self.role
        super(PuppetRole, self).save(*args, **kwargs)

    class Meta(object):
        ordering = ('role',)

    def __str__(self):
        return self.get_role_display()


class Application(models.Model):
    """
    An application is an asset too. This base class is used to extend upon
    in team specific classes.
    """
    name = models.CharField(max_length=32, unique=True)
    short_name =  models.CharField(max_length=16, unique=True)
    description = models.TextField(max_length=512)
    status = models.CharField(max_length=32, choices=_APPLICATION_STATUSES, default='production')
    # This should be set in team specific Save method
    owner = models.CharField(max_length=8, choices=_TEAMS)

    default_port = models.PositiveSmallIntegerField(validators=[is_unprivileged_port], null=True, blank=True)
    default_ssl_port = models.PositiveSmallIntegerField(validators=[is_unprivileged_port], null=True, blank=True)
    default_jmx_port = models.PositiveSmallIntegerField(validators=[is_unprivileged_port], null=True, blank=True)
    healthcheck_url = models.CharField(max_length=64, default='/healthcheck')
    has_healthcheck = models.BooleanField(default=False)

    nexus_url = models.URLField(null=True, blank=True,
                                help_text='URL to Nexus assets')
    pre_deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                  help_text='The name of the Jenkins job to run before deploying this application')
    deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                      help_text='The name of the Jenkins job to deploy this application')
    post_deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                      help_text='The name of the Jenkins job to run after deploying this application')

    class Meta(object):
        ordering = ('name',)

    def __str__(self):
        return self.name


class ApplicationStack(models.Model):
    """
    An application stack is a collection (or 1) of applications that are deloyed together for something to run.
    """
    name = models.CharField(max_length=32)
    short_name =  models.CharField(max_length=16, unique=True)
    # This should be set in team specific Save method
    owner = models.CharField(max_length=8, choices=_TEAMS)
    description = models.TextField(max_length=512)
    valid_target = models.CharField(max_length=32, choices=_SERVERROLES, null=True, blank=True,
                                    help_text='What server role can this stack be deployed onto?')
    pre_deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                  help_text='The name of the Jenkins job to run before deploying this application')
    deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                      help_text='The name of the Jenkins job to deploy this application')
    post_deploy_job = models.CharField(max_length=32, null=True, blank=True, choices=all_jobs(),
                                      help_text='The name of the Jenkins job to run after deploying this application')

    class Meta(object):
        ordering = ('name',)


# Create your models here.
class TaskHistory(models.Model):
    """
    Essentially a high-level, long lived log of task information
    We will add data programmatically and avoid foreign key relationships here
    """
    task_name = models.CharField(max_length=64, db_index=True)
    customer_environment = models.CharField(max_length=64, db_index=True)
    servers = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=_TASK_STATUSES, db_index=True)
    task_log = models.URLField()
    ran_by = models.CharField(max_length=64, default='Admin User')
    reason = models.CharField(max_length=128, default='-')
    level = models.CharField(max_length=32, default='primary')

    class Meta:
        ordering = ('-start_time',)
        verbose_name_plural = 'Task history'

    def save(self, *args, **kwargs):
        if bool(self.end_time) and bool(self.start_time):
            self.duration = self.end_time - self.start_time
        super(TaskHistory, self).save(*args, **kwargs)

    def __str__(self):
        return self.task_name
