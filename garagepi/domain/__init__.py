"""Module for domain logic."""


class App:
    """Application container"""

    def __init__(self,
                 garage_door,
                 open_command,
                 close_command,
                 on_position_change,
                 interactive=False):
        """Create application class."""
        self.garage_door = garage_door
        self.open_command = open_command
        self.close_command = close_command
        self.on_position_change = on_position_change
        self.interactive = interactive

    def run(self):
        """Run the application"""
