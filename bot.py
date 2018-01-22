import sqlite3 
import sys
from flask import Flask, request
import os
import sys
import json
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])

def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hi James!", 200


def webhook():
	   if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    chatID = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message = messaging_event["message"]  # the message's text

                    run_app(chatID, message)
                 
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

		return "ok", 200

## Functions below

def run_app(chatID, message):

	if returnVisitor(chatID):
		startChatSession(chatID, message)

	else:
		collectData(chatID)
		runApp(chatID, message)

def startChatSession(chatID, message):
	if hasBuddy(chatID):
		buddyData = hasBuddy(chatID)
		buddyID = buddyData[0]
		if message['type'] == 'text':
			send_text(buddyID, message["message"]["text"])
		elif message['type'] == 'photo':
			send_photo(buddyID, message["message"]["text"])
		elif message['type'] == 'video':
			send_video(buddyID, message["message"]["text"])
		elif message['type'] == 'link':
			send_link(buddyID, message["message"]["text"])

	else:
		getBuddy(chatID)
		startChatSession(chatID, buddyID)

def returnVisitor(chatID):
	## checks database for entry with proper chatID
	db = sqlite3.connect("db.db")
	cursor = db.cursor()

	cursor.execute('''SELECT chatID FROM userdb''')
	idList = cursor.fetchall()
	db.close()

	if chatID in idList:
		return true
	else:
		return false



def collectData(chatid):


def hasBuddy(chatID):
	## TODO check database for existing buddy, return ID

	db = sqlite3.connect("db.db")
	cursor = db.cursor()

	cursor.execute('''SELECT buddyID FROM userdb WHERE chatID = (?)''', (chatID))
	idlist = cursor.fetchall()
	db.close()

	if idList[0] and not idList[0].isspace()
		return idList[0]
	else:
		return false


def getBuddy(chatID):
	## TODO matches friends to furthest existing non-matched match
	while not hasBuddy:
		sleep(1)

def send_link(buddyID, link_url):
	## TODO sends link

def send_image(buddyID, image_url):
	## TODO sends image

def send_text(buddyID, text):

    log("sending message to {recipient}: {text}".format(recipient=buddyID, text=text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": buddyID
        },
        "message": {
           
           "text": text

        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_video(buddyID, buddyAuth, video_url):


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)

