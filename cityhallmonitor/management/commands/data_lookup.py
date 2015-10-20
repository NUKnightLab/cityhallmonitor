from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import pprint
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud
from smtplib import SMTPException


DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT

DEFAULT_PROJECT = 'Chicago City Hall Monitor'


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect 
    def removed(self):
        return self.set_past - self.intersect 
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


class Command(BaseCommand):
    help = 'Lookup record by id or hyperlink/source and compare with DocumentCloud'
    
    _client = None

    def client(self):
        """Using un-authenticated client..."""
        if self._client is None:
            self._client = DocumentCloud()
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('id_or_url', help='id or url to check')

    def search(self, query):
        """Search document cloud and verify response type"""
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r

    def attachment_data(self, attachment):
        """
        Return attachment data
        """
        matter = attachment.matter
        sort_date = max([d for d in [
                matter.intro_date, 
                matter.agenda_date, 
                matter.passed_date, 
                matter.enactment_date] if d is not None], default=None)
        data = {
            'MatterAttachmentId': str(attachment.id),
            'MatterId': str(matter.id),
            'MatterFile': matter.file,
            'MatterName': matter.name,
            'MatterTitle': matter.title,
            'MatterType': matter.matter_type.name,
            'MatterStatus': matter.matter_status.name,
            'MatterIntroDate': str(matter.intro_date),
            'MatterAgendaDate': str(matter.agenda_date),
            'MatterPassedDate': str(matter.passed_date),
            'MatterEnactmentDate': str(matter.enactment_date),
            'MatterEnactmentNumber': str(matter.enactment_number),
            'MatterRequester': matter.requester,
            'MatterNotes': matter.notes,
            'MatterSortDate': str(sort_date)
        }   
        return data     
        
    def doc_data(self, doc, key_list=None):
        """
        Return document data
        """
        if key_list:
            return {k:doc.data.get(k) for k in key_list}           
        return {k:v for k,v in doc.data.items() if k != 'ops:DescriptionProcessed'}
 
 
    def compare_data(self, attachment, doc):
        """
        Compare attachment and DocumentCloud doc
        """
        print('- source', doc.source)
        print('- created_at', doc.created_at)
        print('- updated_at', doc.updated_at)
        
        att_data = self.attachment_data(attachment)
        doc_data = self.doc_data(doc, key_list=att_data.keys())
        
        dd = DictDiffer(att_data, doc_data)
        print('* data added:', dd.added())
        print('* data removed:', dd.removed())
        print('* data changed:', dd.changed())
       
                                            
    def compare_docs(self, doc1, doc2):
        """
        Compare two DocumentCloud documents
        """        
        print('Document 1')
        print('- source', doc1.source)
        print('- created_at', doc1.created_at)
        print('- updated_at', doc1.created_at)

        print('Document 2')
        print('- source', doc2.source)
        print('- created_at', doc2.created_at)
        print('- updated_at', doc2.created_at)
       
        dd = DictDiffer(doc1.data, doc2.data)
        print('* data added:', dd.added())
        print('* data removed:', dd.removed())
        print('* data changed:', dd.changed())
        
        if doc1.full_text == doc2.full_text:
            print('* full_text is SAME')
        else:
            print('* full_text is DIFFERENT')
                                                                                 
    def handle(self, *args, **options):
        try:
            id = 0
            url = ''
            query_list = []
            
            try:
                id = int(options['id_or_url'])
            except ValueError:
                url = options['id_or_url']
                      
            if id:
                query_list.append('MatterAttachmentId:%d' % id)
                
                try:
                    attachment = MatterAttachment.objects.get(id=id)
                    query_list.append('source: "%s"' % attachment.hyperlink)
                   
                    print('\nDatabase record')
                    print('- hyperlink', attachment.hyperlink) 
                    print('- last_modified', attachment.last_modified) 
                    print('- link_obtained_at', attachment.link_obtained_at)                    
                    print('- matter.id', attachment.matter.id)
                    print('- matter.last_modified', attachment.matter.last_modified)
                    print('- matter.attachments_obtained_at', attachment.matter.attachments_obtained_at)
                except MatterAttachment.DoesNotExist:
                    print('\nMatterAttachment does not exist in database')
            else:
                query_list.append('source: "%s"' % url)
                
                try:
                    attachment = MatterAttachment.objects.get(hyperlink=url)
                    query_list.append('MatterAttachmentId:%d' % attachment.id)
                    
                    print('\nDatabase record')
                    print('- id', attachment.id) 
                    print('- last_modified', attachment.last_modified) 
                    print('- link_obtained_at', attachment.link_obtained_at) 
                    print('- matter.id', attachment.matter.id)
                    print('- matter.last_modified', attachment.matter.last_modified)
                    print('- matter.attachments_obtained_at', attachment.matter.attachments_obtained_at)
                except MatterAttachment.DoesNotExist:
                    print('\nMatterAttachment does not exist in database')
                          
            for q in query_list:  
                print('\nQuerying DocumentCloud [%s]' % q)
                
                r = self.search('account:%s %s' % (DOCUMENT_CLOUD_ACCOUNT, q))    
                if not r:
                    print('NOT FOUND')
                elif len(r) > 1:
                    print('MULTIPLE FOUND [%d]' % len(r))
                    self.compare_docs(r[1], r[0])
                else:
                    if attachment:
                        self.compare_data(attachment, r[0])
               
            print('')              
        except Exception as e:
            print(e)