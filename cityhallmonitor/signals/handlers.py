from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from cityhallmonitor.models import DirtyFieldsModel, \
    Matter, MatterAttachment, MatterSponsor

     
@receiver(pre_save, sender=DirtyFieldsModel)
def handle_pre_save(sender, instance, *args, **kwargs):
    """Set updated_at timestamp if model is actually dirty"""
    if hasattr(sender, 'is_dirty'):
        if instance.is_dirty():
            instance.updated_at = timezone.now()
    
@receiver(post_save, sender=DirtyFieldsModel)
def handle_post_save(sender, instance, **kwargs):
    """Reset dirty state, maybe update related Document"""
    if hasattr(sender, 'is_dirty'):
        if sender == Matter and instance.is_dirty():
            for r in instance.matterattachment_set.all():
                if hasattr(r, 'document'):
                    r.document.on_related_update()
        elif sender == MatterAttachment and instance.is_dirty():
            if hasattr(instance, 'document'):
                r.document.on_related_update()
        elif sender == MatterSponsor and instance.is_dirty():
            for r in instance.matter.matterattachment_set.all():
                if hasattr(r, 'document'):
                    r.document.on_related_update()
                
    if hasattr(sender, 'reset_state'):
        instance.reset_state()
    
