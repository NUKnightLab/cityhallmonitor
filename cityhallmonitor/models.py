from django.db import models


class LegistarModel(models.Model):
    """
    Common fields
    """
    id = models.IntegerField(primary_key=True)
    guid = models.CharField(max_length=100,blank=True)
    last_modified = models.DateTimeField(null=True)
    row_version = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True
    
    
class Action(LegistarModel):
    """Actions, e.g., Adopted, Amended in Committee"""
    name = models.TextField()
    active_flag = models.IntegerField()
    used_flag = models.IntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
            
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Action(
            id=d['ActionId'],
            guid=d['ActionGuid'] or '',
            last_modified=d['ActionLastModifiedUtc']+'Z',
            row_version=d['ActionRowVersion'],
            name=d['ActionName'],
            active_flag=d['ActionActiveFlag'],
            used_flag=d['ActionUsedFlag'])


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

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Person(
            id=d['PersonId'],
            guid=d['PersonGuid'] or '',
            last_modified=d['PersonLastModifiedUtc']+'Z',
            row_version=d['PersonRowVersion'],
            first_name=d['PersonFirstName'],
            last_name=d['PersonLastName'],
            full_name=d['PersonFullName'],
            active_flag=d['PersonActiveFlag'],
            used_sponsor_flag=d['PersonUsedSponsorFlag'])


