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

Check out [.env](.env) for possible environment variables.

## Running

Simply execute `./pieq.py`.
