# websocket server consumer
# Jeremy vun 2726092

# websocket imports
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

# authentication imports
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError

# business imports
from .util import *
from drop import message_facade as mf


class MessagesConsumer(WebsocketConsumer):
    notified_id = 0
    last_code = None
    qs_cache = None

    # don't need to authenticate to connect, only when requesting data
    def connect(self):
        self.accept()
        try:
            # bind consumer instance to a geolocation
            self.geoloc = parse_geoloc(self.scope['url_route']['kwargs']['geoloc'])
            if self.geoloc is None:
                raise ValueError("Invalid Geolocation")

            print(f"[SOCKET] Opened @[{self.geoloc}]")
            if self.geoloc and self.geoloc.is_valid():
                async_to_sync(self.channel_layer.group_add)(
                    str(self.geoloc),
                    self.channel_name
                )
                self.send_message_to_client("socket", "Socket is open!")
        except Exception as e:
            self.send_message_to_client("error", str(e))
            self.close()

    # unsubscribe us from the layer group after we disconnect
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            str(self.geoloc),
            self.channel_name
        )

    # Route client request according to category code
    # 0. post message
    # 1. retrieve ranked messages
    # 2. retrieve new messages
    # 3. retrieve random messages
    # 4. retrieve messages in range
    # noinspection PyMethodOverriding
    def receive(self, text_data):
        try:
            if self.geoloc is None:
                return

            json_data = json.loads(text_data)

            # user authentication
            if self.scope["user"].id is None:
                try:
                    user = authenticate_token(json_data)
                    self.scope["user"] = user
                    self.send_message_to_client("socket", f"Authenticated successfully as {user.username}")
                except:
                    raise ValidationError("Invalid Access Token")

            # user is authenticated, receive the client message and route based on category code
            else:
                print(f"[RECEIVED]: {text_data}")
                code = json_data['category']

                # create message
                if code == 0:
                    m = mf.create_message(geoloc=self.geoloc, message=parse_message(json_data['data']), user_id=self.scope["user"].id)
                    if m:
                        self.send_message_to_client("post", f"message created: {m}")
                        self.notify_geoloc_group(m)
                    else:
                        self.send_message_to_client("error", f"duplicate message found!")

                # change geolocation
                elif code == 1:
                    new_geoloc = Geoloc(json_data['lat'], json_data['long'])
                    if new_geoloc.is_valid():
                        self.geoloc = new_geoloc
                        self.send_message_to_client("socket", f"Changed Geolocation to ({new_geoloc.lat},{new_geoloc.long})")
                    else:
                        self.send_message_to_client("error", f"Cannot change to invalid geolocation")

                # we already have a query set paginated, return the requested page instead of hitting DB
                else:
                    page_num = max(1, json_data['page'])

                    if code == self.last_code and self.qs_cache:
                        page_num = max(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages by vote ranking
                    elif code == 2:
                        self.qs_cache = mf.retrieve_messages_ranked(geoloc=self.geoloc)
                        self.last_code = 1
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Newest Messages
                    elif code == 3:
                        self.qs_cache = mf.retrieve_messages_new(geoloc=self.geoloc)
                        self.last_code = 2
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages sorted randomly
                    elif code == 4:
                        self.qs_cache = mf.retrieve_messages_random(geoloc=self.geoloc)
                        self.last_code = 3
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages within a lat/long area
                    elif code == 5:
                        self.qs_cache = mf.retrieve_messages_range(geoloc=self.geoloc, geoloc_range=parse_coord_range(json_data['range']))
                        self.last_code = 4
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

        # handle exceptions
        except ValidationError as v:
            self.send_message_to_client("error", f"{v}")
            self.close()
        except Exception as e:
            self.send_message_to_client("error", "error encountered")

    # notify whole group of a new message
    def notify_geoloc_group(self, message):
        if message:
            self.notified_id = message.pk
            async_to_sync(self.channel_layer.group_send)(
                str(self.geoloc),
                {
                    # type specifies the function to be called when received
                    'type': 'receive_notification',
                    'id': message.pk
                }
            )

    # handle receiving a new message
    def receive_notification(self, event):
        id = event['id']
        if self.notified_id == id:
            notified_id = 0
            return

        m = Message.objects.get(pk=id)
        self.send_message_to_client("notify", serialize_message(m))

    # send message query set back to the client
    def send_retrieved_messages(self, qs):
        if qs is not None:
            result = []
            for m in qs:
                m_json = serialize_message(m)
                if m_json:
                    result.append(m_json)
            self.send_message_to_client("retrieve", result)
        else:
            self.send_message_to_client("retrieve", {})

    # send a data frame to the client
    def send_message_to_client(self, category, data):
        print(f"[SEND] category: {category}, data: {data}")
        self.send(text_data=json.dumps({
            "category": category,
            "data": data
        }))


def authenticate_token(json_data):
    try:
        token = json_data['token']
        valid_data = VerifyAuthTokenSerializer().validate({"token": token})
        return valid_data['user']
    except:
        raise ValidationError("Invalid access token")