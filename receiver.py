#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import sqlite3
import datetime

# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()

def process_message(client, userdata, message):
    message_decoded = str(message.payload.decode("utf-8"))
    register_mode, card_id = message_decoded.split('-')

    if register_mode == 'True':
        register_card(card_id)
    else:
        log_entry_exit(card_id)
    
    print(message_decoded)


def register_card(card_id):
    connection = sqlite3.connect("instance/gym.db")
    cursor = connection.cursor()

    try:
        # Check if the card is already registered
        cursor.execute("SELECT id FROM client WHERE card_id = ?", (card_id,))
        client = cursor.fetchone()
        if client:
            return
        cursor.execute("INSERT INTO card (card_id) VALUES (?)", (card_id,))

        # Register the card
        connection.commit()
        print("karta zarejestrowana")
        
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def log_entry_exit(card_id):
    print("logowanie wejścia/wyjścia")
    connection = sqlite3.connect("instance/gym.db")
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT status FROM client WHERE card_id = ?", (card_id,))
        client = cursor.fetchone()
        if not client or client[0] == "inactive":
            print("karta nieaktywna")
            return

        cursor.execute("SELECT action FROM log WHERE card_id = ? ORDER BY timestamp DESC LIMIT 1", (card_id,))
        last_log = cursor.fetchone()

        if last_log is None or last_log[0] == 'exit':
           action = 'entry'
        else:
           action = 'exit'

        log_time = int(time.time())
        cursor.execute("INSERT INTO log (card_id, timestamp, action) VALUES (?, ?, ?)", (card_id, log_time, action,))

        cursor.execute("SELECT card_id FROM attendance WHERE card_id = ?", (card_id,))
        attendance = cursor.fetchone()

        if attendance is None:
           cursor.execute("INSERT INTO attendance (card_id, is_present, last_updated) VALUES (?, ?, ?)", (card_id, int(action == 'entry'), log_time,))
        else:
            cursor.execute("UPDATE attendance SET is_present = ?, last_updated = ? WHERE card_id = ?", (int(action == 'entry'), log_time, card_id,))
        print("log zapisany")
        connection.commit()

    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def connect_to_broker():
    # Connect to the broker.
    client.connect(broker)
    # Send message about conenction.
    client.on_message = process_message
    # Starts client and subscribe.
    client.subscribe("worker/card")
    while client.loop() == 0:
        pass


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()
    disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()