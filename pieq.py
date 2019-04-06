#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import os
import sys
import time
import _thread
import http.client
import socket
import json

client_influxdb = None
if os.getenv("INFLUXDB_ENABLED", "0") == "1":
    from influxdb import InfluxDBClient

    influxdb_host = os.getenv("INFLUXDB_HOST", "localhost")
    influxdb_port = int(os.getenv("INFLUXDB_PORT", "8086"))
    influxdb_user = os.getenv("INFLUXDB_USERNAME", "root")
    influxdb_pass = os.getenv("INFLUXDB_PASSWORD", "root")
    influxdb_ssl = (os.getenv("INFLUXDB_SSL", "1") == "1")
    influxdb_vssl = (os.getenv("INFLUXDB_VERIFY_SSL", "1") == "1")
    influxdb_db = os.getenv("INFLUXDB_DATABASE", None)
    client_influxdb = InfluxDBClient( \
        host=influxdb_host, \
        port=influxdb_port, \
        username=influxdb_user, \
        password=influxdb_pass, \
        database=influxdb_db, \
        ssl=influxdb_ssl, \
        verify_ssl=influxdb_vssl \
    )

import urllib
from sense_hat import SenseHat

views = [
    "temperature",
    "humidity",
    "pressure",
    "thp"
]

lock_ui = _thread.allocate_lock()
lock_measures = _thread.allocate_lock()
lock_orientation = _thread.allocate_lock()
lock_animation_run = _thread.allocate_lock()

current_view = 0
measures = {}
orientation = 0

leds_number = 8
temperature_max = 40
temperature_min = 0
temperature_scale = temperature_max - temperature_min
temperature_step = int(round(temperature_scale / leds_number))

humidity_max = 100
humidity_min = 0
humidity_scale = humidity_max - humidity_min
humidity_step = int(round(humidity_scale / leds_number))

pressure_max = 232 # so that the usual pressure of 101 kPa results in 4 leds lighting up
pressure_min = 30 # ... if anyone should be interested in running this on the top of Mount Everest
pressure_scale = pressure_max - pressure_min
pressure_step = int(round(pressure_scale / leds_number))

x = [100, 205, 246]
o = [0, 0, 0]

wave_animation = [
    [
        o,o,o,o,o,o,o,o,
        o,o,o,x,x,o,o,o,
        o,o,x,x,x,x,o,o,
        x,x,x,o,o,x,x,x,
        x,x,o,o,o,o,x,x,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,x,x,o,o,o,o,
        o,x,x,x,x,o,o,o,
        x,x,o,o,x,x,x,o,
        x,o,o,o,o,x,x,x,
        o,o,o,o,o,o,o,x,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,x,x,o,o,o,o,o,
        x,x,x,x,o,o,o,o,
        x,o,o,x,x,x,o,o,
        o,o,o,o,x,x,x,o,
        o,o,o,o,o,o,x,x,
        o,o,o,o,o,o,o,x,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        x,x,o,o,o,o,o,o,
        x,x,x,o,o,o,o,o,
        o,o,x,x,x,o,o,o,
        o,o,o,x,x,x,o,o,
        o,o,o,o,o,x,x,x,
        o,o,o,o,o,o,x,x,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        x,o,o,o,o,o,o,o,
        x,x,o,o,o,o,o,o,
        o,x,x,x,o,o,o,o,
        o,o,x,x,x,o,o,x,
        o,o,o,o,x,x,x,x,
        o,o,o,o,o,x,x,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        x,o,o,o,o,o,o,o,
        x,x,x,o,o,o,o,x,
        o,x,x,x,o,o,x,x,
        o,o,o,x,x,x,x,o,
        o,o,o,o,x,x,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        x,x,o,o,o,o,x,x,
        x,x,x,o,o,x,x,x,
        o,o,x,x,x,x,o,o,
        o,o,o,x,x,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,x,
        x,o,o,o,o,x,x,x,
        x,x,o,o,x,x,x,o,
        o,x,x,x,x,o,o,o,
        o,o,x,x,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,x,
        o,o,o,o,o,o,x,x,
        o,o,o,o,x,x,x,o,
        x,o,o,x,x,x,o,o,
        x,x,x,x,o,o,o,o,
        o,x,x,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,x,x,
        o,o,o,o,o,x,x,x,
        o,o,o,x,x,x,o,o,
        o,o,x,x,x,o,o,o,
        x,x,x,o,o,o,o,o,
        x,x,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,x,x,o,
        o,o,o,o,x,x,x,x,
        o,o,x,x,x,o,o,x,
        o,x,x,x,o,o,o,o,
        x,x,o,o,o,o,o,o,
        x,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],[
        o,o,o,o,o,o,o,o,
        o,o,o,o,x,x,o,o,
        o,o,o,x,x,x,x,o,
        o,x,x,x,o,o,x,x,
        x,x,x,o,o,o,o,x,
        x,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ]
]

