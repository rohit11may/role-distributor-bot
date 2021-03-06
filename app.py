import os

import redis
from flask import Flask, request
from pymessenger.bot import Bot
from role_distributor import RoleDistributor

app = Flask(__name__, static_url_path='', static_folder='')
r = redis.from_url(os.environ.get("REDIS_URL"))
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

bot = Bot(ACCESS_TOKEN)
rd = RoleDistributor(r)


@app.route("/privacypolicy", methods=['GET', 'POST'])
def privacy_policy():
    return app.send_static_file('privacypolicy.html')


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response = rd.handleMsg(message)
                        send_message(recipient_id, response['message'])
                        if response['ownerNotif'] and response['ownerId']:
                            send_message(response['ownerId'], response['ownerNotif'])

                        if response['roles']:
                            for memberId, role in response['roles']:
                                send_message(memberId, f"You are {role}!")
                            send_message(response['ownerId'], "Roles distributed!")

    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    # app.run(debug=True)
    k = "Hello"
    v = "World"
    print(r.mset({k: v}))
    print(r.delete("Hello"))
    print(r.exists(k))