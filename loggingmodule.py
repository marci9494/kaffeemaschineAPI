#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 10:47:59 2018

author: florian, patrick
filename: logging.py
version: 0.1
last updated: 27.08.2018 by FS


description: 
    Request: this class stores the attributes of one request to the coffeemachine; eg. the UUID or the coffeetype
    Loghandler: this class gets a Request-object by submit-method and stores it to the database
example:
    log = Loghandler() #creation of the Loghandler object
    objekt = Request() #creation of the Request object
    objekt.uuid = 1 #sets the uuid of the Request object to "1"
    objekt.toqueue = 1 #sets toqueue to 1 and the attribute toqueuetime to actual time
    objekt.errorcode = 1 #sets the errorcode to 1 and the errortext to "Fehler vorhanden"
    objekt.tocustomer = 1 #sets tocustomer to 1 and the attribute tocustomertime to actual time
    log.submit(objekt) #creation (or update) of database entry

"""

import sqlite3
import datetime


class Loghandler:
    def __init__(self):
        self.db = sqlite3.connect('data/db.sqlite3')
        self.cursor = self.db.cursor() 
        
    def CreateDBEntry(self, uuid, toqueue, toqueuetime, tocoffeemachine, tocoffeemachinetime, tocustomer, tocustomertime, coffee, quantity, errorcode, errortext):
        self.cursor.execute('''INSERT INTO logs(uuid, toqueue, toqueuetime, tocoffeemachine, tocoffeemachinetime, tocustomer, tocustomertime, coffee, quantity, errorcode, errortext)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?)''', (uuid, toqueue, toqueuetime, tocoffeemachine, tocoffeemachinetime, tocustomer, tocustomertime, coffee, quantity, errorcode, errortext))
        self.db.commit()

    def UpdateDBEntry(self, uuid, toqueue, toqueuetime, tocoffeemachine, tocoffeemachinetime, tocustomer, tocustomertime, coffee, quantity, errorcode, errortext):
        self.cursor.execute('''UPDATE logs SET uuid = ?, toqueue = ?, toqueuetime = ?, tocoffeemachine = ?, tocoffeemachinetime = ?, tocustomer = ?, tocustomertime = ?, coffee = ?, quantity = ?, errorcode = ?, errortext = ?
                  WHERE uuid = ?''', (uuid, toqueue, toqueuetime, tocoffeemachine, tocoffeemachinetime, tocustomer, tocustomertime, coffee, quantity, errorcode, errortext, uuid))
        self.db.commit()
    
    def SetTimes(self, robject):
        try:
            self.cursor.execute('''SELECT toqueuetime FROM logs WHERE uuid = ?''', (robject.uuid,))
            toqueuetime = self.cursor.fetchall()[0][0]
            self.cursor.execute('''SELECT tocoffeemachinetime FROM logs WHERE uuid = ?''', (robject.uuid,))
            tocoffeemachinetime = self.cursor.fetchall()[0][0]
            self.cursor.execute('''SELECT tocustomertime FROM logs WHERE uuid = ?''', (robject.uuid,))
            tocustomertime = self.cursor.fetchall()[0][0]
        except:
            toqueuetime = '0'
            tocoffeemachinetime = '0'
            tocustomertime = '0'
  
        if ( toqueuetime == '0' and robject.toqueue == 1 ):
            robject.toqueuetime = datetime.datetime.now()
        if ( tocoffeemachinetime == '0' and robject.tocoffeemachine == 1 ):
            robject.tocoffeemachinetime = datetime.datetime.now()
        if ( tocustomertime == '0' and robject.tocustomer == 1 ):
            robject.tocustomertime = datetime.datetime.now()
        
        return(robject)

    def submit(self, robject):
        self.cursor.execute('''SELECT uuid FROM logs WHERE uuid = ?''', (robject.uuid,))
        result = self.cursor.fetchall() 
        robject = self.SetTimes(robject)
        
            
        
        robject.CreateErrortext()
        coffee = 0
        quantity = 0
        #coffee,quantity erstellen aus HTTPOBject TBD



        if (len(result) == 0):
            self.CreateDBEntry(robject.uuid, robject.toqueue, robject.toqueuetime, robject.tocoffeemachine, robject.tocoffeemachinetime, robject.tocustomer, robject.tocustomertime, coffee, quantity, robject.errorcode, robject.errortext) 
        else:
            self.UpdateDBEntry(robject.uuid, robject.toqueue, robject.toqueuetime, robject.tocoffeemachine, robject.tocoffeemachinetime, robject.tocustomer, robject.tocustomertime, coffee, quantity, robject.errorcode, robject.errortext)
            
        
class Request:
    def __init__(self):
        self.uuid = 0
        self.httpobject = 0
        self.toqueue = 0
        self.toqueuetime = 0
        self.tocoffeemachine = 0
        self.tocoffeemachinetime = 0
        self.tocustomer = 0
        self.tocustomertime = 0
        self.errorcode = 0
        self.coffee = 0
        self.quantity = 0
        self.errortext = 0

    
    def CreateErrortext(self):
        if (self.errorcode == 0):
            self.errortext = "Kein Fehler vorhanden"
        else:
            self.errortext = "Fehler vorhanden" #tbd
            
            