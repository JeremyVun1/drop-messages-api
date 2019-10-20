from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import drop.routing

# route connections based on protocol type
application = ProtocolTypeRouter({
	# (http->django views routing is added by default)

	# route websocket->drop/routing.py
	# authmiddlewarestack populations connection's scope with authenticated user info
	'websocket': AuthMiddlewareStack(
		URLRouter(
			drop.routing.websocket_urlpatterns
		)
	),
})