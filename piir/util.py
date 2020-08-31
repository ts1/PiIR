def reverse_bits(byte):
    return int(f'{byte:08b}'[::-1], 2)

def bits_to_bytes(bits, msb_first):
    data = []
    b = 0
    byte = 0
    for bit in bits:
        if bit:
            byte |= 1 << b
        b += 1
        if b >= 8:
            data.append(byte)
            byte = 0
            b = 0
    if b:
        data.append(byte)
    if msb_first:
        data = [reverse_bits(byte) for byte in data]
    return bytes(data)

def bytes_to_bits(data, format, bits=None):
    bits = bits or format.get('bits') or (len(data) * 8)
    msb_first = format.get('msb_first')
    result = []
    for byte in data:
        if msb_first:
            byte = reverse_bits(byte)
        for bit in range(8):
            result.append(byte & 1)
            if len(result) >= bits:
                return result
            byte >>= 1
    return result

def hexify(data):
    return ' '.join(f'{byte:02X}' for byte in data)

