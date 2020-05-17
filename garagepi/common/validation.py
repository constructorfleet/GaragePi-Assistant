import re

import voluptuous as vol

from garagepi.common.const import DATA_INTERFACE_HASS, DATA_INTERFACE_MQTT, COMMAND_OPEN, \
    COMMAND_CLOSE, TEMPLATE_STATE

FLOAT_PATTERN = re.compile(r'[+-]?([0-9]*[.])?[0-9]+')

VALID_INTERFACES = vol.Any(
    DATA_INTERFACE_HASS,
    DATA_INTERFACE_MQTT
)

VALID_COMMANDS = vol.Any(
    COMMAND_OPEN,
    COMMAND_CLOSE
)

VALID_GPIO_PINS = vol.In([
        2,
        3,
        4,
        17,
        27,
        22,
        10,
        11,
        5,
        6,
        13,
        19,
        26,
        18,
        23,
        24,
        25,
        8,
        7,
        12,
        16,
        20,
        21
    ])


def keys_with_schema(
    key_schema,
    value_schema
):
    """Ensure all keys follow schema."""

    schema = vol.Schema({int: value_schema})

    def verify(value):
        """Validate all keys pass value_schema."""
        if not isinstance(value, dict):
            raise vol.Invalid("expected dictionary")

        result = {}
        for key, value in value.items():
            valid_key = key_schema(value)
            result[valid_key] = value

        return schema(result)

    return verify


def is_valid_entity_id(value):
    """Test if an entity ID is a valid format.
    Format: <domain>.<entity> where both are slugs.
    """
    if not isinstance(value, str):
        return False
    if FLOAT_PATTERN.match(value):
        return False

    return (isinstance(value, str) and
            '.' in entity_id and
            value == value.replace(' ', '_'))


def entity_id(value):
    """Validate Entity ID."""
    value = str(value).lower()
    if is_valid_entity_id(value):
        return value

    raise vol.Invalid('Entity ID {} is an invalid entity id'.format(value))


def ensure_list(value):
    """Wrap value in list if it is not one."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def valid_topic(value):
    """Validate that this is a valid topic name/filter."""
    value = vol.Coerce(str)(value)
    try:
        raw_value = value.encode("utf-8")
    except UnicodeError:
        raise vol.Invalid("MQTT topic name/filter must be valid UTF-8 string.")
    if not raw_value:
        raise vol.Invalid("MQTT topic name/filter must not be empty.")
    if len(raw_value) > 65535:
        raise vol.Invalid(
            "MQTT topic name/filter must not be longer than 65535 encoded bytes."
        )
    if "\0" in value:
        raise vol.Invalid("MQTT topic name/filter must not contain null character.")
    return value


def valid_subscribe_topic(value):
    """Validate that we can subscribe using this MQTT topic."""
    value = valid_topic(value)
    for i in (i for i, c in enumerate(value) if c == "+"):
        if (i > 0 and value[i - 1] != "/") or (
                i < len(value) - 1 and value[i + 1] != "/"
        ):
            raise vol.Invalid(
                "Single-level wildcard must occupy an entire level of the filter"
            )

    index = value.find("#")
    if index != -1:
        if index != len(value) - 1:
            # If there are multiple wildcards, this will also trigger
            raise vol.Invalid(
                "Multi-level wildcard must be the last "
                "character in the topic filter."
            )
        if len(value) > 1 and value[index - 1] != "/":
            raise vol.Invalid(
                "Multi-level wildcard must be after a topic level separator."
            )

    return value


def valid_publish_topic(value):
    """Validate that we can publish using this MQTT topic."""
    value = valid_topic(value)
    if "+" in value or "#" in value:
        raise vol.Invalid("Wildcards can not be used in topic names")
    return value


def valid_state_template(value):
    """Validate the MQTT state payload template."""
    return TEMPLATE_STATE in value


def constant_value(value):
    """No matter the input, return the value."""
    def constant(input_value):
        return value

    return constant


class ValidateGPIOPin:
    """Validates a GPIO pin in the configuration."""
    _used_pins = set()

    def __call__(self, value):
        int_value = vol.Coerce(int)(value)
        VALID_GPIO_PINS(int_value)
        if int_value in self._used_pins:
            raise vol.Invalid("GPIO pin {} is already used elsewhere.".format(str(int_value)))

        self._used_pins.add(int_value)
        return int_value


class ValidateNumericPosition:
    """Validates a numeric position key."""
    _used_positions = set()

    def __call__(self, value):
        float_value = vol.Coerce(float)(
            float(str(value)[-1]) if isinstance(value, str) else value)
        int_value = vol.Coerce(int)(float_value * 10 if float_value < 1.0 else float_value)
        if int_value in self._used_positions:
            raise vol.Invalid("Position {} is already used elsewhere".format(str(value)))
        return int_value
