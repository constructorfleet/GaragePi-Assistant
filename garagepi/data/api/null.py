import voluptuous as vol

from garagepi import CONF_NAME, API_NULL
from garagepi.common.validation import constant_value
from garagepi.framework.data.Api import Api

NULL_CONFIGURATION_SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME, default=API_NULL): constant_value(API_NULL)
})


class NullApi(Api):
    """Null API adapter."""

    def _initialize(self):
        self.logger.warning('Initializing API')

    async def get_updates(self):
        self.logger.warning('Getting updates')

    def _validate_configuration(self, configuration):
        self.logger.warning('Validating')
        return configuration

    async def report_state(self, garage_door):
        self.logger.warning("Reporting %s", str(garage_door))
