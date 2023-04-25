import board
import time
import os

import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT

import adafruit_sht4x

secrets = {
    "wifi": os.getenv("wifi_ssid"),
    "wifi_pwd": os.getenv("wifi_pwd"),
    "aio_username": os.getenv("aio_username"),
    "aio_key": os.getenv("aio_key")
}

# Setup a simple sensor
sht = adafruit_sht4x.SHT4x(board.STEMMA_I2C())
sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

# Setup a feed named 'temperaturesensor' for publishing
temperaturesensor_feed = secrets["aio_username"] + "/feeds/temperaturesensor"

# This is the modern CircuitPython MQTT code init sequence. No need to pass a socket, requests or other things previous versions required
wifi.radio.connect(secrets["wifi"], secrets["wifi_pwd"])
pool = socketpool.SocketPool(wifi.radio)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print("Feed {0} received new value: {1}".format(feed_id, payload))

mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Note: I found the sample code that set on_connect caused an error on connect(). This issue needs investigation
mqtt_client.on_message = message

mqtt_client.connect()

while True:
    temperature, relative_humidity = sht.measurements

    mqtt_client.loop()
    print("Sending temperaturesensor value: %d..." % temperature)
    mqtt_client.publish(temperaturesensor_feed, temperature)
    print("Sent!")
    time.sleep(10)