wifi_animation = [
    [
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o
    ],
    [
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,x,x,o,o,o,
        o,o,x,x,x,x,o,o
    ],
    [
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,o,o,o,o,o,o,
        o,o,x,x,x,x,o,o,
        o,x,x,x,x,x,x,o,
        o,x,o,o,o,o,x,o,
        o,o,o,x,x,o,o,o,
        o,o,x,x,x,x,o,o
    ],
    [
        o,x,x,x,x,x,x,o,
        x,x,x,x,x,x,x,x,
        x,o,o,o,o,o,o,x,
        o,o,x,x,x,x,o,o,
        o,x,x,x,x,x,x,o,
        o,x,o,o,o,o,x,o,
        o,o,o,x,x,o,o,o,
        o,o,x,x,x,x,o,o
    ]
]

gradients = {
    "blue": [
        [6, 36, 61],
        [9, 52, 83],
        [10, 70, 109],
        [10, 96, 148],
        [8, 118, 182],
        [3, 141, 218],
        [0, 165, 253],
        [0, 180, 255]
    ],
    "red": [
        [61, 14, 11],
        [91, 19, 15],
        [120, 24, 20],
        [149, 27, 22],
        [188, 33, 27],
        [218, 38, 31],
        [254, 43, 34],
        [255, 0, 0]
    ],
    "yellow": [
        [79, 70, 19],
        [105, 93, 21],
        [132, 115, 25],
        [152, 128, 15],
        [179, 151, 15],
        [205, 172, 14],
        [230, 192, 6],
        [252, 209, 0]
    ]
}

def get_level(color, lvl):
    level = []

    for i in range(7, -1, -1):
        if i < lvl:
            level.extend((o, o, o, gradients[color][i], gradients[color][i], o, o, o))
        else:
            level.extend((o, o, o, o, o, o, o, o))
    return level

def get_level_trio(color1, lvl1, color2, lvl2, color3, lvl3):
    level = []

    for i in range(7, -1, -1):
        if i < lvl1:
            level.extend((gradients[color1][i], gradients[color1][i], o))
        else:
            level.extend((o, o, o))

        if i < lvl2:
            level.extend((gradients[color2][i], gradients[color2][i], o))
        else:
            level.extend((o, o, o))

        if i < lvl3:
            level.extend((gradients[color3][i], gradients[color3][i]))
        else:
            level.extend((o, o))

    return level

def animate_wifi():
    iterator = 0
    while iterator < len(wifi_animation):
        sense.set_pixels(wifi_animation[iterator])
        iterator += 1
        time.sleep(.2)

def animate_wave():
    iterator = 0
    while iterator < len(wave_animation):
        sense.set_pixels(wave_animation[iterator])
        iterator += 1
        time.sleep(.1)

def client_influxdb_send(json_data):
    return client_influxdb.write_points(json_data)

def http_post(host, route, data, headers):
    connection = http.client.HTTPSConnection(host)

    connection.request('POST', route, data, headers)

    response = connection.getresponse()
    print(response.read().decode())
    return response.status

def client_pushover_send(title, message):
    return http_post(
        "api.pushover.net",
        "/1/messages.json",
        urllib.parse.urlencode({
            "token": os.getenv("PUSHOVER_APP_TOKEN"),
            "user": os.getenv("PUSHOVER_USER_KEY"),
            "priority": os.getenv("PUSHOVER_PRIORITY"),
            "title": title,
            "message": message
        }),
        { "Content-type": "application/x-www-form-urlencoded" }
    )

# "Borrowed" from https://github.com/johnwargo/pi_weather_station
def get_cpu_temperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return float(res.replace("temp=", "").replace("'C\n", ""))