class BodyType(LegistarModel):
    """Body types, e.g., Department, Joint Committee"""
    name = models.TextField()
    
    class Meta:
        ordering = ['name']
        verbose_name = 'BodyType'
 

    def __str__(self):
        return self.name
    
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return BodyType(
            id=d['BodyTypeId'],
            guid=d['BodyTypeGuid'] or '',
            row_version=d['BodyTypeRowVersion'],
            last_modified=d['BodyTypeLastModifiedUtc']+'Z',
            name=d['BodyTypeName'])


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
    
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Body(
            id=d['BodyId'],
            guid=d['BodyGuid'] or '',
            last_modified=d['BodyLastModifiedUtc']+'Z',
            row_version=d['BodyRowVersion'],
            name=d['BodyName'],
            body_type_id=d['BodyTypeId'],
            meet_flag=d['BodyMeetFlag'],
            active_flag=d['BodyActiveFlag'],
            sort=d['BodySort'],
            description=d['BodyDescription'] or '',
            contact=d['BodyContactNameId'],
            used_control_flag=d['BodyUsedControlFlag'],
            n_members=d['BodyNumberOfMembers'],
            used_acting_flag=d['BodyUsedActingFlag'],
            used_target_flag=d['BodyUsedTargetFlag'],
            used_sponsor_flag=d['BodyUsedSponsorFlag'])


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

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return MatterStatus(
            id=d['MatterStatusId'],
            guid=d['MatterStatusGuid'] or '',
            last_modified=d['MatterStatusLastModifiedUtc']+'Z',
            row_version=d['MatterStatusRowVersion'],
            name=d['MatterStatusName'],
            description=d['MatterStatusDescription'] or '',
            sort=d['MatterStatusSort'],
            active_flag=d['MatterStatusActiveFlag'],
            used_flag=d['MatterStatusUsedFlag'])
            
                 
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

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return MatterType(
            id=d['MatterTypeId'],
            guid=d['MatterTypeGuid'] or '',
            last_modified=d['MatterTypeLastModifiedUtc']+'Z',
            row_version=d['MatterTypeRowVersion'],
            name=d['MatterTypeName'],
            description=d['MatterTypeDescription'] or '',
            sort=d['MatterTypeSort'],
            active_flag=d['MatterTypeActiveFlag'],
            used_flag=d['MatterTypeUsedFlag'])


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
    
    def __str__(self):
        return self.title or self.name or self.file
    
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Matter(
            id=d['MatterId'],
            guid=d['MatterGuid'] or '',
            last_modified=d['MatterLastModifiedUtc']+'Z' if d['MatterLastModifiedUtc'] else None,
            row_version=d['MatterRowVersion'],
            file=d['MatterFile'] or '',
            name=d['MatterName'] or '',
            title=d['MatterTitle'] or '',
            matter_type_id=d['MatterTypeId'],
            matter_status_id=d['MatterStatusId'],
            body_id=d['MatterBodyId'],
            intro_date=d['MatterIntroDate']+'Z' if d['MatterIntroDate'] else None,
            agenda_date=d['MatterAgendaDate']+'Z' if d['MatterAgendaDate'] else None,
            passed_date=d['MatterPassedDate']+'Z' if d['MatterPassedDate'] else None,
            enactment_date=d['MatterEnactmentDate']+'Z' if d['MatterEnactmentDate'] else None,
            enactment_number=d['MatterEnactmentNumber'] or '',
            requester=d['MatterRequester'] or '',
            notes=d['MatterNotes'] or '',
            version=d['MatterVersion'] or '',
            text1=d['MatterText1'] or '',
            text2=d['MatterText2'] or '',
            text3=d['MatterText3'] or '',
            text4=d['MatterText4'] or '',
            text5=d['MatterText5'] or '',
            date1=d['MatterDate1']+'Z' if d['MatterDate1'] else None,
            date2=d['MatterDate2']+'Z' if d['MatterDate2'] else None,
            ex_text1=d['MatterEXText1'] or '',
            ex_text2=d['MatterEXText2'] or '',
            ex_text3=d['MatterEXText3'] or '',
            ex_text4=d['MatterEXText4'] or '',
            ex_text5=d['MatterEXText5'] or '',
            ex_text6=d['MatterEXText6'] or '',
            ex_text7=d['MatterEXText7'] or '',
            ex_text8=d['MatterEXText8'] or '',
            ex_text9=d['MatterEXText9'] or '',
            ex_text10=d['MatterEXText10'] or '',
            ex_date1=d['MatterEXDate1']+'Z' if d['MatterEXDate1'] else None,
            ex_date2=d['MatterEXDate2']+'Z' if d['MatterEXDate2'] else None,
            ex_date3=d['MatterEXDate3']+'Z' if d['MatterEXDate3'] else None,
            ex_date4=d['MatterEXDate4']+'Z' if d['MatterEXDate4'] else None,
            ex_date5=d['MatterEXDate5']+'Z' if d['MatterEXDate5'] else None,
            ex_date6=d['MatterEXDate6']+'Z' if d['MatterEXDate6'] else None,
            ex_date7=d['MatterEXDate7']+'Z' if d['MatterEXDate7'] else None,
            ex_date8=d['MatterEXDate8']+'Z' if d['MatterEXDate8'] else None,
            ex_date9=d['MatterEXDate9']+'Z' if d['MatterEXDate9'] else None,
            ex_date10=d['MatterEXDate10']+'Z' if d['MatterEXDate10'] else None)   


class MatterSponsor(models.Model):
    """
    Sponsors (links Matter to Person)
    """
    id = models.IntegerField(primary_key=True)
    guid = models.CharField(max_length=100, blank=True)
    row_version = models.CharField(max_length=100, blank=True)
    last_modified = models.DateTimeField(null=True)        
    matter = models.ForeignKey(Matter)   
    matter_version = models.TextField(blank=True, default='0')    
    person = models.ForeignKey(Person)
    sequence = models.IntegerField()

    class Meta:
        # TODO: set ordering my person name?
        verbose_name = 'MatterSponsor'

    def __str__(self):
        return self.person.full_name

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return MatterSponsor(
            id=d['MatterSponsorId'],
            guid=d['MatterSponsorGuid'] or '',
            last_modified=d['MatterSponsorLastModifiedUtc']+'Z',
            row_version=d['MatterSponsorRowVersion'],
            matter_id=d['MatterSponsorMatterId'],
            matter_version=d['MatterSponsorMatterVersion'],
            person_id=d['MatterSponsorNameId'],
            sequence=d['MatterSponsorSequence'])


