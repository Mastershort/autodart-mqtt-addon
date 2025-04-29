import time
import json
import requests
import paho.mqtt.client as mqtt
import threading

# Konfigurationsparameter
api_url = "http://192.168.50.109:3180/api/state"
mqtt_broker = "localhost"
mqtt_topic = "autodart/status"

# MQTT-Client einrichten
client = mqtt.Client()
client.connect(mqtt_broker)

# Funktion zur API-Abfrage
def get_api_data():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Fehler beim Abrufen der API-Daten:", response.status_code)
            return None
    except Exception as e:
        print("Fehler bei der Verbindung zur API:", e)
        return None

# Funktion zum Senden von MQTT-Nachrichten
def send_mqtt_message(data):
    payload = json.dumps(data)
    client.publish(mqtt_topic, payload)
    print(f"Gesendet an MQTT: {payload}")

# Funktion zum regelmäßigen Abrufen und Senden der Daten
def fetch_and_send_data():
    while True:
        data = get_api_data()
        if data:
            send_mqtt_message(data)
        time.sleep(10)  # 10 Sekunden warten, bevor die nächste Anfrage gemacht wird

# Starte das Abrufen der Daten in einem eigenen Thread
def start_service():
    mqtt_thread = threading.Thread(target=fetch_and_send_data)
    mqtt_thread.start()

# Start des Skripts
if __name__ == "__main__":
    start_service()
    client.loop_forever()
