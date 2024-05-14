# sensu-sympony-handler
symphony chat handler for sensu-go monitoring

symphony chat handler allows you to send notifications from sensu directly to symphony chat room.
Handler is a simple python3 script which read sensu event json and send message to symphony chat room.

To authorize you need provide ssh-key or already generated jwt token (one of these).
In case of ssh-key, script will generate jwt token and store it in the same directory
(so sensu-backend should be able to write there)

From time to time script will regenerate expired jwt token.

You can modify script on your own, if you want to change path/authorization/message format


# How to install
1. Put symphony-handler.py to your handlers assets
2. Edit and apply sensu-handler-example.yaml using sensuctl
	sensuctl --namespace <ENV> -f sensu-handler-example.yaml
3. Create check with symphony-handler handler and test connectivity.
    You can also manually send event JSON to symphony-handler.py
    By default is_incident filter is enabled for handler, so don't forget
    that check should generate erorr or warning to send action to handler script.
4. Troubleshot:
   Uncomment debug print line at the end of symphony-handler.py - 
    Script will generate curl command to send notification.
    Play with curl command to debug what is going wrong.


Sergii Kulyk (https://github.com/sfkulyk)