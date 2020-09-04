import json, os
from time import time, sleep
from io import IOBase
from .encode import encode
from .io import send
from .util import bytes_to_bits, bits_to_bytes

class Remote:
    def __init__(self, data, gpio, active_low=False, duty_cycle=None):
        self.gpio = gpio
        self.active_low = active_low
        self.duty_cycle = duty_cycle
        self.last_sent = 0

        if isinstance(data, (str, os.PathLike)):
            data = open(data)

        if isinstance(data, IOBase):
            data = json.load(data)

        self.load(data)

    def load(self, data):
        self.formats = data.get('formats')
        if not self.formats:
            self.formats = [data['format']]
        self.keys = data['keys']
        self.cache = {}

    def restore_data(self, data, restore_data=True):
        if not isinstance(data, list):
            data = [data]
        result = []
        for part in data:
            if isinstance(part, dict):
                d = part['data']
                format = part['format']
            else:
                d = part
                format = 0

            if isinstance(d, str):
                d = bytes.fromhex(d)

            r = self.formats[format].copy()

            if restore_data and r['coding'] != 'raw':
                pre = r.get('pre_data')
                if pre: r['pre_data'] = bytes.fromhex(pre)

                post = r.get('post_data')
                if post: r['post_data'] = bytes.fromhex(post)

                if r.get('byte_by_byte_complement'):
                    d = bytes(sum(zip(d, (byte ^ 0xff for byte in d)), ()))

            r['data'] = d

            result.append(r)
        return result

    def encode(self, data):
        data = self.restore_data(data)
        pulses = encode(data)
        gap = data[-1].get('gap')
        carrier = data[-1].get('carrier')
        return pulses, gap, carrier

    def send_pulses(self, pulses, gap, carrier, repeat):
        t = gap / 1e6 - (time() - self.last_sent)
        if t > 0:
            sleep(t)
        self.last_sent = time()
        send(
            self.gpio,
            pulses,
            active_low = self.active_low,
            duty_cycle = self.duty_cycle,
            carrier = carrier,
            repeat = repeat,
            gap = gap,
        )

    def send_data(self, data, repeat=1):
        pulses, gap, carrier = self.encode(data)
        self.send_pulses(pulses, gap, carrier, repeat)

    def send(self, key, repeat=1):
        data = self.keys[key]
        cache = self.cache.get(key)
        if cache:
            pulses, gap, carrier = cache
        else:
            pulses, gap, carrier = self.encode(data)
            self.cache[key] = pulses, gap, carrier
        self.send_pulses(pulses, gap, carrier, repeat)

    def unprettify(self):
        result = {}
        for name, data in self.keys.items():
            parts = self.restore_data(data)
            r_parts = []
            for part in parts:
                r = part.copy()
                if part['coding'] == 'raw':
                    r['data'] = (
                        part.get('pre_data', []) +
                        part['data'] +
                        part.get('post_data', [])
                    )
                else:
                    bits = []

                    pre = part.get('pre_data')
                    if pre:
                        bits += bytes_to_bits(
                            pre,
                            part,
                            part.get('pre_data_bits'),
                        )

                    bits += bytes_to_bits(part['data'], part)

                    post = part.get('post_data')
                    if post:
                        bits += bytes_to_bits(
                            post,
                            part,
                            part.get('post_data_bits'),
                        )

                    r['data'] = bits_to_bytes(bits, part.get('msb_first'))
                    r['bits'] = (
                        part.get('pre_data_bits', 0) +
                        part.get('bits', len(part['data']) * 8) +
                        part.get('post_data_bits', 0)
                    )
                r.pop('pre_data', None)
                r.pop('pre_data_bits', None)
                r.pop('post_data', None)
                r.pop('post_data_bits', None)
                r.pop('byte_by_byte_complement', None)
                r_parts.append(r)
            result[name] = r_parts
        return result
