import json
import logging
import os
import re

import paho.mqtt.client as mqtt

from .coco_ip_by_mac import CoCoIpByMac
from .coco_light import CoCoLight
from .coco_switch import CoCoSwitch
from .const import MQTT_PROTOCOL, MQTT_TRANSPORT, MQTT_TOPIC_PUBLIC_RSP, MQTT_TOPIC_SUFFIX_RSP, \
    MQTT_TOPIC_SUFFIX_SYS_EVT, MQTT_TOPIC_SUFFIX_CMD, MQTT_TOPIC_SUFFIX_EVT, MQTT_TOPIC_PUBLIC_CMD, MQTT_RC_CODES, \
    KEY_UUID, KEY_ENTITY, KEY_MODEL, INTERNAL_KEY_CALLBACK, KEY_TYPE, DEV_TYPE_ACTION, MQTT_METHOD_SYSINFO_PUBLISH, \
    KEY_METHOD, MQTT_METHOD_DEVICES_LIST, MQTT_METHOD_SYSINFO_PUBLISHED, MQTT_METHOD_DEVICES_STATUS, \
    MQTT_METHOD_DEVICES_CHANGED
from .helpers import extract_devices

_LOGGER = logging.getLogger(__name__)


class CoCo:
    def __init__(self, address, username, password, port=8883, ca_path=None, switches_as_lights=False):
        self._address_is_mac = re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", address.lower())
        self._valid_switches = ['socket', 'switched-generic']
        self._valid_lights = ['light', 'dimmer']
        if ca_path is None:
            ca_path = os.path.dirname(os.path.realpath(__file__)) + '/coco_ca.pem'
        client = mqtt.Client(protocol=MQTT_PROTOCOL, transport=MQTT_TRANSPORT)
        client.username_pw_set(username, password)
        client.tls_set(ca_path)
        client.tls_insecure_set(True)
        self._client = client
        self._address = address
        self._port = port
        self._profile_creation_id = username
        self._all_devices = None
        self._device_callbacks = {}
        self._switches_as_lights = switches_as_lights
        self._lights = None
        self._lights_callback = lambda x: None
        self._switches = None
        self._switches_callback = lambda x: None
        self._system_info = None
        self._system_info_callback = lambda x: None

    def __del__(self):
        self._client.disconnect()

    def connect(self):

        def _on_message(client, userdata, message):
            topic = message.topic
            response = json.loads(message.payload)
            if topic == self._profile_creation_id + MQTT_TOPIC_PUBLIC_RSP and response[
                KEY_METHOD] == MQTT_METHOD_SYSINFO_PUBLISH:
                self._system_info = response
                self._system_info_callback(self._system_info)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP):
                if response[KEY_METHOD] == MQTT_METHOD_DEVICES_LIST:
                    client.unsubscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP)
                    actionable_devices = list(
                        filter(lambda d: d[KEY_TYPE] == DEV_TYPE_ACTION, extract_devices(response)))
                    existing_uuids = list(self._device_callbacks.keys())

                    for x in actionable_devices:
                        if x[KEY_UUID] not in existing_uuids:
                            self._device_callbacks[x[KEY_UUID]] = {INTERNAL_KEY_CALLBACK: None, KEY_ENTITY: None}

                    lights = [x for x in actionable_devices if
                              (x[KEY_MODEL] in self._valid_lights)
                              or (self._switches_as_lights
                                  and (x[KEY_MODEL] in self._valid_switches))
                              ]
                    if not self._switches_as_lights:
                        switches = [x for x in actionable_devices if x[KEY_MODEL] in self._valid_switches]
                    else:
                        switches = []

                    self._lights = []
                    for light in lights:
                        if self._device_callbacks[light[KEY_UUID]] and self._device_callbacks[light[KEY_UUID]][
                            KEY_ENTITY] and \
                                self._device_callbacks[light[KEY_UUID]][KEY_ENTITY].uuid:
                            self._device_callbacks[light[KEY_UUID]][KEY_ENTITY].update_dev(light)
                        else:
                            self._device_callbacks[light[KEY_UUID]][KEY_ENTITY] = CoCoLight(light,
                                                                                            self._device_callbacks[
                                                                                                light[KEY_UUID]],
                                                                                            self._client,
                                                                                            self._profile_creation_id)
                        self._lights.append(self._device_callbacks[light[KEY_UUID]][KEY_ENTITY])
                    self._switches = []
                    for switch in switches:
                        if self._device_callbacks[switch[KEY_UUID]] and self._device_callbacks[switch[KEY_UUID]][
                            KEY_ENTITY] and \
                                self._device_callbacks[switch[KEY_UUID]][KEY_ENTITY].uuid:
                            self._device_callbacks[switch[KEY_UUID]][KEY_ENTITY].update_dev(switch)
                        else:
                            self._device_callbacks[switch[KEY_UUID]][KEY_ENTITY] = CoCoSwitch(switch,
                                                                                              self._device_callbacks[
                                                                                                  switch[KEY_UUID]],
                                                                                              self._client,
                                                                                              self._profile_creation_id)
                        self._switches.append(self._device_callbacks[switch[KEY_UUID]][KEY_ENTITY])

                    self._lights_callback(self._lights)
                    self._switches_callback(self._switches)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_SYS_EVT) \
                    and response[KEY_METHOD] == MQTT_METHOD_SYSINFO_PUBLISHED:
                # If the connected controller publishes sysinfo... we expect something to have changed.
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP, qos=1)
                client.publish(self._profile_creation_id + MQTT_TOPIC_SUFFIX_CMD, '{"Method":"devices.list"}', 1)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_EVT) \
                    and (response[KEY_METHOD] == MQTT_METHOD_DEVICES_STATUS or response[
                KEY_METHOD] == MQTT_METHOD_DEVICES_CHANGED):
                devices = extract_devices(response)
                for device in devices:
                    try:
                        if KEY_UUID in device:
                            self._device_callbacks[device[KEY_UUID]][INTERNAL_KEY_CALLBACK](device)
                    except:
                        pass
                return

        def _on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("connetec %d" % rc)
                _LOGGER.info('Connected!')
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP, qos=1)
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_PUBLIC_RSP, qos=1)
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_EVT, qos=1)
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_SYS_EVT, qos=1)
                client.publish(self._profile_creation_id + MQTT_TOPIC_PUBLIC_CMD, '{"Method":"systeminfo.publish"}', 1)
                client.publish(self._profile_creation_id + MQTT_TOPIC_SUFFIX_CMD, '{"Method":"devices.list"}', 1)
            elif MQTT_RC_CODES[rc]:
                raise Exception(MQTT_RC_CODES[rc])
            else:
                raise Exception('Unknown error')

        def _on_disconnect(client, userdata, rc):
            def update_ip(ip):
                if self._client._host != ip:
                    self._client.connect_async(ip, self._port, keepalive=5, clean_start=True)
                    self._client.reconnect()

            _LOGGER.warning('Disconnected')
            if self._address_is_mac:
                CoCoIpByMac(self._address, update_ip)
            for uuid, device_callback in self._device_callbacks.items():
                offline = {'Online': 'False', KEY_UUID: uuid}
                device_callback[INTERNAL_KEY_CALLBACK](offline)

        self._client.on_message = _on_message
        self._client.on_connect = _on_connect
        self._client.on_disconnect = _on_disconnect
        if self._address_is_mac:
            def connect_with_ip(ip):
                self._client.connect_async(ip, self._port, keepalive=5, clean_start=True)
                self._client.loop_start()
            CoCoIpByMac(self._address, connect_with_ip)
        else:
            self._client.connect_async(self._address, self._port, clean_start=True)
            self._client.loop_start()

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()

    def get_systeminfo(self, callback):
        self._system_info_callback = callback
        if self._system_info:
            self._system_info_callback(self._system_info)

    def get_lights(self, callback):
        self._lights_callback = callback
        if self._lights:
            self._lights_callback(self._lights)

    def get_switches(self, callback):
        self._switches_callback = callback
        if self._switches:
            self._switches_callback(self._switches)

    def _emit_switches(self):
        self._switches_callback(self._switches)
