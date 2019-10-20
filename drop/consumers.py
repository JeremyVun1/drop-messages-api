# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class MessagesConsumer(WebsocketConsumer):
    def connect(self):
        # get the room name from keywords defined in url route
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # create a group name from the param
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                # type specifies the function to be called when received
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


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