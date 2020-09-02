import piir

data = {
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

def test_unprettify():
    remote = piir.Remote(data, None)
    u = remote.unprettify()
    assert piir.prettify(u) == data
