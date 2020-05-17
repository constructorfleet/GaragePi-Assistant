import asyncio

try:
    import RPi.GPIO as gpio
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils

    fake_rpigpio.utils.install()
    import RPi.GPIO as gpio

    def _write_output(pin, value):
        pass
    setattr(gpio, 'write_output', _write_output)

from garagepi.common.const import *

CONFIG_PIN_MODES = {
    CONF_CLOSE_GARAGE_PIN: gpio.OUT,
    CONF_OPEN_GARAGE_PIN: gpio.OUT,
    CONF_POSITIONS: gpio.IN
}


class Interactive:
    should_quit = False

    def run(self):
        while not self.should_quit:
            print('Enter pin: ')
            pin = int(input())
            print('1 or 0? ')
            value = int(input())
            gpio.write_output(pin, value)


class GaragePiAssistant:
    """Main class for interacting with the garage door and data layer."""

    __slots__ = ['config', 'api', 'interactive']

    def __init__(self, config, api, interactive=None):
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

            config_value = config_value if isinstance(config_value, list) else [config_value]
            for position_pin in config_value:
                if pin_mode == gpio.IN:
                    gpio.setup(
                        position_pin,
                        pin_mode,
                        pull_up_down=gpio.PUD_DOWN)
                else:
                    gpio.setup(
                        position_pin,
                        pin_mode)
