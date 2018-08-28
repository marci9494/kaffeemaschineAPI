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
from datetime import timedelta
import sys

import time

queue = [{'deliveryDate': '2014-06-14T23:34:30', 'productID': '4', 'userID': '4-bla', 'uuid': '5945c961-e74d-478f-8afe-da53cf4189e1'},{'deliveryDate': '2016-06-14T23:34:30', 'productID': '4', 'userID': '4-bla', 'uuid': '5945c961-e74d-478f-8afe-da53cf4189e2'},{'deliveryDate': '2017-06-14T23:34:30', 'productID': '4', 'userID': '4-bla', 'uuid': '5945c961-e74d-478f-8afe-da53cf4189e3'},{'deliveryDate': '2018-06-14T23:34:30', 'productID': '4', 'userID': '4-bla', 'uuid': '5945c961-e74d-478f-8afe-da53cf4189e4'},{'deliveryDate': '2019-06-14T23:34:30', 'productID': '4', 'userID': '4-bla', 'uuid': '5945c961-e74d-478f-8afe-da53cf4189e5'}]
#queue = []

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
    uuid = request.args.get('uuid')
    for entry in queue:
        if(str(uuid) == str(entry['uuid'])):
            return entry
            break

def get_status_for_all_orders():
    return queue
     
    
@app.route('/orderBeverage')
def orderBeverage():
    global acs_next_order
    beverage = request.args.get('productID')
    user = request.args.get('userID')
    uuid = '5945c961-e74d-478f-8afe-da53cf4189e3'
    date = request.args.get('deliveryDate')
    date_now = time.strftime("%Y-%m-%dT%H:%M:%S")
    dateobj = time.strptime(date, "%Y-%m-%dT%H:%M:%S")

    # Zeitdifferenz, wenn mehr als 15 Sek in Vergangenheit -> aktuelle Zeit eintragen

    
    
    if(date == None):
        date = date_now
    
    
    
    if (beverage == None):
        log_message("Kein Getränk angegeben")
        response = Response(
            response=json.dumps("No command given"),
            status=500,
            mimetype='application/json'
        )
    else:
#       order_id = acs_next_order
#       acs_next_order += 1
        entry = {}
        entry["deliveryDate"] = date
        entry["productID"] = beverage
        entry["userID"] = user
        entry["uuid"] = uuid 
        queue.append(entry)
        sort_queue()
        log_message("Starting Beverage " + str(uuid))
        msg = {}
        msg["uuid"] = uuid
        response = Response(
            response=json.dumps(msg),
            status=200,
            mimetype='application/json'
        )
        
#       response.set_cookie("order_id",str(order_id))
    return response

@app.route('/updateBeverage')
def updateBeverage():
    uuid = request.args.get('uuid')
    msg = {}
    for entry in queue:
        if(str(uuid) == str(entry['uuid'])):
            entry['productID'] = request.args.get('productID')
            entry['deliveryDate'] = request.args.get('deliveryDate')
            msg['status'] = "True"
            response = Response(
                response=json.dumps(msg),
                status=200,
                mimetype='application/json'
            )
            sort_queue()
            break
        else:
            msg['status'] = "False"
            response = Response(
                response=json.dumps(msg),
                status=404,
                mimetype='application/json'
            )
    return response

@app.route('/deleteBeverage')
def deleteBeverage():
    uuid = request.args.get('uuid')
    msg = {}
    for entry in queue:
        if(str(uuid) == str(entry['uuid'])):
            queue.remove(entry)
            msg["status"] = "True"
            response = Response(
                response=json.dumps(msg),
                status=200,
                mimetype='application/json'
            )            
            sort_queue
            break
        else:
            msg["status"] = "False"
            response = Response(
                response=json.dumps(msg),
                status=404,
                mimetype='application/json'
            )
    return response

def sort_queue():
    queue.sort(key=lambda x: datetime.datetime.strptime(x['deliveryDate'], '%Y-%m-%dT%H:%M:%S'))
    print (queue)
    return 0

@app.route('/getStatus')
def getStatus():
    uuid = request.args.get('uuid')
    if (uuid != None):
        msg = get_status_for_order(uuid) 
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
    uuid = request.args.get('uuid')
    if(uuid != None):
        counter = 1
        estimatedTime = 0
        for entry in queue:
            if (str(entry['uuid']) == str(uuid)):
                estimatedTime = counter * 30
                response = Response(
                    response=json.dumps(estimatedTime),
                    status=200,
                    mimetype='application/json'
                )
                break
            else:
                counter += 1
    else:
        response = Response(
            response=json.dumps("No ID given"),
            status=400,
            mimetype='application/json'
        )          
    return response


@app.route('/')
def index():
    return "<html><body><h1>Simulator für die App-Schnittstelle, services unter /orderBeverage und /getStatus </html></body>"

if __name__ == '__main__':
    app.run(debug=True)
