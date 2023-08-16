import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json


# Note! Initialize first instance of google firebase and then overwrite credential \n
# as "serviceAccountKey.json" as file inside project folder

credential = None
cred = credentials.Certificate(credential)

# Note! after credentials is initiated, copy url of google firebase instance and \n
#overwrite url_db

url_db = None

#initialize service account
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred,{
        'databaseURL': url_db
    })



ref = db.reference("/") 

#save new data, assigin child element as 'income_expense
def insert_period(period,incomes,expenses,comment):
    data = {'incomes':incomes,'expenses':expenses,'comment':comment}
    ref.child('income_expense').child(period).set(data)

#fetch all
def fetch_all():
    data = []
    vars = ref.child('income_expense').get()
    for i in vars.items():
        jn = list(i)
        data.append(jn[0])

    return data

def get_period(period):
    value = ref.child('income_expense').child(period).get() 
    return value