class MatterAttachment(LegistarModel):
    """Attachments"""
    matter = models.ForeignKey(Matter)
    name = models.TextField()
    hyperlink = models.TextField(blank=True)
    file_name = models.TextField(blank=True)
    matter_version = models.TextField(blank=True)    
    is_hyperlink = models.BooleanField()
    is_supporting_doc = models.BooleanField()
    binary = models.TextField(blank=True, default='') # <MatterAttachmentBinary i:nil="true"/>

    class Meta:
        #ordering =??
        verbose_name = 'MatterAttachment'

    def __str__(self):
        return self.file_name
    
    def from_json(matter_id, d):
        """
        Convert legistar dictionary to model instance
        Note that you need to pass in MatterId!
        """
        return MatterAttachment(
            id=d['MatterAttachmentId'],
            guid=d['MatterAttachmentGuid'] or '',
            last_modified=d['MatterAttachmentLastModifiedUtc']+'Z',          
            row_version=d['MatterAttachmentRowVersion'],
            matter_id=matter_id,
            matter_version=d['MatterAttachmentMatterVersion'],
            name=d['MatterAttachmentName'],
            hyperlink=d['MatterAttachmentHyperlink'],
            file_name=d['MatterAttachmentFileName'],
            is_hyperlink=d['MatterAttachmentIsHyperlink'],
            is_supporting_doc=d['MatterAttachmentIsSupportingDocument'],
            binary=d['MatterAttachmentBinary'] or '')
    
    
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

    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return VoteType(
            id=d['VoteTypeId'],
            guid=d['VoteTypeGuid'] or '',
            last_modified=d['VoteTypeLastModifiedUtc']+'Z',
            row_version=d['VoteTypeRowVersion'],
            name=d['VoteTypeName'],
            used_for=d['VoteTypeUsedFor'],
            result=d['VoteTypeResult'],
            sort=d['VoteTypeSort'])
    
    
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
    
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return Event(
            id=d['EventId'],
            guid=d['EventGuid'] or '',
            last_modified=d['EventLastModifiedUtc']+'Z',
            row_version=d['EventRowVersion'],
            body_id=d['EventBodyId'],
            date=d['EventDate'].split('T')[0],
            time=d['EventTime'] or '',
            video_status=d['EventVideoStatus'] or '',
            agenda_status_id=d['EventAgendaStatusId'] or 0,
            agenda_status_name=d['EventAgendaStatusName'] or '',
            minutes_status_id=d['EventMinutesStatusId'] or 0,
            minutes_status_name=d['EventMinutesStatusName'] or '',
            location=d['EventLocation'] or '')


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
    
    def __str__(self):
        return self.matter
    
    def from_json(d):
        """Convert legistar dictionary to model instance"""
        return EventItem(
            id=d['EventItemId'],
            guid=d['EventItemGuid'] or '',
            last_modified=d['EventItemLastModifiedUtc']+'Z',
            row_version=d['EventItemRowVersion'],
            event_id=d['EventItemEventId'],
            agenda_sequence=d['EventItemAgendaSequence'] or 0,
            minutes_sequence=d['EventItemMinutesSequence'] or 0,
            agenda_number=d['EventItemAgendaNumber'] or '',
            video=d['EventItemVideo'] or 0,
            video_index=d['EventItemVideoIndex'] or 0,            
            version=d['EventItemVersion'] or '',            
            agenda_note=d['EventItemAgendaNote'] or '',
            minutes_note=d['EventItemMinutesNote'] or '',
            action_id=d['EventItemActionId'],
            passed_flag=d['EventItemPassedFlag'] or 0,
            passed_flag_name=d['EventItemPassedFlagName'] or '',
            roll_call_flag=d['EventItemRollCallFlag'] or 0,
            flag_extra=d['EventItemFlagExtra'] or 0,
            title=d['EventItemTitle'] or '',
            tally=d['EventItemTally'] or '',
            consent=d['EventItemConsent'] or 0,
            mover_id=d['EventItemMoverId'],
            seconder_id=d['EventItemSeconderId'],
            matter_id=d['EventItemMatterId'])
    
    
    
    