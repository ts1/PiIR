# PiIR

![CI](https://github.com/ts1/PiIR/workflows/CI/badge.svg)

IR remote control for Raspberry Pi.

PiIR is a client program for [pigpio](http://abyz.me.uk/rpi/pigpio/), the excellent hardware-timed GPIO library. 
Some code are taken from its sample program `irrp.py`.

## Features
- Records and plays IR remote control code.
- Decodes and encodes NEC, Sony, RC5, RC6, AEHA, Mitsubishi, Sharp and Nokia formats.
- Dumps decoded and prettified data to help you analyze your air conditioner's remote.
- Both command-line and programmatic control.

## Requirements
- Raspberry Pi (any model where pigpio works should work)
- IR LED and/or receiver on GPIO (see [Hardware](#hardware) section)
- Python >= 3.6
- Running pigpiod daemon

## Installation
```sh
sudo pip3 install PiIR
```

Start pigpio daemon.
```sh
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Command line usage

In the following example, the transmit GPIO is 17 and the receive GPIO is 22.
You may need to change them to fit your hardware configuration.

### Recoding

```sh
piir record --gpio 22 --file light.json
```

This asks key names on your remote and to press the keys.
The resulted data is saved to `light.json`.
The file will look like this:

```json
{
  "format": {
    "preamble": [
      8,
      4
    ],
    "coding": "ppm",
    "zero": [
      1,
      1
    ],
    "one": [
      1,
      3
    ],
    "postamble": [
      1
    ],
    "pre_data": "2C 52",
    "timebase": 430,
    "gap": 75000
  },
  "keys": {
    "on": "09 2D 24",
    "off": "09 2F 26",
    "cool": "39 90 A9",
    "warm": "39 91 A8",
    "bright": "09 2A 23",
    "dark": "09 2B 22",
    "full": "09 2C 25",
    "night": "09 2E 27"
  }
}
```

### Playing

```sh
piir play --gpio 17 --file light.json off
```

This sends IR signal for `off` from `light.json`.

### Analyzing

```sh
piir dump --gpio 22
```

This prints decoded data of received signal like this:

```json
{
  "preamble": [
    8,
    4
  ],
  "coding": "ppm",
  "zero": [
    1,
    1
  ],
  "one": [
    1,
    3
  ],
  "postamble": [
    1
  ],
  "pre_data": "01 10 00 40 BF FF 00 CC 33",
  "post_data": "00 FF 80 7F 03 FC 01 FE 88 77 00 FF 00 FF FF 00 FF 00 FF 00 FF 00",
  "byte_by_byte_complement": true,
  "timebase": 420,
  "gap": 49000,
  "data": "92 42 64 00 00 00 00 00 53 F1 00"
}
```

It removes pre/post data and byte-by-byte complement from `data`, so you can focus on the actual data changes.
It shold help analyzing data from stateful remotes such as air conditioners.
An example of programmatic data generation using this result can be found in `piir/remotes`.

For more options try `-h`.

## API

To send an IR signal recorded in a file:

```python
import piir

remote = piir.Remote('light.json', 17)
remote.send('off')
```

You can also send arbitrary data like this:

```python
remote.send_data('09 2E 27')
```

or

```python
remote.send_data(bytes([0x09, 0x2E, 0x27]))
```

TODO: write more

## Hardware

![Photo](https://raw.githubusercontent.com/ts1/PiIR/master/img/photo.jpeg)

I'm using Raspberry Pi Zero WH with four IR LEDs.
Each LED has a measured current of 120mA, switched by a transitor connected to GPIO 17.

On an unrelated note, the big gold thing is a carbon dioxide sensor.

![Schematic of LED](https://raw.githubusercontent.com/ts1/PiIR/master/img/schema-led.png)

Also onboard is a 38KHz IR receiver from Sharp, connected to GPIO 22.

![Schematic of receiver](https://raw.githubusercontent.com/ts1/PiIR/master/img/schema-receiver.png)
