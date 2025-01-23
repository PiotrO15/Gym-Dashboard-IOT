#!/usr/bin/env python3

from operator import is_
from config import *
import RPi.GPIO as GPIO
import time
from mfrc522 import MFRC522
from datetime import datetime
import paho.mqtt.client as mqtt
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331

terminal_id = "T0"
broker = "localhost"
client = mqtt.Client()
register_mode = True

image_swipe = Image.open('./img/swipe.png')
image_error = Image.open('./img/error.png')
image_success = Image.open('./img/success.png')

def changeLeds(val):
    GPIO.output(led1, val)
    GPIO.output(led2, val)
    GPIO.output(led3, val)
    GPIO.output(led4, val)

def buzzer(state):
    GPIO.output(buzzerPin, not state)

def playSuccess(disp):
    disp.ShowImage(image_success, 0, 0)
    buzzer(True)
    time.sleep(1)
    buzzer(False)
    disp.ShowImage(image_swipe, 0, 0)

def playError(disp):
    disp.ShowImage(image_error, 0, 0)
    buzzer(True)
    time.sleep(0.4)
    buzzer(False)
    time.sleep(0.2)
    buzzer(True)
    time.sleep(0.4)
    buzzer(False)
    disp.ShowImage(image_swipe, 0, 0)

def read():
    MIFAREReader = MFRC522()
    last_card = None
    last_read_time = 0
    
    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()
    
    disp.ShowImage(image_swipe, 0, 0)

    while True:
        updateMode()

        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                num = 0
                current_time = time.time()

                for i in range(0, len(uid)):
                    num += uid[i] << (i*8)

                if not (last_card == num and (current_time - last_read_time) <= 1.5):

                    call_worker(str(num), register_mode)
                    if register_mode:
                        if can_register(str(num)):
                            playSuccess(disp)
                        else:
                            playError(disp)
                    else:
                        if is_active(str(num)):
                            playSuccess(disp)
                        else:
                            playError(disp)

                last_card = num
                last_read_time = current_time

def call_worker(worker_id, register_mode):
   client.publish("worker/card", str(register_mode) + "-" + str(worker_id))

def connect_to_broker():
   client.connect(broker)

def disconnect_from_broker():
   client.disconnect()

def updateMode():
    global register_mode

    if (GPIO.input(buttonRed) == 0):
        register_mode = True
        changeLeds(True)

    if (GPIO.input(buttonGreen) == 0):
        register_mode = False
        changeLeds(False)

def check_status(card_id, condition):
    connection = sqlite3.connect("instance/gym.db")
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT status FROM client WHERE card_id = ?", (card_id,))
        client = cursor.fetchone()

        if condition(client):
            return False

        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

    return True

def can_register(card_id):
    return check_status(card_id, (lambda client: client))

def is_active(card_id):
    return check_status(card_id, (lambda client: not client or client[0] == "inactive"))

if __name__ == "__main__":
    changeLeds(True)
    connect_to_broker()
    read()
    disconnect_from_broker()
    GPIO.cleanup()