import logging

initialized = False

try:
    import RPi.GPIO as gpio
    initialized = True
except (RuntimeError, ModuleNotFoundError):
    if not initialized:
        import fake_rpigpio.utils

        fake_rpigpio.utils.install()
        from fake_rpigpio.RPi import _FakeGPIO as fake_gpio

        _LOGGER = logging.getLogger(__name__)

    class MockPin:
        __slots__ = ['channel', 'mode', 'value', 'pud']

        def __init__(self, channel, mode, value=0, pud=fake_gpio.PUD_OFF):
            self.channel = channel
            self.mode = mode,
            self.value = value
            self.pud = pud

        def __str__(self):
            return "{} {} {}".format(self.channel, self.mode, self.value)

    class MockGPIO(fake_gpio):
        _out_pins = {}
        _in_pins = {}
        _event_callbacks = {}
        _events = {}

        def __init__(self):
            print('Initializing mock')

        def cleanup(self, channel=None):
            self._out_pins = {}
            self._in_pins = {}

        def setup(self, channel, direction, initial=0, pull_up_down=fake_gpio.PUD_DOWN):
            if direction == fake_gpio.OUT:
                self._out_pins[channel] = MockPin(channel, direction, initial)
            elif direction == fake_gpio.IN:
                self._in_pins[channel] = MockPin(channel, direction, initial, pull_up_down)

        def add_event_callback(self, gpio, callback):
            self._event_callbacks[gpio] = callback

        def add_event_detect(self, gpio, edge, callback=None, bouncetime=None):
            self._events[gpio] = {
                'edge': edge
            }

        def remove_event_detect(self, gpio):
            if gpio in self._events:
                del self._events[gpio]

        def output(self, channel, value):
            _LOGGER.warning('OUTPUT')
            pin = self._out_pins.get(channel, None)
            if pin is None:
                _LOGGER.warning('output- pin none')
                return
            if pin.value != value:
                pin.value = value
                _LOGGER.info('Notifying')
                self._out_pins[channel].value = value
                self.wait_for_edge(channel, value)
            else:
                _LOGGER.warning('No change in pin value')

        def input(self, channel):
            pin = self._in_pins.get(channel, None)
            return None if pin is None else pin.value

        def set_input(self, channel, value):
            pin = self._in_pins.get(channel, None)
            if pin is None:
                return
            if pin.value != value:
                pin.value = value
                print('Notifying')
                self._in_pins[channel].value = value
                self._notify(channel, value)

        def _notify(self, channel, value):
            callback = self._event_callbacks.get(channel, None)
            if callback is None:
                return
            callback(channel, value)

    gpio = MockGPIO()
