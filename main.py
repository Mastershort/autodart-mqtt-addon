import tkinter as tk
import threading
import time
import json
import requests
import paho.mqtt.client as mqtt
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("API ➜ MQTT Sender")
        self.running = False

        # Laden der gespeicherten Konfiguration
        self.load_config()

        # API IP & Port
        tk.Label(root, text="API IP (z.B. 192.168.1.10:3180)").pack()
        self.api_ip = tk.Entry(root)
        self.api_ip.insert(0, self.api_ip_value)
        self.api_ip.pack()

        # MQTT-Broker
        tk.Label(root, text="MQTT Broker (z.B. 192.168.1.50)").pack()
        self.broker = tk.Entry(root)
        self.broker.insert(0, self.broker_value)
        self.broker.pack()

        # MQTT-Topic
        tk.Label(root, text="MQTT Topic (z.B. sensor/data)").pack()
        self.topic = tk.Entry(root)
        self.topic.insert(0, self.topic_value)
        self.topic.pack()

        # Intervall
        tk.Label(root, text="Intervall (Sekunden)").pack()
        self.interval = tk.Entry(root)
        self.interval.insert(0, str(self.interval_value))
        self.interval.pack()

        # Start/Stop-Button
        self.button = tk.Button(root, text="Start", command=self.toggle)
        self.button.pack(pady=10)

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
                self.api_ip_value = config.get("api_ip", "")
                self.broker_value = config.get("broker", "")
                self.topic_value = config.get("topic", "")
                self.interval_value = config.get("interval", 5)
        else:
            # Standardwerte, wenn keine Konfiguration vorhanden ist
            self.api_ip_value = ""
            self.broker_value = ""
            self.topic_value = ""
            self.interval_value = 5

    def save_config(self):
        config = {
            "api_ip": self.api_ip.get(),
            "broker": self.broker.get(),
            "topic": self.topic.get(),
            "interval": int(self.interval.get())
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    def toggle(self):
        if not self.running:
            self.running = True
            self.button.config(text="Stop")
            threading.Thread(target=self.loop).start()
        else:
            self.running = False
            self.button.config(text="Start")
            # Speichern der Konfiguration bei Stopp
            self.save_config()

    def loop(self):
        while self.running:
            try:
                # URL der API (mit der IP und dem Port)
                url = f"http://{self.api_ip.get()}/api/state"
                
                # Sende GET-Anfrage an die API
                response = requests.get(url)
                
                # Wenn die Antwort erfolgreich ist (Statuscode 200)
                if response.status_code == 200:
                    # Parse die JSON-Daten aus der Antwort
                    data = response.json()

                    # Verbinde mit dem MQTT-Broker und sende die Daten
                    client = mqtt.Client()
                    client.connect(self.broker.get(), 1883, 60)
                    client.publish(self.topic.get(), json.dumps(data))
                    client.disconnect()

                    print("Daten gesendet:", data)
                else:
                    print(f"Fehler beim Abrufen der API-Daten: {response.status_code}")

            except Exception as e:
                print("Fehler:", e)

            # Warte für das angegebene Intervall (in Sekunden)
            time.sleep(int(self.interval.get()))


root = tk.Tk()
app = App(root)
root.mainloop()
