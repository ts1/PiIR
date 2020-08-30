# Hitachi air conditioner remote RAR-8P2

from ..remote import Remote

class Hitachi_RAR_8P2:
    format = {
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
        "pre_data": "01 10 00 40 BF FF 00 CC 33",
        "post_data": "03 FC 01 FE 88 77 00 FF 00 FF FF 00 FF 00 FF 00 FF 00",
        "byte_by_byte_complement": True,
        "timebase": 420,
        "gap": 49000
      },
      "keys": {}
    }

    power = False
    mode = 'blow'
    temperature = 24
    air_speed = 'auto'
    power_saving = False
    clean_inside = False

    def __init__(self, gpio):
        self.remote = Remote(self.format, gpio)

    def send(self):
        data = []
        if self.air_speed == 1:
            data.append(0x98)
        elif self.clean_inside:
            data.append(0xA3)
        elif self.air_speed == 5:
            data.append(0xA9)
        else:
            data.append(0x92)

        data.append(0x13)
        data.append(self.temperature * 4)
        data += [0] * 5

        if self.mode == 'blow':
            d = 1
        elif self.mode == 'cool':
            d = 3
        elif self.mode == 'dry':
            d = 5
        elif self.mode == 'heat':
            d = 6
        else:
            raise ValueError('mode must be one of blow, cool, dry or heat')

        if self.air_speed == 'auto':
            d |= 0x50
        elif self.air_speed <= 4:
            d |= self.air_speed * 0x10
        elif self.air_speed == 5:
            d |= 0x60
        else:
            raise ValueError('air_speed must be 1 to 5 or "auto"')
        data.append(d)

        if self.power:
            d = 0xf0
        else:
            d = 0xe0
        if not self.power_saving:
            d |= 1
        data.append(d)

        if self.air_speed == 5:
            data.append(3)
        else:
            data.append(0)

        data.append(0)

        if self.clean_inside:
            data.append(0x88)
        else:
            data.append(0x80)

        self.remote.send_data(bytes(data))
