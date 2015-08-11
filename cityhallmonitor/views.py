from django.shortcuts import render
from cityhallmonitor.models import Matter, MatterAttachment


def search(request):
    return render(request, 'search.html', context={})
    
    
def documents(request, id):
    """View MatterAttachment"""
    try:    
        matter_attachment = MatterAttachment.objects.get(pk=id) 
        
        return render(request, 'documents.html', context={
            'matter_attachment': matter_attachment
        })
    except Exception as e:
        return render(request, 'documents.html', context={
            'error': str(e)
        })
