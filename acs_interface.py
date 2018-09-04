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
from loggingmodule import *
import time
import uuid
import requests
import queue as Q
from threading import Thread

# Set up some global variables
num_fetch_threads = 1
enclosure_queue = Q.PriorityQueue()

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
    # for entry in queue:
    #    stringliste = stringliste + str(entry)
    return stringliste


@app.route('/getDBInformation')
def getDBInformation():
    uuid = request.args.get('uuid')
    log = Loghandler()
    returnwert = log.GetData(uuid)
    return returnwert

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
    # Element aus Queue suchenn
    for n in enclosure_queue.queue:
        if(str(order_id) == str(n[1]['uuid'])):
            return n[1]

def get_status_for_all_orders():
    all_elements = []
    for n in enclosure_queue.queue:
        # print(n)
        all_elements.append(n[1])
    return all_elements

     
    
@app.route('/orderBeverage')
def orderBeverage():
    global acs_next_order
    beverage = request.args.get('productID')
    user = request.args.get('userID')
    # UUID für neue Bestellung erzeugen
    orderid = uuid.uuid4()
    date = request.args.get('deliveryDate')
    date_now = time.strftime("%Y-%m-%dT%H:%M:%S")


    if(date == None):
        date = date_now
    else:
        dateobj = time.strptime(date, "%Y-%m-%dT%H:%M:%S")
        
    # Zeitdifferenz, wenn mehr als 15 Sek in Vergangenheit -> aktuelle Zeit eintragen

        dt1 = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        dt2 = datetime.datetime.strptime(date_now, "%Y-%m-%dT%H:%M:%S")

        d = dt2 - dt1

        if(d.days>=0):
            if(d.seconds>= 15):
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
        entry["uuid"] = str(orderid) 
        dt = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        #Calculate Priority based on timestamp
        enclosure_queue.put((dt.timestamp(),entry))
        #sort_queue()
        log_message("Starting Beverage " + str(orderid))
        msg = {}
        msg["uuid"] = str(orderid)
        response = Response(
            response=json.dumps(msg),
            status=200,
            mimetype='application/json'
        )
        
#       response.set_cookie("order_id",str(order_id))
    return response

@app.route('/updateBeverage', methods=['GET'])
def updateBeverage():
    uuid = request.args.get('uuid')
    msg = {}
    newQueue = Q.PriorityQueue()
    global enclosure_queue
    msg["status"] = "False"
    for entry in enclosure_queue.queue:
         if(str(uuid) == str(entry[1]['uuid'])):
             entry[1]['productID'] = request.args.get('productID')
             entry[1]['deliveryDate'] = request.args.get('deliveryDate')
             entry[1]['userID'] = request.args.get('userID')
             msg["status"] = "True"
         dt = datetime.datetime.strptime(entry[1]['deliveryDate'], "%Y-%m-%dT%H:%M:%S")
         print(dt, type(dt))
         newQueue.put((dt.timestamp(), entry[1]))

    response = Response(
        response=json.dumps(msg),
        status=404,
        mimetype='application/json'
    )
    
    # Workaround
    enclosure_queue = newQueue
    return response

@app.route('/deleteBeverage')
def deleteBeverage():
    uuid = request.args.get('uuid')
    msg = {}
    newQueue = Q.PriorityQueue()
    global enclosure_queue
    msg["status"] = "False"
    for entry in enclosure_queue.queue:
        if(str(uuid) != str(entry[1]['uuid'])):
            dt = datetime.datetime.strptime(entry[1]['deliveryDate'], "%Y-%m-%dT%H:%M:%S")
            newQueue.put((dt.timestamp(),entry[1]))
        else:
            msg["status"] = "True"
    response = Response(
        response=json.dumps(msg),
        status=200,
        mimetype='application/json'
    )
    
    # Workaround
    enclosure_queue = newQueue
    return response

