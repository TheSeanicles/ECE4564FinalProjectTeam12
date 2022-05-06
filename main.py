import socket
import time
from pymongo import MongoClient
import yaml
from twilio.rest import Client


# TWILIO FUNCTIONS
def create_contact(name, affiliation, phone_num, sms, voice):
    if isinstance(sms, bool) and isinstance(voice, bool):
        return {'username': name,
                'affiliation': affiliation,
                'phone_number': phone_num,
                'sms': sms,
                'voice': voice
                }
    else:
        return {'username': name,
                'affiliation': affiliation,
                'phone_number': phone_num,
                'sms': True,
                'voice': False
                }


def update_contact_info(contacts):
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['ECE4564_FinalProject']['users']
    query = col.find_one({'username': contacts['username']})
    if query is None:
        col.insert_one(contacts)
    else:
        update = {'$set': contacts}
        col.update_one(query, update)


def t_sms(msg):
    with open(r'config.yml') as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
    twilio_client = Client(conf['twilio']['account_sid'], conf['twilio']['auth_token'])
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['ECE4564_FinalProject']['users']
    users = col.find()
    for u in users:
        if u['sms']:
            message = twilio_client.messages.create(
                to=u['phone_number'],
                messaging_service_sid=conf['twilio']['msg_ssid'],
                body=msg
            )


def t_voice(msg):
    with open(r'config.yml') as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
    twilio_client = Client(conf['twilio']['account_sid'], conf['twilio']['auth_token'])
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['ECE4564_FinalProject']['users']
    users = col.find()
    for u in users:
        if u['sms']:
            call = twilio_client.calls.create(
                twiml=f'<Response><Say>{msg}</Say></Response>',
                to=u['phone_number'],
                from_=conf['twilio']['t_num']
            )


def send_alerts(msg):
    t_sms(msg)
    # Do not run the below function unless absolutely necessary as it cost money
    # t_voice(msg)


# END TWILIO FUNCTIONS


def main():
    update_contact_info(create_contact('Sean', 'ADMIN', '+15408558645', True, False))
    send_alerts('Ahoy, World!')


if __name__ == '__main__':
    main()
