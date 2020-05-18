"""Module for domain logic."""
import asyncio
from concurrent.futures import ThreadPoolExecutor

from garagepi.data.rpi import gpio


class Interactive:
    executor = ThreadPoolExecutor()

    def __init__(self, garage_door, open_cmd, close_cmd):
        self.garage_door = garage_door
        self.open_cmd = open_cmd
        self.close_cmd = close_cmd

    def prompt(self):
        print('Command:')
        cmd = str(input())
        if cmd.lower() == 'open':
            self.open_cmd(self)
        elif cmd.lower() == 'close':
            self.close_cmd(self.garage_door)
        # print('Enter pin: ')
        # pin = int(input())
        # print('1 or 0? ')
        # value = int(input())
        # gpio.set_input(pin, value)

    async def run(self):
        while True:
            await asyncio.get_event_loop().run_in_executor(self.executor, self.prompt)
            await asyncio.sleep(1)


class App:
    """Application container"""

    background_thread = None

    def __init__(self,
                 garage_door,
                 open_command,
                 close_command,
                 on_position_change,
                 api,
                 interactive=False):
        """Create application class."""
        self.garage_door = garage_door
        self.open_command = open_command
        self.close_command = close_command
        self.on_position_change = on_position_change
        self.api = api
        self.interactive = Interactive(garage_door, open_command, close_command) if interactive else None

    def run(self):
        """Run the application"""
        asyncio.get_event_loop().create_task(self.api.get_updates())
        if self.interactive is not None:
            asyncio.get_event_loop().create_task(self.interactive.run())
        asyncio.get_event_loop().run_forever()
