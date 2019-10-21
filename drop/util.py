# utility functions
# Jeremy Vun 2726092

from drop.models import Message
from .constants import GEOLOC_RESOLUTION, MAX_MESSAGE_LENGTH, MAX_RANGE


class Geoloc:
	def __init__(self, lat, long):
		self.lat = lat
		self.long = long

	def is_valid(self):
		return isinstance(self.lat, float) and isinstance(self.long, float)\
			   and -90 <= self.lat <= 90 and 180 >= self.long >= -180

	def __str__(self):
		return f"{round(self.lat, GEOLOC_RESOLUTION)}-{round(self.long, GEOLOC_RESOLUTION)}"


# lat,long
def parse_geoloc(geoloc_str):
	try:
		geoloc = geoloc_str.split(',')
		if len(geoloc) != 2:
			return None

		geoloc = Geoloc(
			round(float(geoloc[0]), GEOLOC_RESOLUTION),
			round(float(geoloc[1]), GEOLOC_RESOLUTION)
		)

		if geoloc.is_valid():
			return geoloc
		else:
			return None
	except ValueError:
		return None


def parse_message(m):
	if isinstance(m, str):
		if len(m) > MAX_MESSAGE_LENGTH:
			return m[:MAX_MESSAGE_LENGTH]
		return m
	return None


# serialize message into json
def serialize_message(m):
	if isinstance(m, Message):
		result = {
			"id": m.pk,
			"lat": m.lat,
			"long": m.long,
			"date": m.date.strftime("%d/%m/%Y"),
			"message": m.message,
			"votes": m.votes
		}
		print(result) # TODO testing print
		return result
	return None


def parse_coord_range(coord_range):
	try:
		result = round(float(coord_range), GEOLOC_RESOLUTION)
		if result < 0:
			result = 0
		elif result > MAX_RANGE:
			result = MAX_RANGE
		return result
	except ValueError:
		return 0.0
