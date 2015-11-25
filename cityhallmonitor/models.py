from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, models
from django.db.models.expressions import BaseExpression, Combinable
from django.utils import timezone
 

# https://djangosnippets.org/snippets/1328/
class TsVectorField(models.Field):
    description = "PostgreSQL tsvector field"
    
    def __init__(self, text='', *args, **kwargs):
        self.text = text
        kwargs['null'] = True
        kwargs['editable'] = False
        kwargs['serialize'] = False
        super(TsVectorField, self).__init__(*args, **kwargs)
            
    def db_type(self, connection):
        return 'tsvector'


# Based on //github.com/romgar/django-dirtyfields/blob/develop/src/dirtyfields/dirtyfields.py
class DirtyFieldsModel(models.Model):
    """
    Model with created/updated timestamps
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsModel, self).__init__(*args, **kwargs)
        self.reset_state()

    def _as_dict(self):
        """Return dict representation"""
        d = {}
        for field in self._meta.fields:
            field_value = getattr(self, field.name)
            
            if not isinstance(field_value, (BaseExpression, Combinable)):
                d[field.name] = field_value
        return d 
        
    def reset_state(self):
        """Reset saved state"""
        self._original_state = self._as_dict()
        
    def is_dirty(self):
        """Dirty or not"""
        if not self.id:
            return True
        
        for k, v in self._as_dict().items():
            if v != self._original_state[k]:
                return True
        
        return False    


class LegistarModel(DirtyFieldsModel):
    """
    Common fields and methods
    """
    id = models.IntegerField(primary_key=True)
    guid = models.CharField(max_length=100,blank=True)
    last_modified = models.DateTimeField(null=True)
    row_version = models.CharField(max_length=100, blank=True)
    
    class Meta:
        abstract = True
                          
    @classmethod
    def get_or_new(cls, id):
        """Get existing record by id or create a new instance"""
        try:
            return cls.objects.get(id=id)
        except ObjectDoesNotExist:
            return cls(id=id)
                
            
class Action(LegistarModel):
    """Actions, e.g., Adopted, Amended in Committee"""
    name = models.TextField()
    active_flag = models.IntegerField()
    used_flag = models.IntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name        
                       
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['ActionId'])
        r.guid = d['ActionGuid'] or ''
        r.last_modified = d['ActionLastModifiedUtc']+'Z'
        r.row_version = d['ActionRowVersion']
        r.name = d['ActionName']
        r.active_flag =d['ActionActiveFlag']
        r.used_flag = d['ActionUsedFlag']
        return r


class Person(LegistarModel):
    """People, e.g. Alderman, Mayor, etc"""
    first_name = models.TextField(blank=True)
    last_name = models.TextField()
    full_name = models.TextField()
    active_flag = models.IntegerField()
    used_sponsor_flag = models.IntegerField()    

    class Meta:
        ordering = ['last_name', 'first_name']
 
    def __str__(self):
        return self.full_name

    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['PersonId'])
        r.guid = d['PersonGuid'] or ''
        r.last_modified = d['PersonLastModifiedUtc']+'Z'
        r.row_version = d['PersonRowVersion']
        r.first_name = d['PersonFirstName']
        r.last_name = d['PersonLastName']
        r.full_name = d['PersonFullName']
        r.active_flag = d['PersonActiveFlag']
        r.used_sponsor_flag = d['PersonUsedSponsorFlag']
        return r


class BodyType(LegistarModel):
    """Body types, e.g., Department, Joint Committee"""
    name = models.TextField()
    
    class Meta:
        ordering = ['name']
        verbose_name = 'BodyType'
 
    def __str__(self):
        return self.name
    
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['BodyTypeId'])   
        r.guid = d['BodyTypeGuid'] or ''
        r.row_version = d['BodyTypeRowVersion']
        r.last_modified = d['BodyTypeLastModifiedUtc']+'Z'
        r.name = d['BodyTypeName']
        return r


class Body(LegistarModel):
    """Bodies"""
    name = models.CharField(max_length=255) 
    body_type = models.ForeignKey(BodyType)
    meet_flag = models.IntegerField()
    active_flag = models.IntegerField()
    sort = models.IntegerField()
    description = models.TextField(blank=True)
    contact = models.ForeignKey(Person, blank=True, null=True, on_delete=models.SET_NULL) 
    used_control_flag = models.IntegerField()
    n_members = models.IntegerField()
    used_acting_flag = models.IntegerField()
    used_target_flag = models.IntegerField()
    used_sponsor_flag = models.IntegerField()
        
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Bodies'

    def __str__(self):
        return self.name
    
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['BodyId'])   
        r.guid = d['BodyGuid'] or ''
        r.last_modified = d['BodyLastModifiedUtc']+'Z'
        r.row_version = d['BodyRowVersion']
        r.name = d['BodyName']
        r.body_type_id = d['BodyTypeId']
        r.meet_flag = d['BodyMeetFlag']
        r.active_flag = d['BodyActiveFlag']
        r.sort = d['BodySort']
        r.description = d['BodyDescription'] or ''
        r.contact = d['BodyContactNameId']
        r.used_control_flag = d['BodyUsedControlFlag']
        r.n_members = d['BodyNumberOfMembers']
        r.used_acting_flag = d['BodyUsedActingFlag']
        r.used_target_flag = d['BodyUsedTargetFlag']
        r.used_sponsor_flag = d['BodyUsedSponsorFlag']
        return r


class MatterStatus(LegistarModel):
    """Statuses, e.g., Adopted, Approved, Failed to Pass"""
    name = models.TextField()
    description = models.TextField(blank=True)
    sort = models.IntegerField()
    active_flag = models.IntegerField()
    used_flag = models.IntegerField()

    class Meta:
        ordering = ['name', 'sort']
        verbose_name = 'MatterStatus'
        verbose_name_plural = 'MatterStatuses'
    
    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['MatterStatusId'])   
        r.guid = d['MatterStatusGuid'] or ''
        r.last_modified = d['MatterStatusLastModifiedUtc']+'Z'
        r.row_version = d['MatterStatusRowVersion']
        r.name = d['MatterStatusName']
        r.description = d['MatterStatusDescription'] or ''
        r.sort = d['MatterStatusSort']
        r.active_flag = d['MatterStatusActiveFlag']
        r.used_flag = d['MatterStatusUsedFlag']
        return r
            
                 
class MatterType(LegistarModel):
    """Types, e.g., Appointment, Executive Order, Ordinance"""
    name = models.TextField()
    description = models.TextField(blank=True)
    sort = models.IntegerField()
    active_flag = models.IntegerField()
    used_flag = models.IntegerField()

    class Meta:
        ordering = ['name', 'sort']
        verbose_name = 'MatterType'
        verbose_name_plural = 'MatterTypes'

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['MatterTypeId'])   
        r.guid = d['MatterTypeGuid'] or ''
        r.last_modified = d['MatterTypeLastModifiedUtc']+'Z'
        r.row_version = d['MatterTypeRowVersion']
        r.name = d['MatterTypeName']
        r.description = d['MatterTypeDescription'] or ''
        r.sort = d['MatterTypeSort']
        r.active_flag = d['MatterTypeActiveFlag']
        r.used_flag = d['MatterTypeUsedFlag']
        return r


class Matter(LegistarModel):
    """
    Matters
    """
    file = models.TextField()
    name = models.TextField(blank=True)
    title = models.TextField(blank=True)
    matter_type = models.ForeignKey(MatterType)
    matter_status = models.ForeignKey(MatterStatus)
    body = models.ForeignKey(Body)
    intro_date = models.DateTimeField(null=True)
    agenda_date = models.DateTimeField(null=True)
    passed_date = models.DateTimeField(null=True)
    enactment_date = models.DateTimeField(null=True)
    enactment_number = models.TextField(blank=True)
    requester = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    version = models.TextField(blank=True)
    text1 = models.TextField(blank=True)
    text2 = models.TextField(blank=True)
    text3 = models.TextField(blank=True)
    text4 = models.TextField(blank=True)
    text5 = models.TextField(blank=True)
    date1 = models.DateTimeField(null=True)
    date2 = models.DateTimeField(null=True)
    ex_text1 = models.TextField(blank=True)
    ex_text2 = models.TextField(blank=True)
    ex_text3 = models.TextField(blank=True)
    ex_text4 = models.TextField(blank=True)
    ex_text5 = models.TextField(blank=True)
    ex_text6 = models.TextField(blank=True)
    ex_text7 = models.TextField(blank=True)
    ex_text8 = models.TextField(blank=True)
    ex_text9 = models.TextField(blank=True)
    ex_text10 = models.TextField(blank=True)    
    ex_date1 = models.DateTimeField(null=True)
    ex_date2 = models.DateTimeField(null=True)
    ex_date3 = models.DateTimeField(null=True)
    ex_date4 = models.DateTimeField(null=True)
    ex_date5 = models.DateTimeField(null=True)
    ex_date6 = models.DateTimeField(null=True)
    ex_date7 = models.DateTimeField(null=True)
    ex_date8 = models.DateTimeField(null=True)
    ex_date9 = models.DateTimeField(null=True)
    ex_date10 = models.DateTimeField(null=True)
    attachments_obtained_at = models.DateTimeField(null=True)
    sponsors_obtained_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.title or self.name or self.file
    
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['MatterId'])   
        r.guid = d['MatterGuid'] or ''
        r.last_modified = d['MatterLastModifiedUtc']+'Z' if d['MatterLastModifiedUtc'] else None
        r.row_version = d['MatterRowVersion']
        r.file = d['MatterFile'] or ''
        r.name = d['MatterName'] or ''
        r.title = d['MatterTitle'] or ''
        r.matter_type_id = d['MatterTypeId']
        r.matter_status_id = d['MatterStatusId']
        r.body_id = d['MatterBodyId']
        r.intro_date = d['MatterIntroDate']+'Z' if d['MatterIntroDate'] else None
        r.agenda_date = d['MatterAgendaDate']+'Z' if d['MatterAgendaDate'] else None
        r.passed_date = d['MatterPassedDate']+'Z' if d['MatterPassedDate'] else None
        r.enactment_date = d['MatterEnactmentDate']+'Z' if d['MatterEnactmentDate'] else None
        r.enactment_number = d['MatterEnactmentNumber'] or ''
        r.requester = d['MatterRequester'] or ''
        r.notes = d['MatterNotes'] or ''
        r.version = d['MatterVersion'] or ''
        r.text1 = d['MatterText1'] or ''
        r.text2 = d['MatterText2'] or ''
        r.text3 = d['MatterText3'] or ''
        r.text4 = d['MatterText4'] or ''
        r.text5 = d['MatterText5'] or ''
        r.date1 = d['MatterDate1']+'Z' if d['MatterDate1'] else None
        r.date2 = d['MatterDate2']+'Z' if d['MatterDate2'] else None
        r.ex_text1 = d['MatterEXText1'] or ''
        r.ex_text2 = d['MatterEXText2'] or ''
        r.ex_text3 = d['MatterEXText3'] or ''
        r.ex_text4 = d['MatterEXText4'] or ''
        r.ex_text5 = d['MatterEXText5'] or ''
        r.ex_text6 = d['MatterEXText6'] or ''
        r.ex_text7 = d['MatterEXText7'] or ''
        r.ex_text8 = d['MatterEXText8'] or ''
        r.ex_text9 = d['MatterEXText9'] or ''
        r.ex_text10 = d['MatterEXText10'] or ''
        r.ex_date1 = d['MatterEXDate1']+'Z' if d['MatterEXDate1'] else None
        r.ex_date2 = d['MatterEXDate2']+'Z' if d['MatterEXDate2'] else None
        r.ex_date3 = d['MatterEXDate3']+'Z' if d['MatterEXDate3'] else None
        r.ex_date4 = d['MatterEXDate4']+'Z' if d['MatterEXDate4'] else None
        r.ex_date5 = d['MatterEXDate5']+'Z' if d['MatterEXDate5'] else None
        r.ex_date6 = d['MatterEXDate6']+'Z' if d['MatterEXDate6'] else None
        r.ex_date7 = d['MatterEXDate7']+'Z' if d['MatterEXDate7'] else None
        r.ex_date8 = d['MatterEXDate8']+'Z' if d['MatterEXDate8'] else None
        r.ex_date9 = d['MatterEXDate9']+'Z' if d['MatterEXDate9'] else None
        r.ex_date10 = d['MatterEXDate10']+'Z' if d['MatterEXDate10'] else None
        return r


class MatterSponsor(LegistarModel):
    """
    Sponsors (links Matter to Person)
    
    In the Legistar data, the MatterSponsorNameId can be None, which is
    indicative of no sponsor (e.g. a simple communication).  Those
    records are skipped over in the pull_sponsors management command.
    """
    matter = models.ForeignKey(Matter)   
    matter_version = models.TextField(blank=True, default='0')    
    person = models.ForeignKey(Person)
    sequence = models.IntegerField()

    class Meta:
        verbose_name = 'MatterSponsor'

    def __str__(self):
        return self.person.full_name

    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['MatterSponsorId'])   
        r.guid = d['MatterSponsorGuid'] or ''
        r.last_modified = d['MatterSponsorLastModifiedUtc']+'Z'
        r.row_version = d['MatterSponsorRowVersion']
        r.matter_id = d['MatterSponsorMatterId']
        r.matter_version = d['MatterSponsorMatterVersion']
        r.person_id = d['MatterSponsorNameId']
        r.sequence = d['MatterSponsorSequence']
        return r


class MatterAttachment(LegistarModel):
    """Attachments"""
    matter = models.ForeignKey(Matter)
    name = models.TextField(blank=True, default='')
    hyperlink = models.TextField(blank=True)
    file_name = models.TextField(blank=True)
    matter_version = models.TextField(blank=True)    
    is_hyperlink = models.BooleanField()
    is_supporting_doc = models.BooleanField()
    binary = models.TextField(blank=True, default='') # <MatterAttachmentBinary i:nil="true"/>
    link_obtained_at = models.DateTimeField(null=True)
    
    dc_id = models.TextField(blank=True, default='') # DocumentCloud document id
    text = models.TextField(blank=True) # extracted text
    text_vector = TsVectorField() # postgresql tsvector

    __original_text = None

    class Meta:
        verbose_name = 'MatterAttachment'

    def __init__(self, *args, **kwargs):
        """Override to save original text to detect changes"""
        super(MatterAttachment, self).__init__(*args, **kwargs)
        self.__original_text = self.text

    def save(self, *args, **kwargs):
        """Override to detect changes to text and update tsvector field"""
        update_tsvector = self.text != self.__original_text                            
        super(MatterAttachment, self).save(*args, **kwargs)
        self.__original_text = self.text
        
        # Update tsvector field
        if update_tsvector:
            with connection.cursor() as c:            
                c.execute(
                    "UPDATE %s" \
                    " SET text_vector = to_tsvector('english', coalesce(text, '') || '')" \
                    " WHERE id=%d" % (self._meta.db_table, self.id))

    def __str__(self):
        return self.file_name
    
    @classmethod
    def from_json(cls, matter_id, d):
        """
        Convert legistar dictionary to model instance
        Note that you need to pass in MatterId!
        """
        r = cls.get_or_new(d['MatterAttachmentId'])       
        r.guid = d['MatterAttachmentGuid'] or ''
        r.last_modified = d['MatterAttachmentLastModifiedUtc']+'Z'          
        r.row_version = d['MatterAttachmentRowVersion']
        r.matter_id = matter_id
        r.matter_version = d['MatterAttachmentMatterVersion']
        r.name = d['MatterAttachmentName'] or ''
        r.hyperlink = d['MatterAttachmentHyperlink']
        r.file_name = d['MatterAttachmentFileName']
        r.is_hyperlink = d['MatterAttachmentIsHyperlink']
        r.is_supporting_doc = d['MatterAttachmentIsSupportingDocument']
        r.binary = d['MatterAttachmentBinary'] or ''
        return r

    
class VoteType(LegistarModel):
    """Vote types e.g., Yea, Nay, Present"""
    name = models.TextField()
    plural_name = models.TextField()
    used_for = models.IntegerField()
    result = models.IntegerField()
    sort = models.IntegerField()
    
    class Meta:
        ordering = ['name', 'sort']
        verbose_name = 'VoteType'
        
    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['VoteTypeId'])       
        r.guid = d['VoteTypeGuid'] or ''
        r.last_modified = d['VoteTypeLastModifiedUtc']+'Z'
        r.row_version = d['VoteTypeRowVersion']
        r.name = d['VoteTypeName']
        r.used_for = d['VoteTypeUsedFor']
        r.result = d['VoteTypeResult']
        r.sort = d['VoteTypeSort']
        return r
    
    
class Event(LegistarModel):
    """Events, e.g. meetings and such"""
    body = models.ForeignKey(Body, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateField()
    time = models.TextField(blank=True)
    video_status = models.TextField(blank=True)
    agenda_status_id = models.IntegerField(null=True)
    agenda_status_name = models.TextField(blank=True)
    minutes_status_id = models.IntegerField(null=True)
    minutes_status_name = models.TextField(blank=True)
    location = models.TextField(blank=True)
    
    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.body.name
    
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['EventId'])       
        r.guid = d['EventGuid'] or ''
        r.last_modified = d['EventLastModifiedUtc']+'Z'
        r.row_version = d['EventRowVersion']
        r.body_id = d['EventBodyId']
        r.date = d['EventDate'].split('T')[0]
        r.time = d['EventTime'] or ''
        r.video_status = d['EventVideoStatus'] or ''
        r.agenda_status_id = d['EventAgendaStatusId'] or 0
        r.agenda_status_name = d['EventAgendaStatusName'] or ''
        r.minutes_status_id = d['EventMinutesStatusId'] or 0
        r.minutes_status_name = d['EventMinutesStatusName'] or ''
        r.location = d['EventLocation'] or ''
        return r


class EventItem(LegistarModel):
    event = models.ForeignKey(Event)
    agenda_sequence = models.IntegerField()
    minutes_sequence = models.IntegerField()
    agenda_number = models.TextField(blank=True, default='')
    video = models.IntegerField(default=0)
    video_index = models.IntegerField(default=0)
    version = models.TextField(blank=True, default='')
    agenda_note = models.TextField(blank=True, default='')
    minutes_note = models.TextField(blank=True, default='')
    action = models.ForeignKey(Action, blank=True, null=True, on_delete=models.SET_NULL)
    passed_flag = models.IntegerField(default=0)
    passed_flag_name = models.TextField(blank=True, default='')
    roll_call_flag = models.IntegerField(default=0)
    flag_extra = models.IntegerField(default=0)
    title = models.TextField(blank=True, default='')
    tally = models.TextField(blank=True, default='')
    consent = models.IntegerField(default=0)
    mover = models.ForeignKey(Person, related_name='mover', blank=True, null=True, on_delete=models.SET_NULL)
    seconder = models.ForeignKey(Person, related_name='seconder', blank=True, null=True, on_delete=models.SET_NULL)
    matter = models.ForeignKey(Matter, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['agenda_sequence']
        verbose_name = 'EventItem'
    
    def __str__(self):
        return self.matter
    
    @classmethod
    def from_json(cls, d):
        """Convert legistar dictionary to model instance"""
        r = cls.get_or_new(d['EventItemId'])       
        r.guid = d['EventItemGuid'] or ''
        r.last_modified = d['EventItemLastModifiedUtc']+'Z'
        r.row_version = d['EventItemRowVersion']
        r.event_id = d['EventItemEventId']
        r.agenda_sequence = d['EventItemAgendaSequence'] or 0
        r.minutes_sequence = d['EventItemMinutesSequence'] or 0
        r.agenda_number = d['EventItemAgendaNumber'] or ''
        r.video = d['EventItemVideo'] or 0
        r.video_index = d['EventItemVideoIndex'] or 0            
        r.version = d['EventItemVersion'] or ''            
        r.agenda_note = d['EventItemAgendaNote'] or ''
        r.minutes_note = d['EventItemMinutesNote'] or ''
        r.action_id = d['EventItemActionId']
        r.passed_flag = d['EventItemPassedFlag'] or 0
        r.passed_flag_name = d['EventItemPassedFlagName'] or ''
        r.roll_call_flag = d['EventItemRollCallFlag'] or 0
        r.flag_extra = d['EventItemFlagExtra'] or 0
        r.title = d['EventItemTitle'] or ''
        r.tally = d['EventItemTally'] or ''
        r.consent = d['EventItemConsent'] or 0
        r.mover_id = d['EventItemMoverId']
        r.seconder_id = d['EventItemSeconderId']
        r.matter_id = d['EventItemMatterId']
        return r


class Subscription(models.Model):
    """User alert subscription"""
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    query = models.TextField()
    last_check = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return 'id=%d, email=%s, query="%s"' % \
            (self.id, self.email, self.query)
    
    
