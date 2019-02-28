pieq
====

(Raspberry) Pie Indoor Environmental Quality

A service written in Python that makes use of the [Astro Pi Sense HAT](https://www.raspberrypi.org/products/sense-hat/) to measure indoor temperature, humidity and pressure and display relevant information on its 8x8 dot LED matrix.

## Requirements

- Any Raspberry Pi that's compatible with the [Astro Pi Sense HAT](https://www.raspberrypi.org/products/sense-hat/)
- The [Astro Pi Sense HAT](https://www.raspberrypi.org/products/sense-hat/)
- Raspbian installed on the Raspberry Pi

## Installation

- `aptitude update && aptitude upgrade`
- (Optional) Reboot your Raspberry if your kernel was updated.
- `aptitude install sense-hat`
- Copy `pieq.py` onto the Raspberry Pi. (e.g. `scp ./pieq.py user@raspberrypi:~/`)

## Configuration

### Monitoring (via [InfluxDB](https://www.influxdata.com/time-series-platform/influxdb/) and [Grafana](https://grafana.com))

pieq supports sending measurements into InfluxDB and make use of this data through Grafana. In order to enable that, you need to configure the InfluxDB database:

- `INFLUXDB_ENABLED=1`
- `INFLUXDB_HOST=<host>`
- `INFLUXDB_PORT=8086`
- `INFLUXDB_USERNAME=<user or empty>`
- `INFLUXDB_PASSWORD=<password or empty>`
- `INFLUXDB_SSL=1`
- `INFLUXDB_VERIFY_SSL=1`
- `INFLUXDB_DATABASE=<database>`

### Notifications (via [Pushover](https://pushover.net))

In order to enable notifications via Pushover you need to [create a new application on Pushover](https://pushover.net/apps/build).
Then set the following environment variables:

- `PUSHOVER_APP_TOKEN=<The API Token/key of the Pushover application you just created>`
- `PUSHOVER_USER_KEY=<Your Pushover user key>`
- `PUSHOVER_PRIORITY=<Possible values: -2, -1, 0, 1, 2>`
- `PUSHOVER_ENABLED=1`

Also, you need to specify the notification thresholds. Those can be specified through setting `PUSHOVER_THRESHOLDS_TEMPERATURE`, `PUSHOVER_THRESHOLDS_HUMIDITY` and `PUSHOVER_THRESHOLDS_PRESSURE`. The format looks identical for each of those: `<minimum>,<maximum>`. 

Example: `PUSHOVER_THRESHOLDS_TEMPERATURE=20,30`

In this case, you'd receive a pushover notification as soon as the temperature drops beneath 20 degrees (celsius) and as soon as the temperature rises above 30 degrees (celsius).

## Run manually

Set all necessary environment variables and execute `./pieq.py`.

## Run on boot

In order to run pieq on boot you need to perform a few steps on your Raspberry Pi:

```bash
# Execute these commands ON YOUR RASPBERRY PI
su - # or sudo su -
cd /path/to/the/local/copy/of/this/repo
cp ./pieq.py /usr/local/bin/pieq.py
cp ./pieq /etc/init.d/pieq
cp ./.env /etc/pieq
vi /etc/pieq # and edit to your needs
update-rc.d pieq defaults
```

Now you can reboot your Raspberry with pieq being automatically run.

## Feedback

Feel free to [tweet me](https://twitter.com/mrusme) if you have feedback to share!
