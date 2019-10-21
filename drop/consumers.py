# websocket server consumer
# Jeremy vun 2726092

# websocket imports
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

# authentication imports
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.serializers import VerifyAuthTokenSerializer

# business imports
from .util import *
from drop import message_facade as mf


class MessagesConsumer(WebsocketConsumer):
    notified_id = 0

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

            # check authentication here
            if self.scope["user"].id is None:
                user = authenticate_token(json_data)
                self.scope["user"] = user
                self.send_message_to_client("socket", f"Authenticated successfully as {user.username}")

            # user is authenticated already, receive messages and route them as normal
            else:
                print(f"[RECEIVED]: {text_data}")
                code = json_data['category']
                if code == 0:
                    m = mf.create_message(geoloc=self.geoloc, message=parse_message(json_data['data']))
                    self.send_message_to_client("post", f"message created: {m}")
                    self.notify_geoloc_group(m)
                elif code == 1:
                    qs = mf.retrieve_messages_ranked(geoloc=self.geoloc)
                    self.send_retrieved_messages(qs)
                elif code == 2:
                    qs = mf.retrieve_messages_new(geoloc=self.geoloc)
                    self.send_retrieved_messages(qs)
                elif code == 3:
                    qs = mf.retrieve_messages_random(geoloc=self.geoloc)
                    self.send_retrieved_messages(qs)
                elif code == 4:
                    qs = mf.retrieve_messages_range(geoloc=self.geoloc, geoloc_range=parse_coord_range(json_data['range']))
                    self.send_retrieved_messages(qs)
        except ValidationError as v:
            self.send_message_to_client("error", "Invalid Access Token")
            self.close()
        except Exception as e:
            self.send_message_to_client("error", "error encountered, socket closed")
            self.close()

    def notify_geoloc_group(self, message):
        if message:
            self.notified_id = message.pk
            async_to_sync(self.channel_layer.group_send)(
                str(self.geoloc),
                {
                    # type specifies the function to be called when received
                    'type': 'receive_new_message',
                    'id': message.pk
                }
            )

    def receive_new_message(self, event):
        id = event['id']
        if self.notified_id == id:
            notified_id = 0
            return

        m = Message.objects.get(pk=id)
        self.send_message_to_client("notification", serialize_message(m))

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
'''
AUTH
channels.auth.login
channels.auth.logout

login(scope, user, backend=None)
scope must have the user's session

TOKENS
customer middleware to intercept http headers, check if authorization exists in header
{
    authorization: ['Token', token_key]
} 

LOOK INTO JWT
single auth
- check if user in the scope = authenticated
- if no user, try get a token and auth

def receive(self, text_data=None, bytes_data=None):
    if self.scope['user'].id:
        pass
    else:
        try:
            # It means user is not authenticated yet.
            data = json.loads(text_data)
            if 'token' in data.keys():
                token = data['token']
                user = fetch_user_from_token(token)
                self.scope['user'] = user
                
        except Exception as e:
            # Data is not valid, so close it.
            print(e)
            pass

    if not self.scope['user'].id:
        self.close()
'''