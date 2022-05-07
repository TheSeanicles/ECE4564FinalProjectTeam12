import socket
import datetime
import time
import multiprocessing
import random
from pymongo import MongoClient
import yaml
from twilio.rest import Client
import numpy as np


# MONGODB HR FUNCTIONS
def hr_update(t, usr, hr):
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['User_Heartrate']['u_hr']
    start_dict = {'timestamp': t,
                  'metadata': usr,
                  'hr': hr}
    col.insert_one(start_dict)
    detect_emergency()


def hr_grab(t_select):
    thresh = get_thresh(t_select)
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['User_Heartrate']['u_hr']
    return_dict = {}
    for t in col.find():
        if t['timestamp'] >= thresh:
            return_dict.update({t['_id']: t})
    return return_dict


def get_thresh(t_select):
    if t_select == 'min':
        thresh = datetime.datetime.now() - datetime.timedelta(minutes=1)
    elif t_select == '5min':
        thresh = datetime.datetime.now() - datetime.timedelta(minutes=5)
    elif t_select == '30min':
        thresh = datetime.datetime.now() - datetime.timedelta(minutes=30)
    elif t_select == 'hour':
        thresh = datetime.datetime.now() - datetime.timedelta(hours=1)
    elif t_select == '3hour':
        thresh = datetime.datetime.now() - datetime.timedelta(hours=3)
    elif t_select == '6hour':
        thresh = datetime.datetime.now() - datetime.timedelta(hours=6)
    elif t_select == '24hour':
        thresh = datetime.datetime.now() - datetime.timedelta(hours=24)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=2)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=3)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=4)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=5)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=6)
    elif t_select == '2day':
        thresh = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        # Defaults to 1 hour
        thresh = datetime.datetime.now() - datetime.timedelta(hours=1)
    return thresh


# END MONGODB HR FUNCTIONS

# CONTACT INFO MONGODB FUNCTIONS

def create_contact(name, affiliation, phone_num, addy, sms, voice):
    if isinstance(sms, bool) and isinstance(voice, bool):
        return {'username': name,
                'affiliation': affiliation,
                'phone_number': phone_num,
                'address': addy,
                'sms': sms,
                'voice': voice
                }
    else:
        return {'username': name,
                'affiliation': affiliation,
                'phone_number': phone_num,
                'address': addy,
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


def get_user_name():
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['ECE4564_FinalProject']['users']
    users = col.find()
    for u in users:
        if u['affiliation'] == 'Patient':
            return u['username']
        else:
            return 'No Patient'


def get_user_address():
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['ECE4564_FinalProject']['users']
    users = col.find()
    for u in users:
        if u['affiliation'] == 'Patient':
            return u['address']
        else:
            return 'No Patient'


# END CONTACT INFO MONGODB FUNCTIONS


# TWILIO FUNCTIONS
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
    repeats = 4
    for _ in range(repeats):
        msg += ' ' + msg
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


# DECISION FUNCTION
def detect_emergency():
    hr_data = hr_grab('2min')
    hr_spike = False
    hr_sink = False
    panic_b = has_button_pressed()
    hr_list = []
    for d in hr_data:
        hr_list.append(hr_data[d]['hr'])
    hr_array = np.array(hr_list, dtype=np.int16)
    diff_array = np.diff(hr_array)
    for d in diff_array:
        if d >= 30:
            hr_spike = True
        elif d <= -30:
            hr_sink = True
    if hr_spike:
        name = get_user_name()
        address = get_user_address()
        message = f'This is an emergency alert for {name}. They have had a sudden spike in heart rate at {address}.'
        send_alerts(message)
    elif hr_sink:
        name = get_user_name()
        address = get_user_address()
        message = f'This is an emergency alert for {name}. They have had a sudden drop in heart rate at {address}.'
        send_alerts(message)
    elif panic_b:
        name = get_user_name()
        address = get_user_address()
        message = f'This is an emergency alert for {name}. They have pressed a panic button at {address}.'
        send_alerts(message)


def has_button_pressed():
    return False


def main():
    
    hr_update(datetime.datetime.now(), 'Sean', random.randint(60, 70))


if __name__ == '__main__':
    main()
