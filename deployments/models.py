from django.db import models

from assets.models import TaskHistory

# Create your models here.
class DeploymentHistory(TaskHistory):
    """
    Essentially a high-level, long lived log of deployment information
    We will add data programmatically and avoid foreign key relationships here
    """
    application_stack = models.CharField(max_length=64, db_index=True)
    from_version = models.CharField(max_length=64)
    to_version = models.CharField(max_length=64)

    class Meta:
        ordering = ('-start_time',)
        verbose_name_plural = 'Deployment history'

    def __str__(self):
        return self.application_stack





