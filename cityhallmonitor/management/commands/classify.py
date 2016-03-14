from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Document
import sys
sys.path.append(sys.path[0] + "/cityhallmonitor/document_classifier") 
from title_analysis import *
import random

class Command(BaseCommand):
	help = 'Adds a classification type to each document.'

	def handle(self, *args, **options):

		for doc in Document.objects.all():
			doc.classification = classifyTitle(cleanTitle(doc.title))
			doc.save()
