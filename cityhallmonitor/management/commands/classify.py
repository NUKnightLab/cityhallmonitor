from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Document
from cityhallmonitor.document_classifier.title_analysis import cleanTitle, classifyTitle
import random

class Command(BaseCommand):
	help = 'Adds a classification type to each document.'

	def handle(self, *args, **options):

		for doc in Document.objects.all():
			doc.classification = classifyTitle(cleanTitle(doc.title))
			doc.save()
