from garagepi.common.configuration import validate_configuration
from garagepi.common.const import *
from garagepi.data.rpi import gpio
from garagepi.domain import App
from garagepi.domain.usecase.api import BuildApiUseCase, NotifyStateUseCase
from garagepi.domain.usecase.commands import (
    CommandCloseUseCase,
    CommandOpenUseCase,
    CommandToggleUseCase
)
from garagepi.domain.usecase.models import (
    BuildGarageDoorModelUseCase,
    SetGarageDoorPositionUseCase
)
from garagepi.domain.usecase.retrieval.GetPositionUseCase import GetPositionUseCase
from garagepi.domain.usecase.retrieval.InputPinEventUseCase import \
    HandlePositionChangeUseCase
from garagepi.domain.usecase.rpi.SetupPinsUseCase import SetupPinsUseCase


def get_build_api_use_case(api_config):
    """Get use case to build API implementation."""
    return BuildApiUseCase(api_config)


def get_notify_state_use_case(api):
    """Get use case to notify api of state."""
    return NotifyStateUseCase(api)


def get_command_close_use_case(pin, invert):
    """Get use case for sending close command."""
    return CommandCloseUseCase(pin, invert=invert)


def get_command_open_use_case(pin, invert):
    """Get use case for sending open command."""
    return CommandOpenUseCase(pin, invert=invert)


def get_command_toggle_use_case(pin, invert):
    """Get use case for sending toggle command."""
    return CommandToggleUseCase(pin, invert=invert)


def get_build_garage_door_use_case(entity_id):
    """Get use case for building the garage door model."""
    return BuildGarageDoorModelUseCase(entity_id)


def get_set_garage_door_position_use_case(garage_door, notify_state):
    """Get use case for setting position of garage door."""
    return SetGarageDoorPositionUseCase(garage_door, notify_state)


def get_position_use_case(position_config):
    """Get use case for retrieving current position."""
    return GetPositionUseCase(
        {value: key for key, value in position_config.items()},
        gpio.HIGH
    )


def get_handle_position_change_use_case(position_config, set_position):
    """Get use case for handling position change events."""
    return HandlePositionChangeUseCase(
        {value: key for key, value in position_config.items()},
        set_position
    )


def get_setup_pins_use_case(in_pins):
    """Get use case for setting up gpio pins."""
    return SetupPinsUseCase(in_pins=in_pins)


def get_application(configuration):
    """Get the application for the given configuration."""
    config = validate_configuration(configuration)
    invert = config[CONF_INVERT_RELAY]

    get_setup_pins_use_case(
        [config.get(CONF_CLOSE_GARAGE_PIN),
         config.get(CONF_OPEN_GARAGE_PIN),
         config.get(CONF_TOGGLE_GARAGE_PIN)] + \
        config[CONF_POSITIONS].values()
    )()

    if CONF_TOGGLE_GARAGE_PIN in config:
        open_command = close_command = get_command_toggle_use_case(
            config[CONF_TOGGLE_GARAGE_PIN],
            invert)
    else:
        open_command = get_command_open_use_case(
            config[CONF_OPEN_GARAGE_PIN],
            invert
        )
        close_command = get_command_close_use_case(
            config[CONF_CLOSE_GARAGE_PIN],
            invert
        )
    api = get_build_api_use_case(config[CONF_API])()
    garage_door = get_build_garage_door_use_case(
        config[CONF_ENTITY_ID]
    )(get_position_use_case(config[CONF_POSITIONS]))

    return App(
        garage_door=get_build_garage_door_use_case(config[CONF_ENTITY_ID]),
        open_command=open_command,
        close_command=close_command,
        on_position_change=get_handle_position_change_use_case(
            config[CONF_POSITIONS],
            get_set_garage_door_position_use_case(
                garage_door,
                get_notify_state_use_case(api)
            )
        )(),
        api=api,
        interactive=config.get(CONF_INTERACTIVE, False)
    )
