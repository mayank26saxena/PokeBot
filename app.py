import os
import sys
import time
from skiplagged import Skiplagged
import requests
import json
from random import randint
from pygeocoder import Geocoder
from flask import Flask, request

app = Flask(__name__)

i = 0

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello Mayank!", 200


@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events
    b = False
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    if messaging_event.get("message").get("text"):
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                        try :
                            message_text = messaging_event["message"]["text"]  # the message's text
                            #send_message(sender_id, message_text)
                            message_text = message_text.lower()
                            if message_text == "hi" or message_text == "hello" or message_text == "hey" or message_text == "start" or message_text == "begin" or message_text == "yo" or message_text == "help" or message_text == "pokebot" or message_text == "pokemon go" :
                                send_message(sender_id, "PokeBot will help you find Pokemons near you. Send your location to get started!")
                            else:
                                send_message(sender_id, "Unrecognized keyword. Please send your location to find nearby Pokemons.")
                        except:
                            log("error, no text")

                        #send_message(sender_id, "got it, thanks!")

                    if messaging_event.get("message").get("attachments"): # someone sent us an attachment
                        log("Message has an attachment")
                        sender_id = messaging_event["sender"]["id"]
                        if messaging_event["message"]["attachments"][0]["type"] == "location" :
                            recipient_id = messaging_event["recipient"]["id"]
                            lat = messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["lat"]
                            lng = messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["long"]

                            #send_message(sender_id, lat)
                            #send_message(sender_id, lng)

                            # Convert longitude and latitude to a location
                            address = Geocoder.reverse_geocode(lat,lng)
                            log(str(address))

                            if ( b == False):
                               # address_message = "Pokemons near " + str(address) + " are - "
                               # send_message(sender_id, str(address_message))
                                b = True

                            login(str(address),sender_id )


                        else:
                            send_message(sender_id, "Attachment is not of type location")
                            log("Attachment is not of type location")
                            pass

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

                pass

    return "ok", 200

def login(address, sender_id):
    while 1:
        try:
            client = Skiplagged()
            bounds = client.get_bounds_for_address(address)

            usernames = ["prattylolo2", "prattylolo3", "prattylolo4", "prattylolo5", "prattylolo6"]
            passwords = ["prattylolo2", "prattylolo3", "prattylolo4", "prattylolo5", "prattylolo6"]

            n = randint(0, 4)

            username = usernames[n]
            password = passwords[n]

            log("username = " + str(username))
            log("password = " + str(password))


            print client.login_with_pokemon_trainer(username, password)
            print client.get_specific_api_endpoint()
            print client.get_profile()

            address_message = "Pokemons near " + str(address) + " are - "
            send_message(sender_id, str(address_message))

            for pokemon in client.find_pokemon(bounds):
                #send_message(sender_id, str(pokemon))
                s = str(pokemon)
                index_of_colon = s.index(":")
                list_of_commas = find(s, ",")
                index_of_comma = list_of_commas[-1]
                s1 = s[:index_of_colon]
                s2 = s[index_of_comma:]
                s3 = s1+s2
                send_message(sender_id, s3)
                global i
                i += 1
                if i == 5 :
                    return

        except Exception as e:
            log("Exception: {0} {1}".format(e.message, e.args))
            time.sleep(1)


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
