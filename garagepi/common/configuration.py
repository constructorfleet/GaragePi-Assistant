import voluptuous as vol

from garagepi.common.const import (
    CONF_DATA_INTERFACE,
    CONF_POSITIONS,
    CONF_CLOSE_GARAGE_PIN,
    CONF_OPEN_GARAGE_PIN,
    CONF_IS_OPEN_PIN,
    CONF_IS_CLOSED_PIN
)
from garagepi.common.validation import (
    ValidateGPIOPin,
    ValidateNumericPosition,
    VALID_GPIO_PINS, keys_with_schema)
from garagepi.data.hass import HASS_CONFIGURATION_SCHEMA
from garagepi.data.mqtt import MQTT_CONFIGURATION_SCHEMA


def get_configuration_schema():
    """Get the schema for validating the configuration."""
    valid_gpio_pin = ValidateGPIOPin()
    valid_numeric_position = ValidateNumericPosition()

    return vol.Schema({
        vol.Required(CONF_DATA_INTERFACE): vol.Or(
            MQTT_CONFIGURATION_SCHEMA,
            HASS_CONFIGURATION_SCHEMA
        ),
        vol.Required(CONF_OPEN_GARAGE_PIN): valid_gpio_pin,
        vol.Required(CONF_CLOSE_GARAGE_PIN): valid_gpio_pin,
        vol.Required(CONF_IS_OPEN_PIN): valid_gpio_pin,
        vol.Required(CONF_IS_CLOSED_PIN): valid_gpio_pin,
        vol.Optional(CONF_POSITIONS): keys_with_schema(valid_numeric_position, VALID_GPIO_PINS)
    }, extra=vol.ALLOW_EXTRA)
