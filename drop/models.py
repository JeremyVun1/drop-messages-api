# Message model
# Jeremy Vun 2726092

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from .constants import MAX_MESSAGE_LENGTH


class Message(models.Model):
	lat = models.FloatField()
	long = models.FloatField()
	lat_block = models.FloatField()
	long_block = models.FloatField()
	message = models.CharField(max_length=MAX_MESSAGE_LENGTH)
	date = models.DateTimeField(default=now)
	votes = models.IntegerField(default=1)
	seen = models.IntegerField(default=0)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return f"({self.lat},{self.long}) - {self.message} [{self.votes}]"
