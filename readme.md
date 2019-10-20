Drop message
============
- Create messages and drop them at a location
- Pickup messages created by other people at the same location
- Upvote and downvote messages
- Messages are deleted when they are
    1. Downvoted below 0
    2. Expire

Websocket API
===============
1. Create message
2. Get messages (paged)


Lazy Loading data flow
==================
- ws socket keeps updated messages in pagination
- deliver next page
- delivered pages cached on mobile


Notifications
===============
- Long polling option?

Users
=============
- POST registration
- websocket login