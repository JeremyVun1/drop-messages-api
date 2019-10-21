# Message model
# Jeremy Vun 2726092

from django.db import models
from django.utils.timezone import now


class Message(models.Model):
	lat = models.FloatField()
	long = models.FloatField()
	message = models.CharField(max_length=140)
	date = models.DateTimeField(default=now)
	votes = models.IntegerField(default=1)
	# user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return f"({self.lat},{self.long}) - {self.message} [{self.votes}]"