# "Borrowed" from https://github.com/johnwargo/pi_weather_station
def get_smooth(x):
    if not hasattr(get_smooth, "t"):
        get_smooth.t = [x, x, x]
    get_smooth.t[2] = get_smooth.t[1]
    get_smooth.t[1] = get_smooth.t[0]
    get_smooth.t[0] = x
    xs = (get_smooth.t[0] + get_smooth.t[1] + get_smooth.t[2]) / 3
    return xs

# "Borrowed" from https://github.com/johnwargo/pi_weather_station
def get_calculated_temperature():
    temperature_from_humidity = sense.get_temperature_from_humidity()
    temperature_from_pressure = sense.get_temperature_from_pressure()
    temperature_average = (temperature_from_humidity + temperature_from_pressure) / 2
    cpu_temperature = get_cpu_temperature()
    real_temperature = temperature_average - ((cpu_temperature - temperature_average) / 1.5)
    real_temperature = get_smooth(real_temperature)
    return real_temperature

def map_direction_to_orientation(direction, angle):
    direction_at_orientation_map = {
        "0": {
            "left": "left",
            "right": "right",
            "up": "up",
            "down": "down",
            "middle": "middle"
        },
        "90": {
            "left": "down",
            "right": "up",
            "up": "left",
            "down": "right",
            "middle": "middle"
        },
        "180": {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
            "middle": "middle"
        },
        "270": {
            "left": "up",
            "right": "down",
            "up": "right",
            "down": "left",
            "middle": "middle"
        }
    }

    return direction_at_orientation_map[str(angle)][direction]

def navigate(mapped_direction):
    global current_view

    if mapped_direction == "right":
        current_view += 1
    elif mapped_direction == "left":
        current_view -= 1

    if current_view == len(views):
        current_view = 0
    elif current_view < 0:
        current_view = len(views) - 1

    return current_view

def render_temperature(measures):
    global temperature_step
    lvl = int(round(measures["temperature"] / temperature_step))
    sense.set_pixels(get_level("red", lvl))

def render_temperature_clicked(measures):
    sense.show_message(str(measures["temperature"]) + "C")

def render_humidity(measures):
    global humidity_step
    lvl = int(round(measures["humidity"] / humidity_step))
    sense.set_pixels(get_level("blue", lvl))

def render_humidity_clicked(measures):
    sense.show_message(str(measures["humidity"]) + "%")

def render_pressure(measures):
    global pressure_step
    lvl = int(round(measures["pressure"] / pressure_step))
    sense.set_pixels(get_level("yellow", lvl))

def render_pressure_clicked(measures):
    sense.show_message(str(measures["pressure"]) + "kPa")

def render_thp(measures):
    global temperature_step
    lvl1 = int(round(measures["temperature"] / temperature_step))
    global humidity_step
    lvl2 = int(round(measures["humidity"] / humidity_step))
    global pressure_step
    lvl3 = int(round(measures["pressure"] / pressure_step))

    levels = get_level_trio("red", lvl1, "blue", lvl2, "yellow", lvl3)
    sense.set_pixels(levels)

def render_thp_clicked(measures):
    render_temperature_clicked(measures)
    render_humidity_clicked(measures)
    render_pressure_clicked(measures)

def render_none(measures):
    sense.clear()

def render_none_clicked(measures):
    render_temperature_clicked(measures)
    render_humidity_clicked(measures)
    render_pressure_clicked(measures)

def render(measures, direction):
    global current_view

    if measures == {}:
        return False

    renderfn = "render_" + views[current_view]

    if direction == "middle":
        renderfn = renderfn + "_clicked"
    elif direction == "down":
        if sense.low_light == False:
            sense.low_light = True
        else:
            sense.low_light = False

    set_orientation()

    if lock_ui.locked() == True:
        return False

    lock_ui.acquire()
    globals()[renderfn](measures)
    lock_ui.release()
    return True

def get_measures():
    calculated_temperature = get_calculated_temperature()
    temperature = round(calculated_temperature, 1)
    humidity = round(sense.get_humidity(), 0)
    pressure = round(sense.get_pressure() / 10, 1)
    print("Temp: %s C, Humidity: %s% %, Pressure: %s kPa" % (temperature, humidity, pressure))
    return {
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }

def set_measures():
    global measures
    lock_measures.acquire()
    measures = get_measures()
    lock_measures.release()

