# PiIR

![CI](https://github.com/ts1/PiIR/workflows/CI/badge.svg)

IR remote control for Raspberry Pi.

PiIR is a client program for [pigpio](http://abyz.me.uk/rpi/pigpio/), the excellent hardware-timed GPIO library. 
Some code are taken from its sample program `irrp.py`.

## Features
- Records and plays IR remote control code.
- Decodes and encodes NEC, Sony, RC5, RC6, AEHA, Mitsubishi, Sharp and Nokia formats.
- Dumps decoded and prettified data to help you analyze your air conditioner's remote.
- Both command-line and programatic control.

## Requirements
- Raspberry Pi (any model where pigpio works should work)
- IR LED and/or receiver on GPIO (see [Hardware](#hardware) section)
- Python >= 3.6
- Running `pigpiod` daemon

## Installation
```
sudo pip3 install git+https://github.com/ts1/PiIR.git
```

Start pigpio daemon.
```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Command line usage
```
piir record -g GPIO -f FILE
```
This asks key names on your remote and to press the keys.
The resulted data is saved to FILE.

```
piir play -g GPIO -f FILE KEY
```
This sends IR signal for KEY from FILE.

```
piir dump -g GPIO
```
This prints decoded data of received code.

For more options try `-h`.

## API

To send an IR signal recorded in a file:

```
import piir

remote = piir.Remote('FILE', GPIO)
remote.send('KEY')
```

TODO: write more

## Hardware

![Photo](https://raw.githubusercontent.com/ts1/PiIR/master/img/photo.jpeg)

I'm using Raspberry Pi Zero WH with four IR LEDs.
Each LED has a measured current of 120mA, switched by a transitor connected to GPIO 17.

![Schematic of LED](https://raw.githubusercontent.com/ts1/PiIR/master/img/schema-led.png)

Also onboard is a 38KHz IR receiver from Sharp, connected to GPIO 22.

![Schematic of receiver](https://raw.githubusercontent.com/ts1/PiIR/master/img/schema-receiver.png)

Unrelated, but the big gold one is a CO2 sensor.
