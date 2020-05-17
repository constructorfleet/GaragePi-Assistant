import asyncio
from time import sleep

from garagepi.common.const import *
from garagepi.data.rpi import gpio

CONFIG_PIN_MODES = {
    CONF_CLOSE_GARAGE_PIN: gpio.IN,
    CONF_OPEN_GARAGE_PIN: gpio.IN,
    CONF_POSITIONS: gpio.OUT
}


class Interactive:
    should_quit = False

    def run(self):
        while not self.should_quit:
            print('Enter pin: ')
            pin = int(input())
            print('1 or 0? ')
            value = int(input())
            gpio.output(pin, value)


class GaragePiAssistant:
    """Main class for interacting with the garage door and data layer."""

    __slots__ = ['config', 'api', 'interactive', '_open_garage_pin', '_close_garage_pin',
                 '_position_pins', '_pin_positions']

    def __init__(self, config, api, interactive=None):
        self._open_garage_pin = None
        self._close_garage_pin = None
        self._position_pins = {}
        self._pin_positions = {}
        self.config = config
        self.api = api
        self.interactive = None if interactive is None else Interactive()
        self._setup_gpio_pins()

    def run(self):
        asyncio.get_event_loop().create_task(self.api.get_updates())
        if self.interactive is not None:
            self.interactive.run()

    def _setup_gpio_pins(self):
        for config, pin_mode in CONFIG_PIN_MODES.items():
            print('Config key {}, mode {}'.format(config, pin_mode))
            config_value = self.config.get(config, None)
            if config_value is None:
                continue
            print('Config value {} {}'.format(config, config_value))
            if not isinstance(config_value, dict) and not isinstance(config_value, list):
                self._setup_pin(config, config_value)
            elif isinstance(config_value, dict):
                for key, value in config_value.items():
                    self._setup_pin(key, value)

    def _setup_pin(self, config_key, position_pin):
        if CONFIG_PIN_MODES.get(config_key, gpio.OUT) == gpio.IN:
            gpio.setup(
                position_pin,
                gpio.IN,
                pull_up_down=gpio.PUD_DOWN)
            if config_key == CONF_OPEN_GARAGE_PIN:
                self._open_garage_pin = position_pin
                gpio.add_event_callback(gpio, self._handle_open_command)
            elif config_key == CONF_CLOSE_GARAGE_PIN:
                self._close_garage_pin = position_pin
                gpio.add_event_callback(gpio, self._handle_close_command)
        else:
            gpio.setup(
                position_pin,
                gpio.OUT)
            self._position_pins[config_key] = position_pin
            # gpio.add_event_callback(gpio, self._handle_output_change)

    def _handle_open_command(self, channel, value):
        print('Open handler {} {}'.format(channel, value))
        if channel != self._open_garage_pin and value != 1:
            return
        print('Opening')
        self._open()

    def _open(self):
        for position in ['75', '50', '25']:
            if position not in self._position_pins:
                print('{} not in {}'.format(position, self._position_pins))
                continue
            print(position.replace('_pin', ''))
            sleep(3)

    def _handle_close_command(self, channel, value):
        print('Close handler {} {}'.format(channel, value))
        if channel != self._close_garage_pin and value != 1:
            return
        print('Closing')
        self._close()

    def _close(self):
        for position in ['25', '50', '75']:
            if position not in self._position_pins:
                continue
            print(position.replace('_pin', ''))
            sleep(3)
