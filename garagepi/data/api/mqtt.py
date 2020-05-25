import asyncio
import json
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

import paho.mqtt.client as mqtt
import voluptuous as vol

from garagepi.common.const import API_MQTT, CONF_NAME
from garagepi.common.validation import valid_subscribe_topic, valid_publish_topic, \
    valid_state_template, constant_value, ensure_list
from garagepi.framework.data.Api import Api

CONF_BROKER_URL = 'broker_url'
CONF_BROKER_PORT = 'broker_port'
CONF_CLIENT_ID = 'client_id'
CONF_USER = 'user'
CONF_PASSWORD = 'password'
CONF_COMMAND_TOPICS = 'command_topics'
CONF_STATE_TOPIC = 'state_topic'
CONF_STATE_PAYLOAD_TEMPLATE = 'state_payload_template'
CONF_TOPIC = 'topic'
CONF_PAYLOAD = 'payload'
CONF_QOS = 'qos'
CONF_RETAIN = 'retain'
CONF_LAST_WILL = 'last_will'
CONF_BIRTH = 'birth'
# TODO: TLS

DEFAULT_STATE_TEMPLATE = '{' \
                         ' "state": "$TEMPLATE_STATE",' \
                         ' "attributes": {' \
                         '  $TEMPLATE_ATTR_CURRENT_POSITION' \
                         ' }' \
                         '}'

MQTT_PROTOCOLS = [
    '3.1.1',
    '3.1'
]

BIRTH_WILL_SCHEMA = vol.Schema({
    vol.Required(CONF_TOPIC): valid_publish_topic,
    vol.Required(CONF_PAYLOAD): str,
    vol.Optional(CONF_QOS, default=0): vol.All(
        vol.Coerce(int),
        vol.Range(0, 2)
    ),
    vol.Optional(CONF_RETAIN, default=False): vol.Coerce(bool)
})

MQTT_CONFIGURATION_SCHEMA = vol.Schema({
    vol.Required(CONF_BROKER_URL): str,
    vol.Optional(CONF_BROKER_PORT, default=1883): vol.All(
        vol.Coerce(int),
        vol.Range(min=1, max=65535)),
    vol.Optional(CONF_CLIENT_ID): str,
    vol.Optional(CONF_USER): str,
    vol.Optional(CONF_PASSWORD): str,
    vol.Required(CONF_COMMAND_TOPICS): vol.All(
        ensure_list,
        [valid_subscribe_topic]
    ),
    vol.Required(CONF_STATE_TOPIC): valid_publish_topic,
    vol.Optional(CONF_STATE_PAYLOAD_TEMPLATE): valid_state_template,
    vol.Optional(CONF_QOS, default=0): vol.All(
        vol.Coerce(int),
        vol.Range(0, 2)
    ),
    vol.Optional(CONF_RETAIN, default=False): vol.Coerce(bool),
    vol.Optional(CONF_LAST_WILL): BIRTH_WILL_SCHEMA,
    vol.Optional(CONF_BIRTH): BIRTH_WILL_SCHEMA,
    vol.Optional(CONF_NAME, default=API_MQTT): constant_value(API_MQTT)
})


