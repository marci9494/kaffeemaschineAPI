# Simulator für die Steuerung der WMF-Kaffeemaschine

# Die services hier entsprechen denen in KaffeService.cs
# Die Funktionen werden nicht tatsächlich ausgeführt, es werden nur entsprechende
# Nachrichten auf die Konsole ausgegeben. Das reale Verhalten wird nur in etwa
# nachgebildet, timing, Fehlerhäufigkeiten usw. stimmen also nicht (exakt) mit
# der Realität überein.

# Version 0.9 T. Hänisch 30.7.2018

from flask import Flask
from flask import json,Response
from flask import request, render_template, redirect
from flask import g
import urllib.request
import datetime,time
import sys

import time


class ACS:
    # gültige Zustände sind "ready", "isRunning", "waiting" und "timeout". 
    acs_state = "ready"
    # Zeitstempel für Beginn StartBeverage
    acs_start = 0.0

    # Dauer für die Zubereitung eines Kaffees in Sekunden
    acs_duration = 30.0
    
def log_message(txt):
    print(txt)


app = Flask(__name__)

@app.route('/sendCommand')
def sendCommand():
    # Die verfügbaren Kommandos sind die Originalkommandos der Steuersoftware, Details siehe dort.
    # Die hier bereitgestellten Kommandos (und nur diese sollten auch in der Kommunikation mit der
    # echten Maschine verwendet werden sind StartBeverage, speak und setLighting sp?)

    cmd = request.args.get('cmd')
    if (cmd == None):
        log_message("sendCommand: Kein Kommando angegeben")

    elif (cmd == "Speak"):
        log_message("sendCommand: Speak " + cmd)

    elif (cmd == "SetLight"):
        log_message("sendCommand: Set Light " + cmd)

    elif (cmd == "StartBeverage"):
        log_message("sendCommand: StartBeverage " + cmd)
        if (ACS.acs_state != "ready"):
            log_message("sendCommand:StartBeverage, state sollte ready sein, ist " + ACS.acs_state)
        else:
            # Los geht's ...
            ACS.acs_state="isRunning"
            ACS.acs_start = time.time()
            log_message("sendCommand:StartBeverage gestartet um " + str(ACS.acs_start))
            
    else:
        log_message("sendCommand: Unbekanntes Kommando")

    return ""

def check_acs_state():
    # Hier werden die Zustandsübergänge gemacht TODO: Fehler einbauen
    if (ACS.acs_state == "isRunning"):
        if (time.time()-ACS.acs_start > ACS.acs_duration):
            # Getränk produziert 
            ACS.acs_state = "ready"
            ACS.acs_start = 0.0

@app.route('/getStatus')
def getStatus():
    # Reicht, wenn wir das hier aufrufen, wenn niemand nach dem Status schaut, ist er irgendwie auch nicht real ...
    check_acs_state()
    msg=ACS.acs_state
    response = Response(
    response=msg,
    status=200,
    mimetype='application/json'
    )
    return response


@app.route('/')
def index():
    return "<html><body><h1>Simulator für die Steuerung der Kaffeemaschine, services unter /sendCommand und /getStatus </html></body>"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)
