from django.contrib import admin
from cityhallmonitor.models import \
    Action, Person, BodyType, Body, \
    MatterAttachment, MatterStatus, MatterType, Matter, \
    MatterSponsor, VoteType, Event, EventItem, Subscription
    

class ActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_flag', 'last_modified',)
    list_filter = ('active_flag',)
admin.site.register(Action, ActionAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'active_flag', 'last_modified')
    list_filter = ('active_flag',)
admin.site.register(Person, PersonAdmin)


class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified')    
admin.site.register(BodyType, BodyTypeAdmin)

class BodyAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_type', 'active_flag', 'last_modified')
    list_filter = ('active_flag',)    
admin.site.register(Body, BodyAdmin)

class MatterStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_flag', 'last_modified',)
    list_filter = ('active_flag',)
admin.site.register(MatterStatus, MatterStatusAdmin)

class MatterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_flag', 'last_modified',)
    list_filter = ('active_flag',)
admin.site.register(MatterType, MatterTypeAdmin)

class MatterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'matter_status', 'matter_type', 'intro_date', 'last_modified')
    list_filter = ('matter_status', 'matter_type')
    search_fields = ['name', 'title']
    # Hide unused fields in admin form
    exclude = (
        'date1', 'date2',
        'ex_text1', 'ex_text2', 'ex_text3', 'ex_text4', 'ex_text5',
        'ex_text6', 'ex_text7', 'ex_text8', 'ex_text9', 'ex_text10',
        'ex_date1', 'ex_date2', 'ex_date3', 'ex_date4', 'ex_date5',
        'ex_date6', 'ex_date7', 'ex_date8', 'ex_date9', 'ex_date10'
    )

admin.site.register(Matter, MatterAdmin)

class MatterAttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'hyperlink', 'link_obtained_at', 'matter')
admin.site.register(MatterAttachment, MatterAttachmentAdmin)

class MatterSponsorAdmin(admin.ModelAdmin):
    list_display = ('person', 'matter')
    list_filter = ('person',)

admin.site.register(MatterSponsor, MatterSponsorAdmin)

admin.site.register(VoteType)

class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'time', 'last_modified',)
    search_fields = ['body__name']
    ordering = ('-date', '-time')
admin.site.register(Event, EventAdmin)

admin.site.register(EventItem)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'query', 'last_check')
    search_fields = ('email', 'query')    
admin.site.register(Subscription, SubscriptionAdmin)

