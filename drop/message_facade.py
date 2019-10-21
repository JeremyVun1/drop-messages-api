# facade for handling message data transactions and related logic
# Jeremy Vun 2726092

from drop.models import Message
from drop.constants import DELETE_THRESH
from .util import Geoloc


def create_message(geoloc, message):
	if geoloc and geoloc.is_valid() and message:

		# check for duplicate messages at the same geolocation
		qs = Message.objects.filter(lat=geoloc.lat, long=geoloc.long, message=message)

		if not qs.exists():
			m = Message(lat=geoloc.lat, long=geoloc.long, message=message)
			m.save()
			return m
	else:
		return None


# TODO - figure out how to page these queries
def retrieve_messages_ranked(geoloc):
	if geoloc and geoloc.is_valid():
		qs = Message.objects.filter(lat=geoloc.lat, long=geoloc.long).order_by('-votes')
	return None


def retrieve_messages_new(geoloc):
	if geoloc and geoloc.is_valid():
		qs = Message.objects.filter(lat=geoloc.lat, long=geoloc.long).order_by('-date')
	return None


def retrieve_messages_random(geoloc):
	if geoloc and geoloc.is_valid():
		qs = Message.objects.filter(lat=geoloc.lat, long=geoloc.long).order_by('?')
	return None


def retrieve_messages_range(geoloc, geoloc_range):
	print("Retrieving by range")
	if geoloc and geoloc.is_valid():
		geoloc_min = Geoloc(geoloc.lat - geoloc_range / 2, geoloc.long - geoloc_range)
		geoloc_max = Geoloc(geoloc.lat + geoloc_range / 2, geoloc.long + geoloc_range)
		print(f"geoloc_min: {geoloc_min}")
		print(f"geoloc_max: {geoloc_max}")

		result = Message.objects.filter(lat__lte=geoloc_max.lat, lat__gte=geoloc_min.lat, long__lte=geoloc_max.long, long__gte=geoloc_min.long)
		return result
	return None


def upvote(id):
	m = Message.objects.get(pk=id)
	m.votes += 1
	m.save()
	return m.votes


def downvote(id):
	m = Message.objects.get(pk=id)
	m.votes -= 1
	if m.votes <= DELETE_THRESH:
		m.delete()
	else:
		m.save()
	return m.votes