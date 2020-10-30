from time import sleep, time
import pigpio
from .util import synchronized

def receive(gpio, glitch=100, timeout=200):
    last_tick = 0
    in_code = False
    recording = False
    pulses = []

    def callback(gpio, level, tick):
        nonlocal last_tick, in_code, recording
        usec = pigpio.tickDiff(last_tick, tick)
        last_tick = tick
        if level == pigpio.TIMEOUT:
            if in_code:
                in_code = False
                recording = False
        else:
            if in_code:
                pulses.append(usec)
            else:
                # Ignore the first one (time since last timeout).
                in_code = True

    pi = pigpio.pi() # Connect to Pi.

    if not pi.connected:
       raise IOError

    pi.set_mode(gpio, pigpio.INPUT) # IR RX connected to this GPIO.
    pi.set_glitch_filter(gpio, glitch) # Ignore glitches.
    pi.set_watchdog(gpio, timeout)
    pi.callback(gpio, pigpio.EITHER_EDGE, callback)

    while True:
        recording = True
        while recording:
            sleep(0.01)
        if pulses:
            break

    pi.stop()

    return pulses

@synchronized
def send(
    gpio,
    pulses,
    active_low = False,
    carrier = None,
    duty_cycle = None,
    repeat = None,
    gap = None,
):
    carrier = carrier or 38_000
    duty_cycle = duty_cycle or 1/2
    repeat = repeat or 1
    gap = gap or 50_000

    def generate_carrier(length):
        wf = []
        cycle = 1_000_000 / carrier
        cycles = int(round(length / cycle))
        on = int(round(cycle * duty_cycle))
        sofar = 0
        for c in range(cycles):
            target = int(round((c+1)*cycle))
            sofar += on
            off = target - sofar
            sofar += off
            if active_low:
                wf.append(pigpio.pulse(0, 1<<gpio, on))
                wf.append(pigpio.pulse(1<<gpio, 0, off))
            else:
                wf.append(pigpio.pulse(1<<gpio, 0, on))
                wf.append(pigpio.pulse(0, 1<<gpio, off))
        return wf

    pi = pigpio.pi() # Connect to Pi.
    if not pi.connected:
        raise IOError
    pi.set_mode(gpio, pigpio.OUTPUT)

    pi.wave_clear()
    wave_ids = {}
    chain = []

    if len(pulses) & 1:
        pulses = pulses + [0]

    if repeat > 1:
        pulses[-1] += gap

    for i in range(0, len(pulses), 2):
        mark = pulses[i]
        space = pulses[i + 1]
        wave_id = wave_ids.get((mark, space))
        if not wave_id:
            wf = generate_carrier(mark)
            if space:
                wf.append(pigpio.pulse(0, 0, space))
            pi.wave_add_generic(wf)
            wave_id = pi.wave_create()
            wave_ids[(mark, space)] = wave_id
        chain.append(wave_id)

    for i in range(repeat):
        pi.wave_chain(chain)
        while pi.wave_tx_busy():
            sleep(0.001)

    pi.wave_clear()
    pi.stop()
