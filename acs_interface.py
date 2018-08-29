# Simulator für die App-Schnittstelle WMF-Kaffeemaschine
# Hier können Getränke bestellt und die Queue abgefragt werden.
# Verwendet wird das Low Level Interface, entweder der ACS-Software (KaffeeServicde.cs)
# oder der Simulator sim_acs.py

# Version 0.9 T. Hänisch 30.7.2018

from flask import Flask
from flask import json,Response
from flask import request, render_template, redirect
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import datetime
import sys

import time

queue = []

# Die id für die nächste Bestellung
# Achtung, bei Neustart nicht eindeutig, sollte persistent gemacht werden ...
acs_next_order = 4711

# Die URL für den Status-Webservice der Kaffemaschine
acs_status_url = "http://localhost:8000/getStatus"

def log_message(txt):
    print(txt)


app = Flask(__name__)

@app.route('/listBeverages')
def list_beverages():
   return '[{"name": "Espresso", "id": 1},{"name": "Cappuccino", "id": 2},{"name": "Cafe Creme", "id": 3},{"name": "Latte Macchiato", "id": 4},{"name": "Milch-Choc", "id": 5},{"name": "Milchkaffee", "id": 6}, {"name": "Chociatto", "id": 7},{"name": "Milchschaum", "id": 8}]'

@app.route('/getQueue')
def getQueue():
    stringliste = ''
    for entry in queue:
        stringliste = stringliste + str(entry)
    return stringliste


# Fragt den Status der Kaffemaschine ab und liefert den als String zurück
def get_status_from_acs():
    req = Request(acs_status_url)
    status = "timeout"
    try:
        response = urlopen(req)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach the server.')
        print('Reason: ', e.reason)
    else:
        # everything is fine
        status = response.read().decode('utf-8')
    return status

def get_status_for_order(order_id):
    # Fake: Hier wird der Status von der Kaffemaschine geholt und zurückgeliefert,
    # das sollte natürlich der Status des gewünschten Entries sein ....       
    acs_response = get_status_from_acs()
    orderID = request.args.get('orderID')
    for entry in queue:
        if(str(orderID) == str(entry['orderID'])):
            return entry
            break

def get_status_for_all_orders():
    return queue
     
    
@app.route('/orderBeverage')
def orderBeverage():
    global acs_next_order
    beverage = request.args.get('productID')
    user = request.args.get('userID')
    date = request.args.get('deliveryDate')
    uuid = '5945c961-e74d-478f-8afe-da53cf4189e3'
    
    if (beverage == None):
        log_message("Kein Getränk angegeben")
        response = Response(
            response=json.dumps("No command given"),
            status=500,
            mimetype='application/json'
        )
    else:
        order_id = acs_next_order
        acs_next_order += 1
        entry = {}
        entry["deliveryDate"] = date
        entry["productID"] = beverage
        entry["userID"] = user
        entry["uuid"] = uuid
        queue.append(entry)
        sort_queue()
        log_message("Starting Beverage " + str(order_id))
        response = Response(
            response=json.dumps(uuid),
            status=200,
            mimetype='application/json'
        )
        
        response.set_cookie("order_id",str(order_id))
    return response

@app.route('/updateBeverage')
def updateBeverage():
    userID = request.args.get('userID')
    for entry in queue:
        if(str(userID) == str(entry['userID'])):
            entry['productID'] = request.args.get('productID')
            entry['deliveryDate'] = request.args.get('deliveryDate')
            status = '[{„status“ : „True“}]'
            sort_queue()
            break
        else:
            status = '[{„status“ : „False“}]'
        return status

@app.route('/deleteBeverage')
def deleteBeverage():
    userID = request.args.get('userID')
    for entry in queue:
        if(str(userID) == str(entry['userID'])):
            queue.remove(entry)
            status = '[{„status“ : „True“}]'
            sort_queue
            break
        else:
            status = '[{„status“ : „False“}]'
    return status

def sort_queue():
    queue.sort(key=lambda x: datetime.datetime.strptime(x['deliveryDate'], '%Y-%m-%dT%H:%M:%S'))
    print (queue)
    return 0

@app.route('/getStatus')
def getStatus():
    order_id = request.args.get('orderID')
    if (order_id != None):
        msg = get_status_for_order(order_id) 
        response = Response(
            response=json.dumps(msg),
            status=200,
            mimetype='application/json'
        )
    else:
        msg = get_status_for_all_orders()   
        response = Response(
            response=json.dumps(msg),
            status=200,
            mimetype='application/json'
        )
    return response

@app.route('/getEstimatedTime')
def getEstimatedTime():
    orderID = request.args.get('orderID')
    counter = 1
    estimatedTime = 0
    estimatedTime = queue.index(orderID) * 30
    print(queue.index(orderID))            
    return str(estimatedTime)

@app.route('/')
def index():
    return "<html><body><h1>Simulator für die App-Schnittstelle, services unter /orderBeverage und /getStatus </html></body>"

@app.route('/monitor')
def monitoring():
    if(getQueue() == 0 ):
        monitorqueue = "Die Queue ist Leer!"
    else:
        monitorqueue = " Die Queue hat " + str(getQueue().count('}')) + " Einträge!"
    states = {'ready': "Die Kaffeemaschiene ist bereit!", 'isRunning': "Die Kaffeemaschiene arbeitet!", 'waiting' :"Die Kaffeemaschiene wartet!", 'timeout': "Die Kaffeemaschiene ist nicht erreichbar!"}
    monitor = states.get(get_status_from_acs()) + monitorqueue
    return monitor

if __name__ == '__main__':
    app.run(debug=True)
