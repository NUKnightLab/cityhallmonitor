from django.core.management.base import BaseCommand, CommandError
import os.path
from django.db import connection

class Command(BaseCommand):
    help = 'Import MatterType data from JSON file'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('path', nargs='?')

    def handle(self, *args, **options):
        path = './machinelearning/corpus'
        if options['path']:
            path = options['path']

        print("Extracting corpus to {}".format(os.path.realpath(path)))
        os.makedirs(path,exist_ok=True)
        cursor = connection.cursor()
        c2 = connection.cursor()
        # select * query including the text column hangs so iterate ids and select text individually
        cursor.execute('select matter_attachment_id, title from cityhallmonitor_document')
        for (i,(pk, title)) in enumerate(cursor):
            c2.execute("select text from cityhallmonitor_document where matter_attachment_id = %s" % pk)
            text = c2.fetchall()[0][0]
            self.dump_doc(pk, text, path)
            if i % 1000 == 0: print(i)
        c2.close()
        cursor.close()


    def dump_doc(self, pk, text, path):
        filename = '{}.txt'.format(pk)
        with open(os.path.join(path, filename),'w') as f:
            f.write(text)
