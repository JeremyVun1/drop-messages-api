# websocket server consumer
# Jeremy vun 2726092

# websocket imports
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

# authentication imports
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError

from drop.custom_exceptions import TokenError
from .drfjwt.serializers import VerifyAuthTokenSerializer

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
            print(f"[SOCK]<ANON> opened")
            self.geoloc = None
        except Exception as e:
            self.send_message_to_client("error", str(e))
            self.close()

    # unsubscribe us from the layer group after we disconnect
    def disconnect(self, close_code):
        if self.geoloc:
            async_to_sync(self.channel_layer.group_discard)(
                self.geoloc.get_block_name(),
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
            json_data = json.loads(text_data)
            print(json_data)

            # user authentication
            if self.geoloc is None or self.scope["user"].id is None:
                try:
                    print(f">>[REC]<Anon>: {json_data}")

                    # parse the geolocation
                    self.geoloc = parse_geoloc(json_data["lat"], json_data["long"])
                    if self.geoloc is not None:
                        # authenticate the user
                        user = authenticate_token(json_data["token"])
                        self.scope["user"] = user

                        # user is authenticated with a valid geolocation
                        print(f"@[SOCK]<{user.username}> Opened @({self.geoloc.get_block_string()})")

                        # add user to a geoblock layer group
                        if self.geoloc and self.geoloc.is_valid():
                            async_to_sync(self.channel_layer.group_add)(
                                self.geoloc.get_block_name(),
                                self.channel_name
                            )
                            self.send_message_to_client("socket", "open")
                    else:
                        raise ValueError("Invalid Geolocation")
                except:
                    raise TokenError("Invalid Access Token")

            # user is authenticated, receive the client message and route based on category code
            else:
                print(f">>[REC][{self.scope['user'].username}]: {text_data}")
                code = json_data['category']

                # client wishes to close the socket
                if code == 9:
                    self.send_message_to_client("socket", "closed")
                    self.close()

                # create message
                if code == 0:
                    m = mf.create_message(geoloc=self.geoloc, message=parse_message(json_data['data']), user_id=self.scope["user"].id)
                    if m:
                        json_response = json.dumps({
                            "echo": serialize_message(m),
                            "result": True,
                            "meta": ""
                        })
                        self.send_message_to_client("post", json_response)
                        self.notify_geoloc_group(m)
                    else:
                        json_response = json.dumps({
                            "echo": serialize_message(m),
                            "result": False,
                            "meta": "duplicate"
                        })
                        self.send_message_to_client("post", json_response)

                # change geolocation
                elif code == 1:
                    new_geoloc = Geoloc(json_data['lat'], json_data['long'])
                    if new_geoloc.is_valid():
                        # leave current group
                        async_to_sync(self.channel_layer.group_discard)(
                            self.geoloc.get_block_string(),
                            self.channel_name
                        )

                        # join new group
                        self.geoloc = new_geoloc
                        async_to_sync(self.channel_layer.group_add)(
                            self.geoloc.get_block_string(),
                            self.channel_name
                        )

                        self.send_message_to_client("socket", f"{new_geoloc.get_block_string()}")
                    else:
                        self.send_message_to_client("socket", f"invalid location")

                # Upvote
                elif code == 7:
                    msg_id = int(json_data["data"])
                    votes = mf.upvote(msg_id)
                    if votes is None:
                        json_response = json.dumps({
                            "id": msg_id,
                            "success": False,
                            "meta": "Not found"
                        })
                        self.send_message_to_client("vote", json_response)
                    else:
                        json_response = json.dumps({
                            "id": msg_id,
                            "success": True,
                            "meta": str(votes)
                        })
                        self.send_message_to_client("vote", json_response)

                # Downvote
                elif code == 8:
                    msg_id = int(json_data["data"])
                    votes = mf.downvote(msg_id)
                    if votes is None:
                        json_response = json.dumps({
                            "id": msg_id,
                            "success": False,
                            "meta": "Not found"
                        })
                        self.send_message_to_client("vote", json_response)
                    else:
                        json_response = json.dumps({
                            "id": msg_id,
                            "success": True,
                            "meta": str(votes)
                        })
                        self.send_message_to_client("vote", json_response)

                # we already have a query set paginated, return the requested page instead of hitting DB
                else:
                    page_num = max(1, parse_int(json_data['page']))

                    if code == self.last_code and self.qs_cache:
                        if page_num > self.qs_cache.num_pages:
                            self.send_retrieved_messages([]) # send empty is emmpty
                        else:
                            self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages by vote ranking
                    elif code == 2:
                        self.qs_cache = mf.retrieve_messages_ranked(geoloc=self.geoloc)
                        self.last_code = 2
                        page_num = min(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Newest Messages
                    elif code == 3:
                        self.qs_cache = mf.retrieve_messages_new(geoloc=self.geoloc)
                        self.last_code = 3
                        page_num = min(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages sorted randomly
                    elif code == 4:
                        self.qs_cache = mf.retrieve_messages_random(geoloc=self.geoloc)
                        self.last_code = 4
                        page_num = min(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages within a lat/long area
                    elif code == 5:
                        self.qs_cache = mf.retrieve_messages_range(geoloc=self.geoloc, geoloc_range=parse_coord_range(json_data['data']))
                        self.last_code = 5
                        page_num = min(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

                    # Messages posted by the user
                    elif code == 6:
                        self.qs_cache = mf.retrieve_user_messages(self.scope["user"].id)
                        self.last_code = 6
                        page_num = min(page_num, self.qs_cache.num_pages)
                        self.send_retrieved_messages(self.qs_cache.page(page_num))

        # handle exceptions
        except Exception as e:
            if e is TokenError:
                self.send_message_to_client("token", f"{e}")
            else:
                self.send_message_to_client("error", f"{e}")

            self.close()

    # notify whole group of a new message
    def notify_geoloc_group(self, message):
        if message:
            self.notified_id = message.pk
            async_to_sync(self.channel_layer.group_send)(
                str(self.geoloc.get_block_string()),
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
        mf.update_seen(qs)

        if qs is not None:
            result = []
            for m in qs:
                m_json = serialize_message(m)
                if m_json:
                    result.append(m_json)
            self.send_message_to_client("retrieve", result)
        else:
            self.send_message_to_client("retrieve", "")

    # send a data frame to the client
    def send_message_to_client(self, category, data):
        if not isinstance(data, str):
            data = json.dumps(data)
        print(f"<<[SND][{self.scope['user'].username}]: cat: {category}, data: {data}")
        self.send(text_data=json.dumps({
            "category": category,
            "data": data
        }))


def authenticate_token(token):
    print("authenticating token...")
    try:
        valid_data = VerifyAuthTokenSerializer().validate({"token": token})
        return valid_data['user']
    except:
        raise TokenError("Invalid access token")



