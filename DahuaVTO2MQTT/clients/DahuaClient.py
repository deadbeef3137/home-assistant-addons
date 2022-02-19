import asyncio
import hashlib
import json
import logging
import struct
import sys
from threading import Timer
from typing import Optional, Dict, Any, Callable

import requests

from clients.MQTTClient import MQTTClient
from common.consts import *
from models.DahuaConfigData import DahuaConfigurationData

_LOGGER = logging.getLogger(__name__)


class DahuaClient(asyncio.Protocol):
    dahua_config: DahuaConfigurationData

    requestId: int
    sessionId: int
    keep_alive_interval: int
    realm: Optional[str]
    random: Optional[str]
    mqtt_client: MQTTClient
    dahua_details: Dict[str, Any]
    base_url: str
    hold_time: int
    lock_status: Dict[int, bool]
    data_handlers: Dict[Any, Callable[[Any, str], None]]
    mqtt_handlers: Dict[str, Callable[[dict], None]]

    def __init__(self):
        self.dahua_config = DahuaConfigurationData()
        self.mqtt_client = MQTTClient(self, self.on_mqtt_message)

        self.dahua_details = {}

        self.realm = None
        self.random = None
        self.request_id = 1
        self.sessionId = 0
        self.keep_alive_interval = 0
        self.transport = None
        self.hold_time = 0
        self.lock_status = {}
        self.data_handlers = {}
        self.mqtt_handlers = {
            TOPIC_DOOR: self.access_control_open_door,
            TOPIC_MUTE: self.access_control_open_door
        }

        self._loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        _LOGGER.debug("Connection established")

        try:
            self.transport = transport

            self.mqtt_client.initialize()
            self.pre_login()

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to handle message, error: {ex}, Line: {exc_tb.tb_lineno}")

    def data_received(self, data):
        try:
            message = self.parse_response(data)
            _LOGGER.debug(f"Data received: {message}")

            message_id = message.get("id")

            handler: Callable = self.data_handlers.get(message_id, self.handle_default)
            handler(message)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to handle message, error: {ex}, Line: {exc_tb.tb_lineno}")

    @staticmethod
    def on_mqtt_message(self, topic: str, payload: dict):
        try:
            if topic in self.mqtt_handlers:
                action = self.mqtt_handlers[topic]
                action(payload)
            else:
                _LOGGER.warning(f"No MQTT message handler for {topic}, Payload: {payload}")
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to handle callback, error: {ex}, Line: {exc_tb.tb_lineno}")

    def handle_notify_event_stream(self, params):
        try:
            event_list = params.get("eventList")

            for message in event_list:
                code = message.get("Code")

                for k in self.dahua_details:
                    if k in DAHUA_ALLOWED_DETAILS:
                        message[k] = self.dahua_details.get(k)

                self.mqtt_client.publish(f"{code}/Event", message)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to handle event, error: {ex}, Line: {exc_tb.tb_lineno}")

    def handle_default(self, message):
        _LOGGER.info(f"Data received without handler: {message}")

    def eof_received(self):
        _LOGGER.info('Server sent EOF message')

        self._loop.stop()

    def connection_lost(self, exc):
        _LOGGER.error('server closed the connection')

        self._loop.stop()

    def send(self, action, handler, params=None):
        if params is None:
            params = {}

        self.request_id += 1

        message_data = {
            "id": self.request_id,
            "session": self.sessionId,
            "magic": "0x1234",
            "method": action,
            "params": params
        }

        self.data_handlers[self.request_id] = handler

        if not self.transport.is_closing():
            message = self.convert_message(message_data)

            self.transport.write(message)

    @staticmethod
    def convert_message(data):
        message_data = json.dumps(data, indent=4)

        header = struct.pack(">L", 0x20000000)
        header += struct.pack(">L", 0x44484950)
        header += struct.pack(">d", 0)
        header += struct.pack("<L", len(message_data))
        header += struct.pack("<L", 0)
        header += struct.pack("<L", len(message_data))
        header += struct.pack("<L", 0)

        message = header + message_data.encode("utf-8")

        return message

    def pre_login(self):
        _LOGGER.debug("Prepare pre-login message")

        def handle_pre_login(message):
            error = message.get("error")
            params = message.get("params")

            if error is not None:
                error_message = error.get("message")

                if error_message == "Component error: login challenge!":
                    self.random = params.get("random")
                    self.realm = params.get("realm")
                    self.sessionId = message.get("session")

                    self.login()

        request_data = {
            "clientType": "",
            "ipAddr": "(null)",
            "loginType": "Direct",
            "userName": self.dahua_config.username,
            "password": ""
        }

        self.send(DAHUA_GLOBAL_LOGIN, handle_pre_login, request_data)

    def login(self):
        _LOGGER.debug("Prepare login message")

        def handle_login(message):
            params = message.get("params")
            keep_alive_interval = params.get("keepAliveInterval")

            if keep_alive_interval is not None:
                self.keep_alive_interval = keep_alive_interval - 5

                self.load_access_control()
                self.load_version()
                self.load_serial_number()
                self.load_device_type()
                self.attach_event_manager()

                Timer(self.keep_alive_interval, self.keep_alive).start()

        password = self._get_hashed_password(self.random, self.realm, self.dahua_config.username, self.dahua_config.password)

        request_data = {
            "clientType": "",
            "ipAddr": "(null)",
            "loginType": "Direct",
            "userName": self.dahua_config.username,
            "password": password,
            "authorityType": "Default"
        }

        self.send(DAHUA_GLOBAL_LOGIN, handle_login, request_data)

    def attach_event_manager(self):
        _LOGGER.info("Attach event manager")

        def handle_attach_event_manager(message):
            method = message.get("method")
            params = message.get("params")

            if method == "client.notifyEventStream":
                self.handle_notify_event_stream(params)

        request_data = {
            "codes": ['All']
        }

        self.send(DAHUA_EVENT_MANAGER_ATTACH, handle_attach_event_manager, request_data)

    def load_access_control(self):
        _LOGGER.info("Get access control configuration")

        def handle_access_control(message):
            params = message.get("params")
            table = params.get("table")

            for item in table:
                access_control = item.get('AccessProtocol')

                if access_control == 'Local':
                    self.hold_time = item.get('UnlockReloadInterval')

                    _LOGGER.info(f"Hold time: {self.hold_time}")

        request_data = {
            "name": "AccessControl"
        }

        self.send(DAHUA_CONFIG_MANAGER_GETCONFIG, handle_access_control, request_data)

    def load_version(self):
        _LOGGER.info("Get version")

        def handle_version(message):
            params = message.get("params")
            version_details = params.get("version", {})
            build_date = version_details.get("BuildDate")
            version = version_details.get("Version")

            self.dahua_details[DAHUA_VERSION] = version
            self.dahua_details[DAHUA_BUILD_DATE] = build_date

            _LOGGER.info(f"Version: {version}, Build Date: {build_date}")

        self.send(DAHUA_MAGICBOX_GETSOFTWAREVERSION, handle_version)

    def load_device_type(self):
        _LOGGER.info("Get device type")

        def handle_device_type(message):
            params = message.get("params")
            device_type = params.get("type")

            self.dahua_details[DAHUA_DEVICE_TYPE] = device_type

            _LOGGER.info(f"Device Type: {device_type}")

        self.send(DAHUA_MAGICBOX_GETDEVICETYPE, handle_device_type)

    def load_serial_number(self):
        _LOGGER.info("Get serial number")

        def handle_serial_number(message):
            params = message.get("params")
            table = params.get("table", {})
            serial_number = table.get("UUID")

            self.dahua_details[DAHUA_SERIAL_NUMBER] = serial_number

            _LOGGER.info(f"Serial Number: {serial_number}")

        request_data = {
            "name": "T2UServer"
        }

        self.send(DAHUA_CONFIG_MANAGER_GETCONFIG, handle_serial_number, request_data)

    def keep_alive(self):
        _LOGGER.debug("Keep alive")

        def handle_keep_alive(message):
            Timer(self.keep_alive_interval, self.keep_alive).start()

        request_data = {
            "timeout": self.keep_alive_interval,
            "action": True
        }

        self.send(DAHUA_GLOBAL_KEEPALIVE, handle_keep_alive, request_data)

    def run_cmd_mute(self, payload: dict):
        _LOGGER.debug("Keep alive")

        def handle_run_cmd_mute(message):
            _LOGGER.info("Call was muted")

        request_data = {
            "command": "hc"
        }

        self.send(DAHUA_CONSOLE_RUN_CMD, handle_run_cmd_mute, request_data)

    def access_control_open_door(self, payload: dict):
        door_id = payload.get("Door", 1)

        is_locked = self.lock_status.get(door_id, False)
        should_unlock = False

        try:
            if is_locked:
                _LOGGER.info(f"Access Control - Door #{door_id} is already unlocked, ignoring request")

            else:
                is_locked = True
                should_unlock = True

                self.lock_status[door_id] = is_locked
                self.publish_lock_state(door_id, False)

                url = f"{self.base_url}{ENDPOINT_ACCESS_CONTROL}{door_id}"

                response = requests.get(url, verify=False, auth=self.dahua_config.auth)

                response.raise_for_status()

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to open door, error: {ex}, Line: {exc_tb.tb_lineno}")

        if should_unlock and is_locked:
            Timer(float(self.hold_time), self.magnetic_unlock, (self, door_id)).start()

    @staticmethod
    def magnetic_unlock(self, door_id):
        self.lock_status[door_id] = False
        self.publish_lock_state(door_id, True)

    def publish_lock_state(self, door_id: int, is_locked: bool):
        state = "Locked" if is_locked else "Unlocked"

        _LOGGER.info(f"Access Control - {state} magnetic lock #{door_id}")

        message = {
            "door": door_id,
            "isLocked": is_locked
        }

        self.mqtt_client.publish("/MagneticLock/Status", message)

    @staticmethod
    def parse_response(response):
        result = None

        try:
            response_parts = str(response).split("\\x00")
            for response_part in response_parts:
                if response_part.startswith("{"):
                    end = response_part.rindex("}") + 1
                    message = response_part[0:end]

                    result = json.loads(message)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()

            _LOGGER.error(f"Failed to read data: {response}, error: {e}, Line: {exc_tb.tb_lineno}")

        return result

    @staticmethod
    def _get_hashed_password(random, realm, username, password):
        password_str = f"{username}:{realm}:{password}"
        password_bytes = password_str.encode('utf-8')
        password_hash = hashlib.md5(password_bytes).hexdigest().upper()

        random_str = f"{username}:{random}:{password_hash}"
        random_bytes = random_str.encode('utf-8')
        random_hash = hashlib.md5(random_bytes).hexdigest().upper()

        return random_hash
