import json
import logging
import traceback

import configargparse

from garagepi import GaragePiAssistant
from garagepi.common.configuration import validate_configuration
from garagepi.common.const import (
    CONF_API,
    CONF_NAME,
    API_MQTT,
    API_HASS
)
from garagepi.data.api.hass import HassApi
from garagepi.data.api.mqtt import MqttApi

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
        with open(args.config, 'r') as config_file:
            config = json.loads(config_file.read())

        config = validate_configuration(config)
        api = None
        if config[CONF_API][CONF_NAME] == API_HASS:
            api = HassApi(config[CONF_API])
        elif config[CONF_API][CONF_NAME] == API_MQTT:
            api = MqttApi(config[CONF_API])
        print(str(config))
        assistant = GaragePiAssistant(config, api, args.interactive)
        assistant.run()
    except Exception as e:
        _LOGGER.error(str(e))
        traceback.print_exc()
        # traceback.print_stack()


if __name__ == '__main__':
    main()
