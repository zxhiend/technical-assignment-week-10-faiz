import time
import requests

import Adafruit_DHT
import RPi.GPIO as GPIO
from ubidots import ApiClient



PIN_DHT = 4
PIN_RELAY = 27

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24


GPIO.setmode(GPIO.BCM)



TOKEN = "BBFF-QGpKKAZQYQQRVveUVCjr87iCxzNMJP"  # Put your TOKEN here
DEVICE_LABEL = "riil"  # Put your device label here 
VARIABLE_LABEL_1 = "temperature"  # Put your first variable label here
VARIABLE_LABEL_2 = "humidity"  # Put your second variable label here
VARIABLE_LABEL_3 = "relay"
VARIABLE_LABEL_4 = "ultrasonic"


 

 

def distance():
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance


def temperature():
    DHT_SENSOR = Adafruit_DHT.DHT11
    
    humidity = None
    temperature = None

    while temperature is None and humidity is None:
       humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, PIN_DHT)

    return temperature


def humidity():
    DHT_SENSOR = Adafruit_DHT.DHT11
    
    temperature = None
    humidity = None

    while temperature is None and humidity is None:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, PIN_DHT)

    return humidity

 
def relay():
    # api setup
    api = ApiClient(token='BBFF-G7bHXCDx1yl8uspx6CqH9ng1jla1Ea')
    VARIABLE_LABEL_3 = api.get_variable("63006b41a0d47d000d429582")
    status = VARIABLE_LABEL_3.get_values(1)
    
    # status off/on
    print(status[0]['value'])

    if status[0]['value']:
        GPIO.setup(PIN_RELAY, GPIO.OUT)
        GPIO.output(PIN_RELAY, GPIO.HIGH)
    else:
        GPIO.setup(PIN_RELAY, GPIO.IN)
    

def build_payload(variable_1, variable_2, variable_3, variable_4):
    # Creates two random values for sending data
    value_1 = temperature()
    value_2 = humidity()
    value_3 = relay()
    value_4 = distance()

    payload = {variable_1: value_1,
               variable_2: value_2,
               variable_3: value_3,
               variable_4: value_4,
               }

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3, VARIABLE_LABEL_4)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    try:
        while (True):
            main()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nMati")
        GPIO.cleanup()        