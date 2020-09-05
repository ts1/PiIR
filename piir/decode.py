import math
from .util import bits_to_bytes

def round_to_2_digits(x):
    if not x: return x
    if x < 0: return -round_to_2_digits(abs(x))
    frac = 1 - math.floor(math.log10(x))
    y = round(x, frac)
    if frac <= 0:
        return int(y)
    return y

def split_pulses(pulses, min_gap, min_pulses):
    parts = []
    part = []
    gaps = []

    for i, pulse in enumerate(pulses):
        if (i & 1) and pulse >= min_gap:
            gaps.append(pulse)
            if len(part) >= min_pulses:
                parts.append(part)
            part = []
        else:
            part.append(pulse)
    if len(part) >= min_pulses:
        parts.append(part)

    if gaps:
        gap = sorted(gaps)[len(gaps) // 2]
    else:
        gap = None

    return parts, gap

def min_pulse(pulses, tolerance):
    groups = []
    max_pulse = None
    n = 0
    total = 0
    sorted_pulses = sorted(pulses)
    max_pulse = sorted_pulses[0] * (1 + 2 * tolerance)
    for pulse in sorted_pulses:
        if pulse > max_pulse:
            if n >= 3:
                break
            else:
                n = 0
                total = 0
                max_pulse = pulse * (1 + 2 * tolerance)
        n += 1
        total += pulse
    if not n:
        return 0
    return total / n

def try_to_quantize(parts, tolerance, timebase, deviation, strict):
    result = []
    for part in parts:
        result_part = []
        for i, pulse in enumerate(part):
            if i & 1:
                pulse += deviation
            else:
                pulse -= deviation
            f = pulse / timebase
            n = int(round(f))
            if n <= 0:
                return None
            e = abs(f - n)
            if strict:
                if e > tolerance:
                    return None
            else:
                if e > tolerance * n:
                    return None
            result_part.append(n)
        result.append(result_part)
    return result

def quantize(parts, tolerance):
    marks = []
    spaces = []
    for part in parts:
        marks += part[0::2]
        spaces += part[1::2]
    min_mark = min_pulse(marks, tolerance)
    min_space = min_pulse(spaces, tolerance)

    for strict in (True, False):
        min_dev = float('infinity')
        best = None
        for m_len, s_len in ((1, 1), (1, 2), (2, 1)):
            timebase = (min_mark + min_space) / (m_len + s_len)
            deviation = (
                (min_mark - timebase * m_len) +
                (timebase * s_len - min_space)
            ) / 2
            result = try_to_quantize(
                parts,
                tolerance,
                timebase,
                deviation,
                strict,
            )
            if not result: continue
            if abs(deviation) < min_dev:
                min_dev = abs(deviation)
                best = timebase, result
        if best:
            return best

    # Failed to quantize
    return 1, parts

def remove_repeats(parts):
    i = len(parts) - 1
    while i > 0:
        if parts[i] == parts[i - 1]:
            del parts[i]
        i -= 1

# Pulse Position Modulation
def decode_ppm(pulses, msb_first=False):
    preamble = []
    for pre, pulse in enumerate(pulses):
        if pulse == 1:
            break
        preamble.append(pulse)
    if len(preamble) >= len(pulses):
        return None

    codes = set()
    for i in range(pre, len(pulses) - 1, 2):
        pair = pulses[i], pulses[i+1]
        codes.add(pair)
        if len(codes) >= 2:
            break
    if len(codes) != 2: return None

    zero, one = sorted(codes)
    bits = []
    byte_separator = None
    for i in range(pre, len(pulses) - 1, 2):
        pair = pulses[i], pulses[i+1]
        if pair == one:
            bits.append(1)
        elif pair == zero:
            bits.append(0)
        elif pair != zero:
            if len(bits) % 8 == 0:
                byte_separator = pair
                continue
            break
    else:
        i += 2

    if len(bits) < 5:
        return None

    postamble = pulses[i:]
    return dict(
        preamble = preamble,
        coding = 'ppm',
        zero = list(zero),
        one = list(one),
        byte_separator = byte_separator,
        msb_first = msb_first,
        bits = len(bits),
        data = bits_to_bytes(bits, msb_first),
        postamble = postamble,
    )

# Manchester coding
def decode_manchester(
    pulses,
    skip,
    preamble,
    msb_first = True,
    zero = (0, 1),
    one = (1, 0),
    long_bit = None,
):
    levels = []
    level = 0
    for pulse in pulses:
        level = 1 - level
        levels += [level] * pulse
    levels = levels[skip:]
    if len(levels) & 1:
        levels.append(0)

    if long_bit is not None:
        if len(levels) <= long_bit * 2 + 1:
            return None
        del levels[(long_bit + 1) * 2]
        del levels[long_bit * 2]

    bits = []
    for i in range(0, len(levels) - 1, 2):
        pair = levels[i], levels[i+1]
        if pair == one:
            bits.append(1)
        elif pair == zero:
            bits.append(0)
        else:
            return None

    return dict(
        preamble = preamble,
        coding = 'manchester',
        zero = list(zero),
        one = list(one),
        long_bit = long_bit,
        msb_first = msb_first,
        bits = len(bits),
        data = bits_to_bytes(bits, msb_first),
    )

def decode_raw(pulses):
    return dict(coding='raw', data=pulses)

def decode(
    pulses,
    min_gap = 15_000,
    tolerance = 0.2,
    min_pulses = 10,
):
    if len(pulses) < min_pulses:
        return None

    if (len(pulses) & 1) == 0:
        return None

    parts, gap = split_pulses(pulses, min_gap, min_pulses)
    if not parts:
        return None

    timebase, parts = quantize(parts, tolerance)
    if timebase == 1:
        return None
    remove_repeats(parts)

    results = []
    for part in parts:
        result = decode_ppm(part)
        if not result:
            if part[:3] == ([6, 2, 1]):
                # RC6
                result = decode_manchester(part, 10, [6, 2, 1, 1], long_bit=3)
            elif part[:3] == [1, 5, 1]:
                # NOKIA
                result = decode_manchester(
                    part,
                    8,
                    [1, 5, 1, 1],
                    msb_first = False,
                )
            else:
                # RC5
                result = decode_manchester(
                    part,
                    1,
                    [1],
                    zero = (1, 0),
                    one = (0, 1)
                )
        if not result:
            result = decode_raw(part)
        results.append(result)

    timebase = round_to_2_digits(timebase)
    gap = round_to_2_digits(gap)

    for result in results:
        result['timebase'] = timebase
        result['gap'] = gap

    return results
