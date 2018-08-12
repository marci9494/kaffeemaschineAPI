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
    msg = {}
    msg["id"] = order_id
    msg["beverage"] = 1
    msg["state"] = acs_response
    msg["when"] = "24.07.2018 13:54.37"
    return msg

def get_status_for_all_orders():
    content = []
    entry = {}
    entry["id"] = "4711"
    entry["beverage"] = 1
    entry["state"] = "isRunning"
    entry["when"] = "24.07.2018 13:54.37"
    content.append(entry)
    entry = {}
    entry["id"] = "4712"
    entry["beverage"] = 2
    entry["state"] = "waiting"
    entry["when"] = "24.07.2018 13:54.48"
    content.append(entry)
    return content
     
    
@app.route('/orderBeverage')
def orderBeverage():
    global acs_next_order
    beverage = request.args.get('id')
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
        log_message("Starting Beverage " + str(order_id))
        response = Response(
            response=json.dumps(order_id),
            status=200,
            mimetype='application/json'
        )
        
        response.set_cookie("order_id",str(order_id))
    return response

@app.route('/getStatus')
def getStatus():
    order_id = request.args.get('order_id')
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


@app.route('/')
def index():
    return "<html><body><h1>Simulator für die App-Schnittstelle, services unter /orderBeverage und /getStatus </html></body>"

if __name__ == '__main__':
    app.run(debug=True)
