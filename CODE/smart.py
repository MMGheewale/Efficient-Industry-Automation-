import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
import RPi.GPIO as GPIO
import time
from threading import Thread
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
import urllib.request
import requests
import json
URl='https://api.thingspeak.com/update?api_key=J2ET3H82NOTUZWUR'
import dth11


ON = False
OFF = True

lock = 8
GPIO.setup(lock, GPIO.OUT)
GPIO.output(lock, OFF)
global lock_last_state
lock_last_state = 0
alaram = 37
GPIO.setup(alaram, GPIO.OUT)
GPIO.output(alaram, False)

door = 11
GPIO.setup(door, GPIO.IN,GPIO.PUD_UP)
global door_open_count
global door_close_count
door_open_count = 0
door_close_count = 0

ldr = 40
GPIO.setup(ldr, GPIO.IN)
light = 7
GPIO.setup(light, GPIO.OUT) 
GPIO.output(light, OFF)

smoke = 36
GPIO.setup(smoke, GPIO.IN)
mains = 5
GPIO.setup(mains, GPIO.OUT)
GPIO.output(mains, ON)
fan = 3
GPIO.setup(fan, GPIO.OUT)
GPIO.output(fan, OFF)
global smoke_problem_count
smoke_problem_count=0
global smoke_normal_count
smoke_normal_count=0

instance = dth11.DHT11(pin=38)
global temperature_normal_count
global temperature_problem_count
temperature_normal_count = 0
temperature_problem_count = 0


def rfid_(internet_status):
    global lock_last_state
    id, text = reader.read_no_block()
    print(id)
    print(text)
    text = str(text).replace(" ","")
    if((text== "boss") or (text=="saqib") or (text== "guru")):
        if(lock_last_state ==0):
            GPIO.output(lock, ON)
            GPIO.output(alaram, True)
            time.sleep(1)
            GPIO.output(alaram, False)
            if(internet_status==1):
                try:
                    HEADER='&field1={}'.format(1)
                    NEW_URL = URl+HEADER
                    data=urllib.request.urlopen(NEW_URL)
                    print("\n")
                except:
                    print("no internet")
            lock_last_state=1
        else:
            GPIO.output(lock, OFF)
            GPIO.output(alaram, True)
            time.sleep(1)
            GPIO.output(alaram, False)
            if(internet_status==1):
                try:
                    HEADER='&field1={}'.format(0)
                    NEW_URL = URl+HEADER
                    data=urllib.request.urlopen(NEW_URL)
                    print("\n")
                except:
                    print("no internet")
            lock_last_state=0

def door_(internet_status):
    global door_open_count
    global door_close_count
    if(GPIO.input(door)):
        print("Door open")
        door_close_count=0
        if(door_open_count==0):
            if(internet_status==1):
                try:
                    HEADER='&field2={}'.format(1)
                    NEW_URL = URl+HEADER
                    data=urllib.request.urlopen(NEW_URL)
                except:
                    print("no internet")
            door_open_count=1
    else:
        print("Door closed")
        door_open_count=0
        if( door_close_count == 0):
            if(internet_status==1):
                try:
                    HEADER='&field2={}'.format(0)
                    NEW_URL = URl+HEADER
                    data=urllib.request.urlopen(NEW_URL)
                except:
                    print("no internet")
            door_close_count=1
        
def light_():
    if ( GPIO.input(ldr) == 1):
        print("Lights are ON")
        GPIO.output(light, ON)
                    
    else:
        print("Lights are OFF")
        GPIO.output(light, OFF)
        
def smoke_(internet_status):
    global smoke_problem_count
    global smoke_normal_count
    value = GPIO.input(smoke)
    print("value is: ",value)
    if value == 0: # Checks what's up with Pin 4, if it's TRUE or FALSE
        print("smoke Problem")
        smoke_normal_count=0
        GPIO.output(mains, OFF)
        GPIO.output(fan, ON)
        GPIO.output(alaram, True)
        if(smoke_problem_count==0 and internet_status==1):
            try:
                HEADER='&field3={}'.format(1)
                NEW_URL = URl+HEADER
                data=urllib.request.urlopen(NEW_URL)
            except:
                print("no internet")
        smoke_problem_count=1
        time.sleep(10)
        GPIO.output(alaram, False)
                
    else:  
        print("smoke Normal")
        smoke_problem_count=0
        GPIO.output(mains, ON)
        GPIO.output(fan, OFF)
        GPIO.output(alaram, False)
        smoke_normal_count=1
    
def temperature_(internet_status):
    global temperature_normal_count
    global temperature_problem_count
    result = instance.read()
    if result.is_valid():
        print("Temp: %d C" % result.temperature +' '+"Humid: %d %%" % result.humidity)
        print("-",result.temperature,"-")
        store_temprature = str(result.temperature).replace(" ","")
        if(int(store_temprature) >= 30):
            print("temp Problem")
            temperature_normal_count=0
            GPIO.output(mains, OFF)
            GPIO.output(fan, ON)
            GPIO.output(alaram, True)
            if(temperature_problem_count==0 and internet_status==1):
                try:
                    HEADER='&field4={}'.format(result.temperature)
                    NEW_URL = URl+HEADER
                    data=urllib.request.urlopen(NEW_URL)
                except:
                    print("no internet")
            temperature_problem_count=1
            time.sleep(10)
            GPIO.output(alaram, False)
                
    else:  
        print("temp Normal")
        temperature_problem_count=0
        GPIO.output(mains, ON)
        GPIO.output(fan, OFF)
        GPIO.output(alaram, False)
        temperature_normal_count=1            

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False

internet_status = 1 if connect() else 0
if(internet_status==0):
    print("no internet")
    
while True:
    if(internet_status==0):
        internet_status = 1 if connect() else 0
    
    rfid_(internet_status)
    door_(internet_status)
    light_()
    smoke_(internet_status)
    temperature_(internet_status)