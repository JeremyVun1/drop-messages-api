# facade for handling message data transactions and related logic
# Jeremy Vun 2726092

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from drop.models import Message
from drop.constants import DELETE_THRESH, PAGE_SIZE
from .util import Geoloc


def create_message(geoloc, message, user_id):
	try:
		if geoloc and geoloc.is_valid() and message:
			# check for duplicate messages at the same geolocation
			block = geoloc.get_block()
			qs = Message.objects.filter(lat_block=block.lat, long_block=block.long, message__iexact=message)

			if not qs.exists():
				user = User.objects.get(pk=user_id)  # get author
				m = Message(lat=geoloc.lat, long=geoloc.long, lat_block=block.lat, long_block=block.long, message=message, author=user)
				m.save()
				return m
		else:
			return None
	except:
		return None


# TODO - figure out how to page these queries
def retrieve_messages_ranked(geoloc):
	try:
		if geoloc and geoloc.is_valid():
			block = geoloc.get_block()
			qs = Message.objects.filter(lat_block=block.lat, long_block=block.long).order_by('-votes')
			return Paginator(qs, PAGE_SIZE)
		return None
	except:
		return None


def retrieve_messages_new(geoloc):
	try:
		if geoloc and geoloc.is_valid():
			block = geoloc.get_block()
			qs = Message.objects.filter(lat_block=block.lat, long_block=block.long).order_by('-date')
			return Paginator(qs, PAGE_SIZE)
		return None
	except:
		return None


def retrieve_messages_random(geoloc):
	try:
		if geoloc and geoloc.is_valid():
			block = geoloc.get_block()
			qs = Message.objects.filter(lat_block=block.lat, long_block=block.long).order_by('?')
			return Paginator(qs, PAGE_SIZE)
		return None
	except:
		return None


def retrieve_messages_range(geoloc, geoloc_range):
	try:
		if geoloc and geoloc.is_valid():
			block = geoloc.get_block()
			geoloc_min = Geoloc(block.lat - geoloc_range / 2, block.long - geoloc_range)
			geoloc_max = Geoloc(block.lat + geoloc_range / 2, block.long + geoloc_range)

			qs = Message.objects.filter(lat_block__lte=geoloc_max.lat, lat_block__gte=geoloc_min.lat, long_block__lte=geoloc_max.long, long_block__gte=geoloc_min.long)
			return Paginator(qs, PAGE_SIZE)
		return None
	except:
		return None


def retrieve_user_messages(user_id):
	try:
		if user_id and isinstance(user_id, int) and user_id >= 1:
			user = User.objects.get(pk=user_id)
			qs = Message.objects.filter(author=user)
			return Paginator(qs, PAGE_SIZE)
	except:
		return None


def upvote(id):
	try:
		m = Message.objects.get(pk=id)
		m.votes += 1
		m.save()
		return m.votes
	except:
		return None


def downvote(id):
	try:
		m = Message.objects.get(pk=id)
		m.votes -= 1
		if m.votes <= DELETE_THRESH:
			m.delete()
		else:
			m.save()
		return m.votes
	except:
		return None

# TEST
def update_seen(qs):
	pass
