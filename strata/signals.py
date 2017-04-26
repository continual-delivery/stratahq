from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import StrataCustomerStack


@receiver(pre_save, sender=StrataCustomerStack)
def save_last_version(sender, instance, *args, **kwargs):
    """
    Save the current version as the previous version 
    """
    if instance._StrataCustomerStack__version is not None:
        instance.previous_version = instance._StrataCustomerStack__version