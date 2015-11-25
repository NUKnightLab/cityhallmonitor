from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from cityhallmonitor.models import DirtyFieldsModel


@receiver(pre_save, sender=DirtyFieldsModel)
def handle_pre_save(sender, instance, *args, **kwargs):
    """Set updated_at timestamp if model is actually dirty"""
    if hasattr(sender, 'is_dirty'):
        if instance.is_dirty():
            instance.updated_at = timezone.now()
    

@receiver(post_save, sender=DirtyFieldsModel)
def handle_post_save(sender, instance, **kwargs):
    """Reset dirty state"""
    if hasattr(sender, 'reset_state'):
        instance.reset_state()
    
