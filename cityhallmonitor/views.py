from django.conf import settings
from django.shortcuts import render
from documentcloud import DocumentCloud
from cityhallmonitor.models import Matter, MatterAttachment


def search(request):
    return render(request, 'search.html', context={})
    
    
def documents(request, id):
    """View MatterAttachment"""
    try:    
        matter_attachment = MatterAttachment.objects.get(pk=id) 
        
        client = DocumentCloud()
        r = client.documents.search('account:%s source: "%s"' % (
            settings.DOCUMENT_CLOUD_ACCOUNT, 
            matter_attachment.hyperlink
        ))
        
        if not r:
            raise Exception(
                'Could not find document in DocumentCloud for "%s"' % \
                matter_attachment.hyperlink)
        if len(r) > 1:
            raise Exception(
                'Multiple instances exist in DocumentCloud for "%s"' % \
                matter_attachment.hyperlink)
         
        return render(request, 'documents.html', context={
            'matter_attachment': matter_attachment,
            'doc': r[0]
        })
    except Exception as e:
        return render(request, 'documents.html', context={
            'error': str(e)
        })
