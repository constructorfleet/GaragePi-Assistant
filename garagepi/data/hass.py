"""Data interface with Home-Assistant instance."""
import asyncio
import json
import ssl
import traceback

import voluptuous as vol
import websocket

from garagepi.common.async_utils import run_in_executor, create_task
from garagepi.common.validation import entity_id
from garagepi.data import DataInterface

CONF_CERT_VERIFY = 'cert_verify'
CONF_ENTITY_ID = 'entity_id'
CONF_FRIENDLY_NAME = 'friendly_name'
CONF_TOKEN = 'token'
CONF_URL = 'url'

HASS_CONFIGURATION_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): vol.Url,
    vol.Required(CONF_ENTITY_ID): entity_id,
    vol.Optional(CONF_TOKEN, default=None): str,
    vol.Optional(CONF_FRIENDLY_NAME): str,
    vol.Optional(CONF_CERT_VERIFY, default=True): vol.Coerce(bool)
})


class HassDataInterface(DataInterface):
    """Interface with Home-Assistant instance."""
    _ws_client = None
    _id = 0
    _reading_messages = False
    _hass_booting = False

    def __init__(self, configuration, command_listener):
        super().__init__(configuration, command_listener)

    def _validate_configuration(self, configuration):
        return HASS_CONFIGURATION_SCHEMA(configuration)

    def _initialize(self):
        create_task(self.get_updates())

    def report_state(self):
        pass

    async def _connect(self):
        # Open websocket connection to Home-Assistant instance
        url = self.config[CONF_URL]
        if url.startswith('https://'):
            url = url.replace('https', 'wss', 1)
        elif url.startswith('http://'):
            url = url.replace('http', 'ws', 1)

        ssl_options = {}
        if self.config.get(CONF_CERT_VERIFY, True) is False:
            ssl_options = {'cert_reqs': ssl.CERT_NONE}

        self._ws_client = websocket.create_connection(
            "{}/api/websocket".format(url), sslopt=ssl_options
        )
        res = await run_in_executor(self, self.ws.recv)
        return json.loads(res)

    async def _authenticate(self):
        if self.token is not None:
            auth = json.dumps({
                "type": "auth",
                "access_token": self.token
            })
        else:
            raise ValueError(
                "HASS requires authentication and none provided in plugin config")

        await run_in_executor(self, self.ws.send, auth)
        result = json.loads(self.ws.recv())
        if result["type"] != "auth_ok":
            self.logger.warning("Error in authentication")
            raise ValueError("Error in authentication")

    async def _subscribe_to_service_calls(self):
        sub = json.dumps({
            "id": self._id,
            "type": "subscribe_events",
            "event_type": "call_service"
        })
        await run_in_executor(self, self.ws.send, sub)
        result = json.loads(self.ws.recv())
        if not (result["id"] == self._id and
                result["type"] == "result" and
                result["success"] is True):
            self.logger.warning("Unable to subscribe to HA events, id = %s", self._id)
            self.logger.warning(result)
            raise ValueError("Error subscribing to HA Events")

    async def _consume_events(self):
        ret = await run_in_executor(self, self.ws.recv)
        result = json.loads(ret)

        if not (result["id"] == self._id and result["type"] == "event"):
            self.logger.warning("Unexpected result from Home Assistant, id = %s", self._id)
            self.logger.warning(result)

        await self.AD.events.process_event(self.namespace, result["event"])

    async def get_updates(self):
        while True:
            self._id += 1
            # noinspection PyBroadException
            try:
                result = await self._connect()

                if result["type"] == "auth_required":
                    await self._authenticate()

                await self._subscribe_to_service_calls()

                while not self.stopping:
                    await self._consume_events()

                self._is_connected = False
            except:
                self._is_connected = False

                self.logger.warning("Disconnected from Home Assistant, retrying in 5 seconds")
                self.logger.debug('-' * 60)
                self.logger.debug("Unexpected error:")
                self.logger.debug('-' * 60)
                self.logger.debug(traceback.format_exc())
                self.logger.debug('-' * 60)
                await asyncio.sleep(5)
