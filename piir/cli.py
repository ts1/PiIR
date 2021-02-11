import json, os, sys
from argparse import ArgumentParser
from .io import receive
from .decode import decode
from .util import hexify
from .prettify import prettify
from .remote import Remote
from . import __version__

def bytes_to_hex(x):
    if isinstance(x, bytes):
        return hexify(x)
    raise TypeError

def do_receive(args):
    return receive(args.gpio, glitch=args.glitch, timeout=args.timeout)

def receive_and_decode(args):
    while True:
        data = decode(
            do_receive(args),
            tolerance = args.tolerance,
            min_gap = args.gap * 1000,
            min_pulses = args.pulses,
        )
        if data:
            return data

def record_key(args, name):
    print(f'Press the key named "{name}".')
    data1 = receive_and_decode(args)
    print('Press the same key again to verify.')
    data2 = receive_and_decode(args)
    if data2 == data1:
        return data2
    while True:
        print('Press the same key again to verify.')
        data3 = receive_and_decode(args)
        if data3 == data1 or data3 == data2:
            return data3
        data1 = data2
        data2 = data3

def record(args):
    keys = {}
    if os.path.exists(args.file):
        print(f'Loading "{args.file}"...')
        remote = Remote(args.file, None)
        keys = remote.unprettify()
    if args.keys:
        for name in args.keys:
            keys[name] = record_key(args, name)
    else:
        while True:
            name = input('Name of the key (blank to finish): ')
            if not name:
                break
            keys[name] = record_key(args, name)
    data = prettify(keys, carrier=int(round(args.carrier * 1000)))
    json.dump(data, open(args.file, 'w', encoding='utf8'), indent=2)
    print(f'Saved to "{args.file}".')

def play(args):
    remote = Remote(
        args.file,
        args.gpio,
        active_low = args.active_low,
        duty_cycle = args.duty_cycle,
    )
    for key in args.keys:
        remote.send(key, repeat=args.repeat)

def dump(args):
    keys = {}

    while True:
        if args.raw:
            pulses = do_receive(args)
            print(' '.join(str(x) for x in pulses))
        elif args.intermediate:
            data = receive_and_decode(args)
            print(json.dumps(data, default=bytes_to_hex))
        else:
            data = receive_and_decode(args)
            key = len(keys)
            keys[key] = data
            remote = Remote(prettify(keys), None)
            restored = remote.restore_data(remote.keys[key], False)
            if len(restored) == 1:
                restored = restored[0]
            print(json.dumps(restored, indent=2, default=bytes_to_hex))

def main():
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument(
        '-g',
        '--gpio',
        help = 'GPIO to use',
        type = int,
        required = True,
    )

    decode_parser = ArgumentParser(add_help=False)
    decode_parser.add_argument(
        '-G',
        '--glitch',
        help = 'Ignore glitch shorter than GLITCH microseconds (default 100)',
        type = int,
        default = 100,
    )
    decode_parser.add_argument(
        '-t',
        '--timeout',
        help = 'Finish receiving after TIMEOUT milliseconds of silence (default 100)',
        type = int,
        default = 100,
    )
    decode_parser.add_argument(
        '-T',
        '--tolerance',
        help = 'Timing tolerance for decoding (default 0.2)',
        type = float,
        default = .2,
    )
    decode_parser.add_argument(
        '--gap',
        help = 'Minimum gap between data in milliseconds (default 15)',
        type = int,
        default = 15,
    )
    decode_parser.add_argument(
        '-p',
        '--pulses',
        help = 'Ignore signal with less than PULSES pulses (>=3, default 10)',
        type = int,
        default = 10,
    )

    file_parser = ArgumentParser(add_help=False)
    file_parser.add_argument(
        '-f',
        '--file',
        required = True,
        help = 'Filename to record/play',
    )

    root_parser = ArgumentParser(
        description = 'IR remote control for Raspberry Pi'
    )
    root_parser.set_defaults(func=None)
    subparsers = root_parser.add_subparsers(title='Sub commands')
    root_parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )


    record_parser = subparsers.add_parser(
        'record',
        help = 'Record IR to file',
        parents = [common_parser, file_parser, decode_parser],
    )
    record_parser.set_defaults(func=record)
    record_parser.add_argument(
        'keys',
        nargs = '*',
        metavar = 'KEY',
        help = 'Name of keys',
    )
    record_parser.add_argument(
        '-c',
        '--carrier',
        type = float,
        default = 38,
        help = 'Frequency of carrier wave in KHz (default 38). '
            'NOTE: This option does not affect receiving/decoding, '
            'but is recorded in the file.',
    )

    play_parser = subparsers.add_parser(
        'play',
        help = 'Play IR from file',
        parents = [common_parser, file_parser],
    )
    play_parser.set_defaults(func=play)
    play_parser.add_argument(
        'keys',
        nargs = '+',
        metavar = 'KEY',
        help = 'Name of keys',
    )
    play_parser.add_argument(
        '-r',
        '--repeat',
        metavar = 'N',
        type = int,
        help = 'Repeat sending each key N times (default 1)',
    )
    play_parser.add_argument(
        '-l',
        '--active-low',
        action = 'store_true',
        help = 'Drive LED as active low',
    )
    play_parser.add_argument(
        '-d',
        '--duty-cycle',
        type = float,
        default = 1/2,
        help = 'Duty cycle of carrier wave (default 0.5)',
    )

    dump_parser = subparsers.add_parser(
        'dump',
        help = 'Receive IR and dump',
        parents = [common_parser, decode_parser],
    )
    dump_parser.set_defaults(func=dump)
    dump_mode = dump_parser.add_mutually_exclusive_group()
    dump_mode.add_argument(
        '-r',
        '--raw',
        action = 'store_true',
        help = 'Print raw pulses',
    )
    dump_mode.add_argument(
        '-i',
        '--intermediate',
        action = 'store_true',
        help = 'Print intermediate data',
    )

    args = root_parser.parse_args()

    if args.func is None:
        root_parser.print_help()
        exit(1)

    if getattr(args, 'pulses', 10) < 3:
        print(f'PULSES must be >= 3', file=sys.stderr)
        exit(1)

    args.func(args)

if __name__ == '__main__':
    main()
