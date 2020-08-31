from .util import bytes_to_bits, bits_to_bytes, hexify

def most_frequent(xs):
    d = {}
    for x in xs:
        d.setdefault(x, 0)
        d[x] += 1
    max = 0
    result = None
    for value, count in d.items():
        if count > max:
            max = count
            result = value
    return result

def find_pre_post(format, data):
    bitwise = format.get('bits', 0) % 8 != 0

    if bitwise:
        data = [bytes_to_bits(d, format) for d in data]

    pre = data[0]
    post = data[0]
    for d in data[1:]:
        for i in range(len(pre)):
            if pre[i] != d[i]:
                pre = pre[:i]
                break
        for i in range(1, len(post)):
            if post[-i] != d[-i]:
                if i > 1:
                    post = post[-i+1:]
                else:
                    post = []
                break

    if len(pre) == len(data[0]):
        return

    if bitwise:
        if pre:
            format['pre_data_bits'] = len(pre)
            format['bits'] -= len(pre)
            pre = bits_to_bytes(pre, format.get('msb_first'))
        if post:
            format['post_data_bits'] = len(post)
            format['bits'] -= len(post)
            post = bits_to_bytes(post, format.get('msb_first'))

    if pre: format['pre_data'] = pre
    if post: format['post_data'] = post

def remove_pre_post(keys, formats):
    for name, data in keys.items():
        for part in data:
            f = part['format']
            format = formats[f]

            pre = format.get('pre_data', [])
            if pre:
                pre_bits = format.get('pre_data_bits', 0)
            else:
                pre_bits = 0

            post = format.get('post_data', [])
            if post:
                post_bits = format.get('post_data_bits', 0)
            else:
                post_bits = 0


            if not pre and not post:
                continue
            if pre_bits or post_bits: # bitwise?
                bits = bytes_to_bits(part['data'], format)
                bits = bits[pre_bits:]
                if post_bits:
                    bits = bits[:-post_bits]
                part['data'] = bits_to_bytes(bits, format.get('msb_first'))
            else: # bytewise
                data = part['data']
                data = data[len(pre):]
                if post:
                    data = data[:-len(post)]
                part['data'] = data

            if format.get('byte_by_byte_complement'):
                part['data'] = part['data'][::2]

def remove_complement(keys, formats):
    complement = [True] * len(formats)
    for name, data in keys.items():
        for part in data:
            f = part['format']
            if not complement[f]:
                continue

            format = formats[f]

            if format.get('bits', 0) % 8:
                complement[f] = False
                continue

            d = part['data']
            even = d[::2]
            odd = d[1::2]
            for e, o in zip(even, odd):
                if e ^ o != 0xff:
                    complement[f] = False
                    break

    for c, format in zip(complement, formats):
        if c:
            format['byte_by_byte_complement'] = True

    for name, data in keys.items():
        for part in data:
            f = part['format']
            if not complement[f]:
                continue
            part['data'] = part['data'][::2]

def prettify_keys(keys):
    result = {}
    for name, data in keys.items():
        parts = []
        for part in data:
            d = part['data']
            if isinstance(d, bytes):
                d = hexify(d)
            part['data'] = d
            if part['format'] == 0:
                part = part['data']
            parts.append(part)
        if len(parts) == 1:
            parts = parts[0]
        result[name] = parts
    return result

def prettify(raw_keys):
    formats = []
    timebases = []
    gaps = []
    keys = {}
    data_per_format = []
    for name, raw_data in raw_keys.items():
        data_list = []
        for d in raw_data:
            format = d.copy()
            data = format.pop('data')
            timebase = format.pop('timebase')
            gap = format.pop('gap')

            for k, v in list(format.items()):
                if not v:
                    del format[k]

            if format.get('bits', 1) % 8 == 0:
                del format['bits']

            for i, f in enumerate(formats):
                if f == format:
                    f_index = i
                    break
            else:
                formats.append(format)
                f_index = len(formats) - 1
                timebases.append([])
                gaps.append([])
                data_per_format.append([])

            timebases[f_index].append(timebase)
            if gap:
                gaps[f_index].append(gap)

            data_list.append(dict(format=f_index, data=data))

            data_per_format[f_index].append(data)
        keys[name] = data_list

    for i, format in enumerate(formats):
        find_pre_post(format, data_per_format[i])
    remove_pre_post(keys, formats)

    remove_complement(keys, formats)

    keys = prettify_keys(keys)

    for i, format in enumerate(formats):
        format['timebase'] = most_frequent(timebases[i])
        if gaps[i]:
            format['gap'] = most_frequent(gaps[i])

        pre = format.get('pre_data')
        if pre:
            format['pre_data'] = hexify(pre)

        post = format.get('post_data')
        if post:
            format['post_data'] = hexify(post)

    if len(formats) == 1:
        return dict(format=formats[0], keys=keys)
    else:
        return dict(formats=formats, keys=keys)