class MqttApi(Api):
    """Interface with MQTT broker."""

    _client = None
    _first_connection = True

    def __init__(self, configuration, open_command, close_command):
        super().__init__(configuration, open_command, close_command)

    def _initialize(self):
        self._client = mqtt.Client(
            client_id=self.config.get(CONF_CLIENT_ID, 'GaragePi-Assistant')
        )
        if self.config.get(CONF_STATE_PAYLOAD_TEMPLATE, None) is None:
            self.config[CONF_STATE_PAYLOAD_TEMPLATE] = DEFAULT_STATE_TEMPLATE
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._connect_event = asyncio.Event()

    def _start(self):
        try:
            if self._first_connection:
                self.logger.warning('Config %s', str(self.config))
                if CONF_USER in self.config and CONF_PAYLOAD in self.config:
                    self._client.username_pw_set(self.config[CONF_USER],
                                                 self.config[CONF_PASSWORD])

                if CONF_LAST_WILL in self.config:
                    self._client.will_set(
                        self.config[CONF_LAST_WILL][CONF_TOPIC],
                        self.config[CONF_LAST_WILL][CONF_PAYLOAD],
                        self.config[CONF_LAST_WILL][CONF_QOS],
                        self.config[CONF_LAST_WILL][CONF_RETAIN]
                    )
            self._client.connect_async(
                self.config[CONF_BROKER_URL],
                self.config[CONF_BROKER_PORT],
            )
            self._client.loop_start()
        except Exception as err:
            self.logger.error(str(err))

    def _on_connect(self, client, userdata, flags, rc):
        # noinspection PyBroadException
        try:
            error_message = ""
            if rc == 0:  # Successful connection
                for topic in self.config[CONF_COMMAND_TOPICS]:
                    result = self._client.subscribe(topic)
                    if result[0] != 0:
                        self.logger.error('Unable to subscribe to command topic %s',
                                          topic)
                self._is_connected = True

            elif rc == 1:
                error_message = "Connection was refused due to Incorrect Protocol Version"

            elif rc == 2:
                error_message = "Connection was refused due to Invalid Client Identifier"

            elif rc == 3:
                error_message = "Connection was refused due to Server Unavailable"
            elif rc == 4:
                error_message = "Connection was refused due to Bad Username or Password"
            elif rc == 5:
                error_message = "Connection was refused due to Not Authorised"
            else:
                error_message = "Connection was refused. Please check configuration settings"

            # means there was an error
            if error_message != "":
                self.logger.critical("Could not complete MQTT initialization, for %s",
                                     error_message)

            # continue processing
            self._connect_event.set()
        except:
            self.logger.critical("There was an error while trying to setup the Mqtt Service")
            self.logger.warn(
                'There was an error while trying to setup the MQTT Service, with Traceback: %s',
                traceback.format_exc())

    def _on_message(self, client, userdata, msg):
        try:
            self.logger.warning("Message Received: Topic = %s, Payload = %s", msg.topic, msg.payload.decode())
            try:
                payload_dict = json.loads(msg.payload.decode())
            except TypeError:
                self.logger.critical("Payload is not JSON")
                return

            self._process_event(payload_dict)
        except UnicodeDecodeError:
            self.logger.warning("Unable to decode MQTT message")
            self.logger.debug('Unable to decode MQTT message, with Traceback: %s',
                              traceback.format_exc())
        except Exception as e:
            self.logger.critical(
                "There was an error while processing an MQTT message: {} {}".format(type(e), e))
            self.logger.debug(
                'There was an error while processing an MQTT message, with Traceback: %s',
                traceback.format_exc())

    def _on_disconnect(self, client, userdata, rc):
        # noinspection PyBroadException
        try:
            if rc == 0:
                self.logger.warning("Disconnected successfully")
                return

            self._is_connected = False
            self.logger.critical("MQTT Client Disconnected Abruptly. Will attempt reconnection")
            self.logger.warn("Return code: %s", rc)
            self.logger.warn("userdata: %s", userdata)
        except:
            self.logger.critical("There was an error while disconnecting from the Mqtt Service")
            self.logger.warn(
                'There was an error while disconnecting from the MQTT Service, with Traceback: %s',
                traceback.format_exc())

    def _validate_configuration(self, configuration):
        return MQTT_CONFIGURATION_SCHEMA(configuration)

    async def get_updates(self):
        executor = ThreadPoolExecutor()
        while True:
            if self._is_connected:
                await asyncio.sleep(5)
                continue
            # noinspection PyBroadException
            try:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(executor, self._start), 5.0)
                await asyncio.wait_for(self._connect_event.wait(), 5.0)

            except asyncio.TimeoutError:
                self.logger.warning(str(self.config))
                self.logger.critical(
                    "Could not Complete Connection to Broker, please Ensure Broker at URL %s:%s is"
                    " correct and broker is not down and restart the application",
                    self.config[CONF_BROKER_URL], self.config[CONF_BROKER_PORT])

                self._client.loop_stop()
                # disconnect so it won't attempt reconnection if the broker was to come up
                self._client.disconnect()

    def report_state(self, garage_door):
        self._client.publish(
            self.config[CONF_STATE_TOPIC],
            json.dumps({
                'state': garage_door.state,
                'attributes': garage_door.attributes
            }),
            qos=1,
            retain=1
        )
