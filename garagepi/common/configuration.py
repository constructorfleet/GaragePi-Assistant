import voluptuous as vol

from garagepi.common.const import (
    CONF_DATA_INTERFACE,
    CONF_POSITIONS,
    CONF_CLOSE_GARAGE_PIN,
    CONF_OPEN_GARAGE_PIN,
    CONF_POSITION_OPEN_PIN,
    CONF_POSITION_CLOSE_PIN
)
from garagepi.common.validation import (
    DATA_INTERFACE_HASS,
    DATA_INTERFACE_MQTT,
    ValidateGPIOPin,
    ValidateNumericPosition
)
from garagepi.data.hass import HASS_CONFIGURATION_SCHEMA
from garagepi.data.mqtt import MQTT_CONFIGURATION_SCHEMA


def get_configuration_schema():
    """Get the schema for validating the configuration."""
    valid_gpio_pin = ValidateGPIOPin()
    valid_numeric_position = ValidateNumericPosition()

    return vol.Schema({
        vol.Required(CONF_DATA_INTERFACE): vol.Schema({
            vol.Exclusive(DATA_INTERFACE_MQTT, 'data_interface'): MQTT_CONFIGURATION_SCHEMA,
            vol.Exclusive(DATA_INTERFACE_HASS, 'data_interface'): HASS_CONFIGURATION_SCHEMA
        }),
        vol.Required(CONF_OPEN_GARAGE_PIN): valid_gpio_pin,
        vol.Required(CONF_CLOSE_GARAGE_PIN): valid_gpio_pin,
        vol.Required(CONF_POSITIONS): vol.All(
            vol.Exclusive(vol.Schema({
                vol.Required(CONF_POSITION_OPEN_PIN): valid_gpio_pin,
                vol.Required(CONF_POSITION_CLOSE_PIN): valid_gpio_pin
            }), 'positions'),
            vol.Exclusive(vol.Schema({
                valid_numeric_position: valid_gpio_pin
            }), 'positions'))
    }, extra=vol.ALLOW_EXTRA)
