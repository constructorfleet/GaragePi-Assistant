import voluptuous as vol

from garagepi.common.const import (
    CONF_API,
    CONF_POSITIONS,
    CONF_CLOSE_GARAGE_PIN,
    CONF_OPEN_GARAGE_PIN,
    CONF_ENTITY_ID,
    CONF_TOGGLE_GARAGE_PIN, CONF_INVERT_RELAY)
from garagepi.common.validation import (
    ValidateGPIOPin,
    ValidateNumericPosition,
    VALID_GPIO_PINS,
    keys_with_schema,
    entity_id
)
from garagepi.data.api.hass import HASS_CONFIGURATION_SCHEMA
from garagepi.data.api.mqtt import MQTT_CONFIGURATION_SCHEMA


def validate_configuration(configuration):
    """Get the schema for validating the configuration."""
    valid_gpio_pin = ValidateGPIOPin()
    valid_numeric_position = ValidateNumericPosition()

    config = vol.Schema({
        vol.Required(CONF_API): vol.Or(
            MQTT_CONFIGURATION_SCHEMA,
            HASS_CONFIGURATION_SCHEMA
        ),
        vol.Inclusive(CONF_OPEN_GARAGE_PIN, 'control'): valid_gpio_pin,
        vol.Inclusive(CONF_CLOSE_GARAGE_PIN, 'control'): valid_gpio_pin,
        vol.Optional(CONF_TOGGLE_GARAGE_PIN): valid_gpio_pin,
        vol.Optional(CONF_INVERT_RELAY, default=False): vol.Coerce(bool),
        vol.Required(CONF_POSITIONS): keys_with_schema(valid_numeric_position, VALID_GPIO_PINS),
        vol.Required(CONF_ENTITY_ID): entity_id
    }, extra=vol.ALLOW_EXTRA)(configuration)

    if not config.get(CONF_OPEN_GARAGE_PIN) and not config.get(CONF_TOGGLE_GARAGE_PIN):
        raise vol.MultipleInvalid(
            '({} and {}) or {}'.format(
                CONF_OPEN_GARAGE_PIN,
                CONF_CLOSE_GARAGE_PIN,
                CONF_TOGGLE_GARAGE_PIN))

    return config
