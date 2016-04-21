from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Document
from cityhallmonitor.document_classifier.title_analysis import cleanTitle, classifyTitle
import random

class Command(BaseCommand):
	help = 'Adds a classification type to each document.'

	def handle(self, *args, **options):
		count = 0
		while True:
			count = count + 1
			docs = Document.objects.filter(classification__isnull=True)[:1]
			doc = docs[0]
			if(doc):
				doc.classification = classifyTitle(cleanTitle(doc.title))
				doc.save()
			else:
				break
			if (count%1000 == 0):
				print("Total Documents Classified: {}".format(count))
		print("Classification Null: " + str(count))
		
