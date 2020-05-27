"""Data interface with Home-Assistant instance."""
import asyncio
import json
import ssl
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

import voluptuous as vol
import websocket

from garagepi.common.async_utils import create_task
from garagepi.common.const import CONF_NAME, API_HASS
from garagepi.common.validation import entity_id, constant_value
from garagepi.domain.models.StateChangedEvent import StateChangedEvent
from garagepi.framework.data.Api import Api

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
    vol.Optional(CONF_CERT_VERIFY, default=True): vol.Coerce(bool),
    vol.Required(CONF_NAME): constant_value(API_HASS)
})


class HassApi(Api):
    """Interface with Home-Assistant instance."""
    _ws_client = None
    _id = 0
    _token = None
    _reading_messages = False
    _hass_booting = False
    _executor = ThreadPoolExecutor()

    def __init__(self, configuration, open_command, close_command):
        super().__init__(configuration, open_command, close_command)

    def _validate_configuration(self, configuration):
        return HASS_CONFIGURATION_SCHEMA(configuration)

    def _initialize(self):
        create_task(self.get_updates())

    async def report_state(self, garage_door):
        new_state = str(garage_door)
        payload = StateChangedEvent(
            garage_door.entity_id,
            new_state,
            self._previous_state
        )

        self._previous_state = new_state
        await asyncio.get_event_loop().run_in_executor(
            self._executor,
            self._ws_client.send,
            payload
        )

    async def _connect(self):
        self._token = self.config.get(CONF_TOKEN, None)
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
            "{}/usecase/websocket".format(url), sslopt=ssl_options
        )
        res = await asyncio.get_event_loop().run_in_executor(self._executor, self._ws_client.recv)
        return json.loads(res)

    async def _authenticate(self):
        if self._token is not None:
            auth = json.dumps({
                "type": "auth",
                "access_token": self._token
            })
        else:
            raise ValueError(
                "HASS requires authentication and none provided in plugin config")

        await asyncio.get_event_loop().run_in_executor(self._executor, self._ws_client.send, auth)
        result = json.loads(self._ws_client.recv())
        if result["type"] != "auth_ok":
            self.logger.warning("Error in authentication")
            raise ValueError("Error in authentication")

    async def _subscribe_to_service_calls(self):
        sub = json.dumps({
            "id": self._id,
            "type": "subscribe_events",
            "event_type": "call_service"
        })
        await asyncio.get_event_loop().run_in_executor(self._executor, self._ws_client.send, sub)
        result = json.loads(self._ws_client.recv())
        if not (result["id"] == self._id and
                result["type"] == "result" and
                result["success"] is True):
            self.logger.warning("Unable to subscribe to HA events, id = %s", self._id)
            self.logger.warning(result)
            raise ValueError("Error subscribing to HA Events")

    async def _consume_events(self):
        ret = await asyncio.get_event_loop().run_in_executor(self._executor, self._ws_client.recv)
        result = json.loads(ret)

        if not (result["id"] == self._id and result["type"] == "event"):
            self.logger.warning("Unexpected result from Home Assistant, id = %s", self._id)
            self.logger.warning(result)

        event = result.get('Event', None)
        self._process_event(event)

    async def get_updates(self):
        while True:
            self._id += 1
            # noinspection PyBroadException
            try:
                result = await self._connect()

                if result["type"] == "auth_required":
                    await self._authenticate()

                await self._subscribe_to_service_calls()

                while True:
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
