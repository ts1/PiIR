from .util import bytes_to_bits

def data_to_binary(code):
    result = []

    pre = code.get('pre_data')
    if pre:
        result += bytes_to_bits(pre, code, code.get('pre_data_bits'))

    result +=  bytes_to_bits(code['data'], code, code.get('bits'))

    post = code.get('post_data')
    if post:
        result += bytes_to_bits(post, code, code.get('post_data_bits'))

    return result

def encode_ppm(code):
    pulses = []
    pulses += code.get('preamble', [])
    data = data_to_binary(code)
    zero = code['zero']
    one = code['one']
    bits = 0
    byte_separator = code.get('byte_separator')
    for bit in data:
        if bit:
            pulses += one
        else:
            pulses += zero
        bits += 1
        if byte_separator and (bits % 8) == 0 and bits < len(data):
            pulses += byte_separator
    pulses += code.get('postamble', [])
    return pulses

def encode_manchester(code):
    levels = []
    level = 1
    for pulse in code.get('preamble', []):
        levels += [level] * pulse
        level = 1 - level

    data = data_to_binary(code)
    zero = code['zero']
    one = code['one']
    long_bit = code.get('long_bit')
    for i, bit in enumerate(data):
        if i == long_bit:
            if bit:
                levels += [one[0], one[0], one[1], one[1]]
            else:
                levels += [zero[0] + zero[0] + zero[1] + zero[1]]
        else:
            if bit:
                levels += one
            else:
                levels += zero

    pulses = []
    level = 1
    pulse = 0
    for l in levels:
        if l != level:
            level = l
            pulses.append(pulse)
            pulse = 0
        pulse += 1
    if pulse:
        pulses.append(pulse)

    return pulses

def encode_raw(code):
    return code['data']

encoders = dict(
    ppm = encode_ppm,
    manchester = encode_manchester,
    raw = encode_raw,
)

def encode_single(code):
    coding = code['coding']
    encoder = encoders.get(coding)
    if not encoder:
        raise ValueError(f'Unknown coding "{coding}"')
    pulses = encoder(code)

    t = code['timebase']
    pulses = [p * t for p in pulses]

    gap = code.get('gap') or 50_000
    if len(pulses) & 1:
        pulses.append(gap)
    else:
        pulses[-1] += gap

    return pulses

def encode(codes):
    pulses = []
    for code in codes:
        pulses += encode_single(code)
    if (len(pulses) & 1) == 0:
        del pulses[-1]
    return pulses
