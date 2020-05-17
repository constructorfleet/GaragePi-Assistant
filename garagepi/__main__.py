import json
import logging
import traceback

import configargparse

from garagepi.common.configuration import get_configuration_schema
from garagepi.common.const import (
    CONF_DATA_INTERFACE,
    CONF_NAME,
    DATA_INTERFACE_MQTT,
    DATA_INTERFACE_HASS
)
from garagepi.data.hass import HassApi
from garagepi.data.mqtt import MqttApi
from garagepi import GaragePiAssistant

_LOGGER = logging.getLogger(__name__)


def main():
    parser = configargparse.ArgParser(
        description='Google EdgeTPU video stream detection'
    )
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='Path to configuration file')
    parser.add_argument('-i', '--interactive', type=bool, required=False, default=False,
                        help='Run interactive console')
    args = parser.parse_args()

    try:
        config = None
        with open(args.config, 'r') as config_file:
            config = json.loads(config_file.read())

        config = get_configuration_schema()(config)
        api = None
        if config[CONF_DATA_INTERFACE][CONF_NAME] == DATA_INTERFACE_HASS:
            api = HassApi(config[CONF_DATA_INTERFACE], None)
        elif config[CONF_DATA_INTERFACE][CONF_NAME] == DATA_INTERFACE_MQTT:
            api = MqttApi(config[CONF_DATA_INTERFACE], None)
        print(str(config))
        assistant = GaragePiAssistant(config, api, args.interactive)
        assistant.run()
    except Exception as e:
        _LOGGER.error(str(e))
        traceback.print_exc()
        # traceback.print_stack()


if __name__ == '__main__':
    main()
