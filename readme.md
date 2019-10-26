Drop Message
============
API backend using REST and web sockets to allow clients to,
- 'Drop' short messages at a geolocation for others to pick up and read
- Pickup messages created by other people at the same location
- Upvote and downvote messages
- User accounts

When you drop a message, all connected clients in the same geolocation are notified and pick it up. Queries by category are paginated and cached. Call with next page number to get more data. No message duplicates within each geolocation block (lat,long) to 2 decimal places. Messages automatically deleted when they are downvoted below 0, or expire after 48 hours

[https://drop-messages.herokuapp.com/web/portal/](https://drop-messages.herokuapp.com/web/portal/)

Websocket API (JSON)
===============
CLIENT REQUEST
-------
WS endpoint: https://drop-messages.herokuapp.com/ws/\<lat\>,\<long\>/

e.g. Melbourne: https://drop-messages.herokuapp.com/ws/37.81,144.96/

|Description|category|data|token|lat|long|
|-----------|------|------|-----|---|----|
|Required First message (Authentication)|||JWT|
|Create message|0|"message"|
|Change geolocation|1|||-90.0 < x > 90.0|-180.0 < x > 180.0|
|Get top msg's|2|x >= 1|
|Get newest msgs's|3|x >= 1|
|Get random msgs's|4|x >= 1|
|Get msgs's within radius|5|x >= 1|||||
|Get my msg's|6|x >= 1|
|Upvote|7|message id|
|Downvote|8|message_id|
|Disconnect|9|

SERVER RESPONSE
---------
|API|category|data|
|---|--------|----|
|socket status info|"socket"|" "|
|response about information posting|"post"|" "|
|retrieved results|"retrieve"|" "|
|errors|"error"|" "|
|pushed notifications|"notification"|" "|

Rest API endpoints (POST)
===========
|API|username|password|email|token|RESPONSE|
|---|--------|--------|-----|-----|--------|
|/api/register|"username"|"password"|"email"||username, hash, email|
|/api/token|"username"|"password"|||JWT Token|
|/api/verify||||"JWT token"|code 400 or code 200|


Web Endpoints
===========
|API|Description|
|---|-----------|
|/web/portal|Web portal for testing stuff
|/web/register|Register a new account
|/web/login|Login
|/web/logout|Logout

User Authentication pattern
==============
1. Register a user account
2. Get JWT token from REST endpoint
3. Use JWT token to authenticate a websocket

Requirements
============
see requirements.txt
- django
- djangorestframework
- djangorestframework-jwt
- channels
- channels-redis
- redis
