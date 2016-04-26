from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Document
from cityhallmonitor.document_classifier.title_analysis import cleanTitle, classifyTitle
import random

class Command(BaseCommand):
	help = 'Adds a classification type to each document.'

	def handle(self, *args, **options):
		count = 0
		for doc in Document.objects.filter(classification__isnull=True).only('title'):
			count = count + 1
			doc.classification = classifyTitle(cleanTitle(doc.title))
			doc.save()
		print("Documents w/ Null Classications That Are Now Updated: " + str(count))
