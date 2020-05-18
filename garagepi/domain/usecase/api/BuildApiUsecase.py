from garagepi import CONF_NAME, API_HASS, API_MQTT
from garagepi.data.api.hass import HassApi
from garagepi.data.api.mqtt import MqttApi
from garagepi.framework.usecase import UseCase


class BuildApiUseCase(UseCase):
    """Create the API class."""

    def __init__(self, api_config):
        self.config = api_config

    def __call__(self, *args, **kwargs):
        if self.config[CONF_NAME] == API_HASS:
            return HassApi(self.config)
        elif self.config[CONF_NAME] == API_MQTT:
            return MqttApi(self.config)