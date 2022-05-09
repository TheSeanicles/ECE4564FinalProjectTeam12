import socket
import datetime
import time
import multiprocessing
import random
from pymongo import MongoClient
import yaml
from twilio.rest import Client
import numpy as np
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from pymongo import MongoClient
import json
from bson import ObjectId

#for objectID
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# MONGODB HR FUNCTIONS
def hr_update(co, t, usr, hr):
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['User_Heartrate'][co]
    start_dict = {'timestamp': t,
                  'metadata': usr,
                  'hr': hr}
    col.insert_one(start_dict)
    detect_emergency(co)


def hr_grab(co, t_select):
    thresh = get_thresh(t_select)
    mongo_client = MongoClient('mongodb://localhost:27017')
    col = mongo_client['User_Heartrate'][co]
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

def create_contact(name, pwd, affiliation, affiliated, phone_num, addy, sms, voice):
    if isinstance(sms, bool) and isinstance(voice, bool):
        return {'username': name,
                'password': pwd,
                'affiliation': affiliation,
                'affiliated': affiliated,
                'phone_number': phone_num,
                'address': addy,
                'sms': sms,
                'voice': voice
                }
    else:
        return {'username': name,
                'password': pwd,
                'affiliation': affiliation,
                'affiliated': affiliated,
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

#WEB API FUNCTIONS

class User():
    def __init__(self, name, id):
        self.name = name
        self.id = id #include more aspects needed here

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return JSONEncoder().encode(self.id)


# create the application object
app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'OOGABOOGAKEYHERE'#probably change key here

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('index.html')  # return a string

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    data = []
    if request.method == 'POST':
        mongoclient = MongoClient("mongodb://localhost:27017")
        col = mongoclient['ECE4564_FinalProject']['users']
        query = col.find_one({"_id": ObjectId(current_user.id[1:-1])})
        if query["affiliated"] == "Self":
            col2 = mongoclient['User_Heartrate'][current_user.id[1:-1]]
        else:
            col2 = mongoclient['User_Heartrate'][query["affiliated"][1:-1]]
        try:
            a = int(request.form["hist"])
            query2 = col2.find({},{"_id": 0, "hr": 1, "timestamp": 1}).sort("_id",-1).limit(a)
            if query2 is None:
                flash("No Results Found")
            for doc in query2:
                data.append([doc['hr'], doc['timestamp']])
        except:
            flash("Incorrect Input Type, Please Put A number")
    return render_template('profile.html', name=current_user.name, data = data)  # render a template

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/addcontact', methods=['GET', 'POST'])
@login_required
def addcontact():
    if request.method == 'POST':
        mongoclient = MongoClient("mongodb://localhost:27017")
        col = mongoclient['ECE4564_FinalProject']['users']
        affiliated = current_user.id
        col.insert_one(create_contact(request.form['name'], request.form['password'], request.form['affiliation'], affiliated, request.form['phone'], request.form['address'], request.form['sms'], request.form['voice']))
        return redirect(url_for('addcontact'))
    return render_template('addcontact.html')

@login_manager.user_loader
def load_user(id):
    mongoclient = MongoClient("mongodb://localhost:27017")
    col = mongoclient['ECE4564_FinalProject']['users']
    query = col.find_one({"_id": ObjectId(id[1:-1])})
    if query is None:
        return None
    return User(query['username'],id)#need to get query here

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mongoclient = MongoClient("mongodb://localhost:27017")
        col = mongoclient['ECE4564_FinalProject']['users']
        query = col.find_one({'username': request.form['name'], 'password': request.form['password']})
        if query is None:
            flash('Invalid Credentials. Please try again.')
        else:
            user = User(request.form['name'], query['_id'])
            remember = True if request.form.get('remember') else False
            login_user(user, remember=remember)#remember can change based on form
            return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/viewcontacts')
@login_required
def viewcontacts():
    data = []
    mongoclient = MongoClient("mongodb://localhost:27017")
    col = mongoclient['ECE4564_FinalProject']['users']
    query = col.find({"affiliated": current_user.id}).sort("_id",-1)
    if query is None:
        flash("No Results Found")
    for doc in query:
        data.append([doc['username'], doc['affiliation'], doc['phone_number'], doc['address']])
    return render_template('viewcontacts.html', data = data)  # render a template

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        mongoclient = MongoClient("mongodb://localhost:27017")
        col = mongoclient['ECE4564_FinalProject']['users']
        col.insert_one(create_contact(request.form['name'], request.form['password'], 'Patient', 'Self', request.form['phone'], request.form['address'], 'Patient', 'Patient'))
        query = col.find_one({'username': request.form['name'], 'password': request.form['password']})
        user = User(request.form['name'], query['_id'])
        login_user(user, remember=False)#remember can change based on form
        return redirect(url_for('profile'))
    return render_template('signup.html')

#END WEB API FUNCTIONS

# DECISION FUNCTION
def detect_emergency(id):
    hr_data = hr_grab(id, '2min')
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
    hr_update('62773a6537c648d63e8bf302', datetime.datetime.now(), 'Sean', random.randint(60, 70))
    app.run(debug=True)


if __name__ == '__main__':
    main()
