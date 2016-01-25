import re
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, models
from django.db.models.expressions import BaseExpression, Combinable
from django.db.models.query_utils import DeferredAttribute
from django.utils import timezone


# text patterns for "routine" documents
_routine_text = [
    'Congratulations extended',
    'Gratitude extended',
    'Recognition extended',
    'Issuance of permits for sign\(s\)',
    'Sidewalk cafe\(s\) for',
    'Canopy\(s\) for',
    'Awning\(s\) for',
    'Residential permit parking',
    'Handicapped Parking Permit',
    'Handicapped permit',
    'Grant\(s\) of privilege in public way',
    'Loading/Standing/Tow',
    'Senior citizens sewer',
    'Oath of office'
]


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



# temp code

def is_deferred(model, field):
    attr = model.__class__.__dict__.get(field.attname)
    return isinstance(attr, DeferredAttribute)


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

    def _is_deferred(self, field):
        attr = self.__class__.__dict__.get(field.attname)
        return isinstance(attr, DeferredAttribute)

    def _as_dict(self):
        """
        Return dict representation *without deferred fields* (which
        would cause the maximum recursion depth to be exceeeded).
        """
        d = {}
        for field in self._meta.fields:
            if self._is_deferred(field):
                continue

            # Using getattr for a null relation causes issues,
            # so just grab the related id instead
            if field.rel:
                field_value = getattr(self, '%s_id' % field.name)
            else:
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


class Person(LegistarModel):
    """People, e.g. Alderman, Mayor, etc"""
    first_name = models.TextField(blank=True)
    last_name = models.TextField()
    full_name = models.TextField()
    active_flag = models.IntegerField()
    used_sponsor_flag = models.IntegerField()
    matters = models.ManyToManyField('Matter', through='MatterSponsor')

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

    class Meta:
        verbose_name = 'MatterAttachment'

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


class Document(DirtyFieldsModel):
    """
    This is what we actually search on.
    """
    matter_attachment = models.OneToOneField(MatterAttachment, primary_key=True)
    sort_date = models.DateTimeField(null=True)
    text = models.TextField(blank=True)
    title = models.TextField(blank=True)
    sponsors = models.TextField(blank=True)
    text_vector = TsVectorField()
    text_vector_weighted = TsVectorField()
    is_routine = models.BooleanField(default=False)

    def __str__(self):
        return "%s [%s]" % \
            (self.matter_attachment.matter.title, self.matter_attachment.name)

    def _set_dependent_fields(self):
        """Initialize dependent instance fields"""
        matter = self.matter_attachment.matter

        self.sort_date = max([dt for dt in [
            matter.intro_date,
            matter.agenda_date,
            matter.passed_date,
            matter.enactment_date] if dt is not None], default=None)

        self.title = matter.title
        sponsors = [s.person.full_name for s in matter.mattersponsor_set.all()]
        self.sponsors = ';;;'.join(sponsors)

        self.is_routine = False
        for t in _routine_text:
            if re.search(r'\b%s\b' % t, self.text, re.I):
                self.is_routine = True
                break

    @classmethod
    def create_from_attachment(cls, matter_attachment, text):
        r = Document(matter_attachment=matter_attachment)
        r.text = '%s;;;%s' % (matter_attachment.matter.title, text)
        r._set_dependent_fields()
        r.save()
        return r

    def on_related_update(self):
        """Update fields when related data is updated"""
        self.text = '%s;;;%s' % \
            (self.matter_attachment.matter.title, self.text.split(';;;')[1])
        r._set_dependent_fields()
        r.save()

    def save(self, *args, update_text=False, **kwargs):
        """Override to update text_vector"""
        text_updated = update_text or (self.text != self._original_state['text'])
        super(Document, self).save(*args, **kwargs)

        if text_updated:
            with connection.cursor() as c:
                c.execute(
                    """UPDATE %s
                    SET text_vector = to_tsvector('english', coalesce(text, '') || '') ,
                    text_vector_weighted =
                        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                        setweight(to_tsvector('english', coalesce(sponsors, '')), 'B') ||
                        setweight(to_tsvector('english', coalesce(text, '')), 'D')
                    WHERE matter_attachment_id=%d""" \
                    % (self._meta.db_table, self.matter_attachment.id))


class Subscription(models.Model):
    """User alert subscription"""
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    query = models.TextField()
    last_check = models.DateTimeField(null=True, auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return 'id=%d, email=%s, query="%s"' % \
            (self.id, self.email, self.query)
