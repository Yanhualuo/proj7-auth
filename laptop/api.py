# Laptop Service
import os
import pymongo
from flask import Flask, request, session, render_template, url_for, redirect
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                          as Serializer, BadSignature, \
                          SignatureExpired)
import time

# Instantiate the app
app = Flask(__name__)
api = Api(app)
app.secret_key = 'AAA'
app.config['SESSION_TYPE'] = 'the quick brown fox jumps over the lazy dog'

client = MongoClient()
db = client.time
mongo = client.user

auth = HTTPBasicAuth()

#############################################
def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)


def generate_auth_token(expiration=600):
    # s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    # pass index of user
    return s.dumps({'id': 1})

def verify_auth_token(token):
    s = Serializer('test1234@#$')
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"


#############################################

class ListAll(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]

        result = { 'open_time': [item["open_times"] for item in i],
        'close_time': [item["close_times"] for item in i],
        'km': [item["km"] for item in i]
        }
        return result


class ListAllJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        doc = []
        for item in i:
            item_doc = {
                'km': item["km"],
                'open_time' : item["open_times"],
                'close_time': item["close_times"]
            }
            doc.append(item_doc)
        return doc


class ListAllCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]

        result=[]
        
        for item in i:
            temp = item["km"] + ", " + item["open_times"] + ", " + item["close_times"]
            result.append(temp)
            
        return result



###################################################


class ListOpenOnly(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = { 'open_time': [item["open_times"] for item in i]}
        return result

class ListOpenOnlyJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = []
        for item in i:
            item_doc = {
                'open_time' : item["open_times"]
            }
            result.append(item_doc)

        return result

class ListOpenOnlyCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
    
        item_list = db.tododb.find().sort("open_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result=[]
        
        for item in i:
            temp = item["open_times"]
            result.append(temp)
        return result


#################################


class ListCloseOnly(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100
        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = { 'close_time': [item["close_times"] for item in i]}
        return result


class ListCloseOnlyJson(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result = []
        for item in i:
            item_doc = {
                'close_time' : item["close_times"]
            }
            result.append(item_doc)
        return result


class ListCloseOnlyCsv(Resource):
    def get(self):
        top = request.args.get("top")
        if top == None:
            top = 100

        item_list = db.tododb.find().sort("close_times", pymongo.ASCENDING).limit(int(top))
        i = [item for item in item_list]
        
        result=[]
        
        for item in i:
            temp = item["close_times"]
            result.append(temp)

        return result


# Create routes

api.add_resource(ListAll, '/listAll')
api.add_resource(ListAllJson, '/listAll/json')
api.add_resource(ListAllCsv, '/listAll/csv')

api.add_resource(ListOpenOnly, '/listOpenOnly')
api.add_resource(ListOpenOnlyJson, '/listOpenOnly/json')
api.add_resource(ListOpenOnlyCsv, '/listOpenOnly/csv')

api.add_resource(ListCloseOnly, '/listCloseOnly')
api.add_resource(ListCloseOnlyJson, '/listCloseOnly/json')
api.add_resource(ListCloseOnlyCsv, '/listCloseOnly/csv')

####################################################################################



@app.route('/')
def index():
    if 'username' in session:
        #return render_template('hello.html')
        return 'You are logged in as ' + session['username']
    
    return render_template('index.html')

@app.route('/api/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        
        if existing_user is None:
            hashpass = hash_password(request.form['pass'])
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'
    
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})
    
    if login_user:
        print(login_user['password'])
        if verify_password(request.form['pass'], login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'







# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
