import pytest
import piir

intermediate1 = {
    '1': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': [1, 1], 'one': [1, 3], 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x05\xfa', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
    '2': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': [1, 1], 'one': [1, 3], 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x07\xf8', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
    '3': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': [1, 1], 'one': [1, 3], 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\t\xf6', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
    '4': [{'preamble': [16, 8], 'coding': 'ppm', 'zero': [1, 1], 'one': [1, 3], 'byte_separator': None, 'msb_first': False, 'bits': 32, 'data': b'\x80\x7f\x1b\xe4', 'postamble': [1], 'timebase': 570, 'gap': 96000}],
}

prettified1 = {
    'format': {
        'byte_by_byte_complement': True,
        'coding': 'ppm',
        'gap': 96000,
        'one': [1, 3],
        'postamble': [1],
        'pre_data': '80 7F',
        'preamble': [16, 8],
        'timebase': 570,
        'zero': [1, 1],
        'carrier': 38000
    },
    'keys': {'1': '05', '2': '07', '3': '09', '4': '1B'}
}

set1 = [intermediate1, prettified1]

intermediate2 = {
    '1': [{"preamble": [6, 2, 1, 1], "coding": "manchester", "zero": [0, 1], "one": [1, 0], "long_bit": 3, "msb_first": True, "bits": 20, "data": b"\x10\x42\x90", "timebase": 430, "gap": 88000}],
    '2': [{"preamble": [6, 2, 1, 1], "coding": "manchester", "zero": [0, 1], "one": [1, 0], "long_bit": 3, "msb_first": True, "bits": 20, "data": b"\x10\x42\xC0", "timebase": 430, "gap": 88000}],
    '3': [{"preamble": [6, 2, 1, 1], "coding": "manchester", "zero": [0, 1], "one": [1, 0], "long_bit": 3, "msb_first": True, "bits": 20, "data": b"\x10\x42\x80", "timebase": 430, "gap": 88000}],
    '4': [{"preamble": [6, 2, 1, 1], "coding": "manchester", "zero": [0, 1], "one": [1, 0], "long_bit": 3, "msb_first": True, "bits": 20, "data": b"\x10\x43\x10", "timebase": 430, "gap": 89000}],
}

prettified2 = {
  "format": {
    "preamble": [
      6,
      2,
      1,
      1
    ],
    "coding": "manchester",
    "zero": [
      0,
      1
    ],
    "one": [
      1,
      0
    ],
    "long_bit": 3,
    "msb_first": True,
    "bits": 5,
    "pre_data_bits": 15,
    "pre_data": "10 42",
    "timebase": 430,
    "gap": 88000,
    'carrier': 38000
  },
  "keys": {
    "1": "48",
    "2": "60",
    "3": "40",
    "4": "88"
  }
}

set2 = [intermediate2, prettified2]

intermediate3 = {
    '1': [{"coding": "raw", "data": [4, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1], "timebase": 600, "gap": 26000}],
    '2': [{"coding": "raw", "data": [4, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1], "timebase": 590, "gap": 26000}],
    '3': [{"coding": "raw", "data": [4, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1], "timebase": 600, "gap": 26000}],
    '4': [{"coding": "raw", "data": [4, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1], "timebase": 600, "gap": 26000}],
}

prettified3 = {
 'format': {'coding': 'raw',
            'gap': 26000,
            'post_data': [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1],
            'pre_data': [4, 1, 2, 1],
            'timebase': 600,
            'carrier': 38000
            },
 'keys': {'1': [[1, 1, 2, 1, 1, 1, 2, 1, 1]],
          '2': [[2, 1, 2, 1, 1, 1, 2, 1, 1]],
          '3': [[1, 1, 2, 1, 1, 1, 1, 1, 2]],
          '4': [[2, 1, 1, 1, 2, 1, 1, 1, 1]]}
}

set3 = [intermediate3, prettified3]

sets = [
    [intermediate1, prettified1],
    [intermediate2, prettified2],
    [intermediate3, prettified3],
]

@pytest.mark.parametrize("intermediate, prettified", sets)
def test_prettify(intermediate, prettified):
    assert piir.prettify(intermediate) == prettified

@pytest.mark.parametrize("_, prettified", sets)
def test_unprettify(_, prettified):
    u = piir.Remote(prettified, None).unprettify()
    assert piir.prettify(u) == prettified
