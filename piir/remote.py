import json
from io import IOBase
from .encode import encode
from .io import send

class Remote:
    def __init__(self, data, gpio, active_low=False, duty_cycle=None):
        self.gpio = gpio
        self.active_low = active_low
        self.duty_cycle = duty_cycle

        if isinstance(data, str):
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

    def restore_data(self, data):
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

    def send_pulses(self, pulses, gap, carrier, times):
        send(
            self.gpio,
            pulses,
            active_low = self.active_low,
            duty_cycle = self.duty_cycle,
            carrier = carrier,
            times = times,
            gap = gap,
        )

    def send_data(self, data, times=1):
        pulses, gap, carrier = self.encode(data)
        self.send_pulses(pulses, gap, carrier, times)

    def send(self, key, times=1):
        data = self.keys[key]
        cache = self.cache.get(key)
        if cache:
            pulses, gap, carrier = cache
        else:
            pulses, gap, carrier = self.encode(data)
            self.cache[key] = pulses, gap, carrier
        self.send_pulses(pulses, gap, carrier, times)
