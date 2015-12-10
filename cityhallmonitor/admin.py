from django.contrib import admin
from django.db.models import F
from cityhallmonitor.models import \
    Person, BodyType, Body, \
    MatterAttachment, MatterStatus, MatterType, Matter, \
    MatterSponsor, Subscription, Document
    

class DirtyFieldsAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at',)


class PersonAdmin(DirtyFieldsAdmin):
    list_display = ('last_name', 'first_name', 'active_flag', 'last_modified')
    list_filter = ('active_flag',)
admin.site.register(Person, PersonAdmin)


class BodyTypeAdmin(DirtyFieldsAdmin):
    list_display = ('name', 'last_modified')    
admin.site.register(BodyType, BodyTypeAdmin)


class BodyAdmin(DirtyFieldsAdmin):
    list_display = ('name', 'body_type', 'active_flag', 'last_modified')
    list_filter = ('active_flag',)    
admin.site.register(Body, BodyAdmin)


class MatterStatusAdmin(DirtyFieldsAdmin):
    list_display = ('name', 'active_flag', 'last_modified',)
    list_filter = ('active_flag',)
admin.site.register(MatterStatus, MatterStatusAdmin)


class MatterTypeAdmin(DirtyFieldsAdmin):
    list_display = ('name', 'active_flag', 'last_modified',)
    list_filter = ('active_flag',)
admin.site.register(MatterType, MatterTypeAdmin)


class MatterAdmin(DirtyFieldsAdmin):
    list_display = ('display_val', 'matter_status', 'matter_type', 'intro_date', 'last_modified')
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
    
    def get_queryset(self, request):
        """
        Annotate queryset with value of __str__, so we can sort on it.
        """
        qs = super(MatterAdmin, self).get_queryset(request)
        return qs.annotate(display_str=(F('title') or F('name') or F('file')))
    
    def display_val(self, obj):
        return obj.display_str
    display_val.admin_order_field = 'display_str'
    display_val.short_description = 'Matter'

admin.site.register(Matter, MatterAdmin)


class MatterAttachmentAdmin(DirtyFieldsAdmin):
    list_display = ('name', 'hyperlink', 'link_obtained_at', 'matter')
    search_fields = ('matter__id',)
admin.site.register(MatterAttachment, MatterAttachmentAdmin)


class MatterSponsorAdmin(DirtyFieldsAdmin):
    list_display = ('person', 'matter')
    list_filter = ('person',)

admin.site.register(MatterSponsor, MatterSponsorAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'query', 'last_check', 'active')
    search_fields = ('email', 'query')    
admin.site.register(Subscription, SubscriptionAdmin)


class DocumentAdmin(DirtyFieldsAdmin):
    list_display = ('sort_date', '__str__', 'is_routine',)
    list_display_links = ('__str__',)
    list_filter = ('is_routine',)
    
   
    # Hide unused fields in admin form
    exclude = (
        'matter_attachment',
    )
admin.site.register(Document, DocumentAdmin)