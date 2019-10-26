# utility functions
# Jeremy Vun 2726092

from drop.models import Message
from .constants import GEOLOC_RESOLUTION, MAX_MESSAGE_LENGTH, MAX_RANGE


class Geoloc:
	def __init__(self, lat, long):
		self.lat = float(lat)
		self.long = float(long)

	def is_valid(self):
		return -90 <= self.lat <= 90 and 180 >= self.long >= -180

	def get_block(self):
		return Geoloc(
			round(self.lat, GEOLOC_RESOLUTION),
			round(self.long, GEOLOC_RESOLUTION)
		)

	def get_block_string(self):
		return str(self.getBlock)

	def __str__(self):
		return f"{round(self.lat, GEOLOC_RESOLUTION)},{round(self.long, GEOLOC_RESOLUTION)}"


# lat,long
def parse_geoloc(geoloc_str):
	try:
		print(f"parging geoloc string: {geoloc_str}")
		geoloc = geoloc_str.split(',')
		print(f"parsed: {geoloc}")
		if len(geoloc) != 2:
			return None

		geoloc = Geoloc(geoloc[0], geoloc[1])

		if geoloc.is_valid():
			return geoloc
		else:
			print("geoloc not valid")
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
			"votes": m.votes,
			"seen": m.seen
		}
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


def parse_int(x):
	try:
		result = int(x)
		return result
	except:
		return 0
