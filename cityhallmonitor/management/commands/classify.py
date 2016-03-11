from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Document
import random

# class Document(DirtyFieldsModel):
#     """
#     This is what we actually search on.
#     """
#     matter_attachment = models.OneToOneField(MatterAttachment, primary_key=True)
#     sort_date = models.DateTimeField(null=True)
#     text = models.TextField(blank=True)
#     title = models.TextField(blank=True)
#     sponsors = models.TextField(blank=True)
#     text_vector = TsVectorField()
#     text_vector_weighted = TsVectorField()
#     is_routine = models.BooleanField(default=False)

class Command(BaseCommand):
	help = 'Adds a classification type to each document.'

	def handle(self, *args, **options):
		wordChoices = ["Transportation", "Claims", "Exemptions", "Permits", "License", "Tax"]

		for doc in Document.objects.all():
			doc.classification = random.choice(wordChoices)
			doc.save()