def sort_queue():
    # queue.sort(key=lambda x: datetime.datetime.strptime(x['deliveryDate'], '%Y-%m-%dT%H:%M:%S'))
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
    reply = json.dumps("No ID given")
    if(uuid != None):
        counter = 1
        estimatedTime = 0
        for n in enclosure_queue.queue:
            if(str(uuid) == str(n[1]['uuid'])):
                estimatedTime = counter * 30
                reply = json.dumps(estimatedTime)
                break
            else:
                counter += 1
    response = Response(
        response=reply,
        status=400,
        mimetype='application/json'
    )          
    return response


@app.route('/')
def index():
    return "<html><body><h1>Simulator für die App-Schnittstelle, services unter /orderBeverage und /getStatus </html></body>"

#monitoring

@app.route('/monitor')
def monitor():

    if (getQueue() == 0):
        monitorqueue = "Die Queue ist Leer!"
    else:
        monitorqueue = " Die Queue hat " + str(getQueue().count('}')) + " Einträge!"
    states = {'ready': "Die Kaffeemaschiene ist bereit!", 'isRunning': "Die Kaffeemaschiene arbeitet!",
              'waiting': "Die Kaffeemaschiene wartet!", 'timeout': "Die Kaffeemaschiene ist nicht erreichbar!"}
    monitor = states.get(get_status_from_acs()) + monitorqueue
    if(get_status_from_acs() != 'timeout'):
        feedbackMonitoring(monitor)
        feedbackStatus(get_status_from_acs())
    return monitor

#feedback:
def feedbackMonitoring(error):
    sound = requests.post("http://localhost:8000/sendCommand?cmd=Speak'"+ str(error) +"'")
    light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(110,0,0)")
    return ""

def feedbackStatus(status):
    if (status == 'ready'): #Status isrunning
        light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(80,255,0)") #grüner RGB-Wert
    elif (status == 'isRunning'): #Status fertig und bereit
        light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(255,255,000)") #orangener RGB-Wert
    elif (status == 'waiting'):  # Status fertig und bereit
        light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(255,255,000)") #orangener RGB-Wert
    return ""

#Funktion wird von der Queue aufgerufen, wenn der Kaffe produziert wird
def feedbackCafeReady():
    cafeTime = 30.0
    time.sleep(cafeTime)
    sound = requests.post("http://localhost:8000/sendCommand?cmd=Speak'Ihr Kaffee ist fertig'")
    return ""

#Funktion wird von der Quue aufgerufen, wenn der 100. Kaffee gestartet wird
def feedbackJubilaeum():
    sound = requests.post("http://localhost:8000/sendCommand?cmd=Speak'Juhu! hundertster Kaffee'")
    light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(255,255,000)") #gelber RGB-Wert
    time.sleep(0.5)
    light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(110,0,0)") #pinkener RGB-Wert
    time.sleep(0.5)
    light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(000,255,0)")
    time.sleep(0.5)
    light = requests.post("http://localhost:8000/sendCommand?cmd=SetLight(80,199,0)")
    return ""

def coffeeLooper(q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and only exit when
    the main thread ends.
    """
    while True:
        for n in enclosure_queue.queue:
            if datetime.datetime.strptime(n[1]['deliveryDate'], "%Y-%m-%dT%H:%M:%S") <= datetime.datetime.now():
                order = q.get()
                print("Working on order "+ order[1]['uuid'])
                # TODO GetStatus ACS before firing 
                u = "http://localhost:8000/sendCommand?cmd=StartBeverage("+order[1]['productID']+")"
                requests.get(u)
                time.sleep(50)
                q.task_done()
        time.sleep(1)

if __name__ == '__main__':
    # Set up some threads to fetch the enclosures

    for i in range(num_fetch_threads):
        worker = Thread(target=coffeeLooper, args=(enclosure_queue,))
        worker.setDaemon(True)
        worker.start()

    print('*** Main thread waiting')
    enclosure_queue.join()

    app.run(host='0.0.0.0', debug=True)
    


    
    