def get_orientation():
    angle = 0
    orientation = sense.get_accelerometer_raw()
    accel_x = orientation['x']
    accel_y = orientation['y']
    accel_z = orientation['z']

    accel_rnd_x = int(round(accel_x, 0))
    accel_rnd_y = int(round(accel_y, 0))
    accel_rnd_z = int(round(accel_z, 0))

    if accel_rnd_x == 0 and accel_rnd_y == 1 and accel_rnd_z == 0:
        angle = 0
    elif accel_rnd_x == -1 and accel_rnd_y == 0 and accel_rnd_z == 0:
        angle = 90
    elif accel_rnd_x == 0 and accel_rnd_y == -1 and accel_rnd_z == 0:
        angle = 180
    elif accel_rnd_x == 1 and accel_rnd_y == 0 and accel_rnd_z == 0:
        angle = 270

    return angle

def set_orientation():
    global orientation
    lock_orientation.acquire()
    orientation = get_orientation()
    sense.set_rotation(orientation, False)
    lock_orientation.release()

def run():
    global measures
    global orientation

    while 1:
        lock_measures.acquire()
        render(measures, "none")
        lock_measures.release()
        time.sleep(5)

def ping(host):
    while os.system("ping -c 1 " + host + " > /dev/null") != 0:
        print("Could not reach " + host + ", retrying in 5 ...")
        time.sleep(5)

def thread_measure():
    global measures

    while 1:
        measures = get_measures()
        time.sleep(5)

def thread_input():
    global measures

    while 1:
        event = sense.stick.wait_for_event()
        print("The joystick was {} {}".format(event.action, event.direction))
        if event.action == "released":
            navigate(map_direction_to_orientation(event.direction, orientation))
            lock_measures.acquire()
            set_orientation()
            render(measures, map_direction_to_orientation(event.direction, orientation))
            lock_measures.release()

def thread_animation(animation_name):
    animations = {
        "wave": animate_wave,
        "wifi": animate_wifi
    }

    set_orientation()

    lock_ui.acquire()
    while not lock_animation_run.acquire(False):
        animations.get(animation_name, "Invalid animation")()
    lock_ui.release()
    _thread.exit()

def notify_influxdb(measures):
    global orientation
    json_data = []

    if os.getenv("INFLUXDB_ENABLED") != "1":
        return False

    for measurement in measures:
        json_data.append({
            "measurement": "pieq-" + measurement,
            "tags": {
                "host": socket.gethostname(),
                "orientation": orientation
            },
            "time": datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(),
            "fields": {
                measurement: measures[measurement]
            }
        })

    return client_influxdb_send(json_data)

def notify_pushover(measures, conditions):
    if conditions is None:
        conditions = {}

    if os.getenv("PUSHOVER_ENABLED") != "1":
        return conditions

    for measurement in measures:
        envvar_name = "PUSHOVER_THRESHOLDS_" + measurement.upper()
        threshold_values = os.getenv(envvar_name).rsplit(",")

        if len(threshold_values) == 2 \
            and conditions.get(measurement, { "only_after": datetime.datetime.now() }).get("only_after") < datetime.datetime.now() \
            and (measures[measurement] < float(threshold_values[0]) or measures[measurement] > float(threshold_values[1])):
            client_pushover_send(measurement.capitalize(), "Current " + measurement + " is: " + str(measures[measurement]))
            conditions[measurement] = {
                "only_after": (datetime.datetime.now() + datetime.timedelta(minutes=30))
            }
    return conditions

def thread_notify():
    global measures
    conditions_pushover = {}

    while 1:
        lock_measures.acquire()
        notify_influxdb(measures)
        conditions_pushover = notify_pushover(measures, conditions_pushover)
        lock_measures.release()
        time.sleep(5)

def main():
    sense.set_imu_config(False, False, True)
    sense.low_light = False
    sense.clear()

    lock_animation_run.acquire()
    _thread.start_new_thread(thread_animation, ("wifi",))
    ping("google.com")
    lock_animation_run.release()

    _thread.start_new_thread(thread_measure, ())
    _thread.start_new_thread(thread_input, ())
    _thread.start_new_thread(thread_notify, ())
    run()
    print("Leaving main()")

try:
    print("Initializing the Sense HAT client")
    sense = SenseHat()

    sense.clear()
except:
    print("Unable to initialize the Sense HAT library:", sys.exc_info()[0])
    sys.exit(1)

print("Initialization complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sense.clear()
        print("\nExit\n")
        sys.exit(0)
