# PiIR

![CI](https://github.com/ts1/PiIR/workflows/CI/badge.svg)

IR remote control for Raspberry Pi.

## Features
- Records and plays IR remote control code.
- Decodes and encodes NEC, Sony, RC5, RC6, AEHA, Mitsubishi, Sharp and Nokia formats.
- Dumps decoded and prettified data to help analyze air conditioner remotes.
- Both command-line and programatic control.

## Requirements
- Raspberry Pi (any model where [pigpio](http://abyz.me.uk/rpi/pigpio/) works should work)
- IR LED and/or receiver on GPIO
- Python >= 3.6

## Installation
```
sudo pip3 install git+https://github.com/ts1/PiIR.git
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
This sends KEY from FILE.

```
piir dump -g GPIO
```
This prints decoded data of received code.

For more options try `-h`.

## API

TBD
