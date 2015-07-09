from django.db import models

class Action(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    guid = models.CharField(max_length=100,blank=True)
    row_version = models.CharField(max_length=100, blank=True)
    last_modified = models.DateTimeField(null=True)
    name = models.TextField()
    active_flag = models.SmallIntegerField()
    used_flag = models.SmallIntegerField()

    def __str__(self):
        return self.name
            
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Action(
            id=d['ActionId'],
            guid=d['ActionGuid'] or '',
            row_version=d['ActionRowVersion'],
            last_modified=d['ActionLastModifiedUtc']+'Z',
            name=d['ActionName'],
            active_flag=d['ActionActiveFlag'],
            used_flag=d['ActionUsedFlag'])

            
class MatterType(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    guid = models.CharField(max_length=100, blank=True)
    row_version = models.CharField(max_length=100, blank=True)
    last_modified = models.DateTimeField(null=True)
    name = models.TextField()
    description=models.TextField(blank=True)
    sort=models.IntegerField()
    active_flag = models.SmallIntegerField()
    used_flag = models.SmallIntegerField()

    def __str__(self):
        return self.name

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return MatterType(
            id=d['MatterTypeId'],
            guid=d['MatterTypeGuid'] or '',
            row_version=d['MatterTypeRowVersion'],
            last_modified=d['MatterTypeLastModifiedUtc']+'Z',
            name=d['MatterTypeName'],
            description=d['MatterTypeDescription'],
            sort=d['MatterTypeSort'],
            active_flag=d['MatterTypeActiveFlag'],
            used_flag=d['MatterTypeUsedFlag'])
