import piir

data = {
'1': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': (1, 1), 'one': (1, 3), 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x05\xfa', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
'2': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': (1, 1), 'one': (1, 3), 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x07\xf8', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
'3': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': (1, 1), 'one': (1, 3), 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\t\xf6', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
'4': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': (1, 1), 'one': (1, 3), 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x1b\xe4', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
}

expected = {
    'format': {
        'byte_by_byte_complement': True,
        'coding': 'ppm',
        'gap': 96000,
        'one': (1, 3),
        'postamble': [1],
        'pre_data': '80 7F',
        'preamble': [16, 8],
        'timebase': 570,
        'zero': (1, 1)
    },
    'keys': {'1': '05', '2': '07', '3': '09', '4': '1B'}
}

def test_prettify():
    assert piir.prettify(data) == expected
