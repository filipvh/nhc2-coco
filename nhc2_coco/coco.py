import json
import logging
import os
from typing import List, Callable

import paho.mqtt.client as mqtt

from .helpers import extract_devices
from .const import MQTT_PROTOCOL, MQTT_TRANSPORT, MQTT_TOPIC_PUBLIC_RSP, MQTT_TOPIC_SUFFIX_RSP, \
    MQTT_TOPIC_SUFFIX_SYS_EVT, MQTT_TOPIC_SUFFIX_CMD, MQTT_TOPIC_SUFFIX_EVT, MQTT_TOPIC_PUBLIC_CMD, MQTT_RC_CODES
from .coco_light import CoCoLight
from .coco_switch import CoCoSwitch

_LOGGER = logging.getLogger(__name__)


class CoCo:
    def __init__(self, address, username, password, port=8883, ca_path=None, switches_as_lights=False):
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
            if topic == MQTT_TOPIC_PUBLIC_RSP and response['Method'] == 'systeminfo.publish':
                self._system_info = response
                self._system_info_callback(self._system_info)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP):
                if response['Method'] == 'devices.list':
                    client.unsubscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP)
                    devices = extract_devices(response)
                    existing_uuids = list(self._device_callbacks.keys())

                    valid_switches = ['socket', 'switched-generic']
                    valid_lights = ['light', 'dimmer']
                    for x in devices:
                        if x['Uuid'] not in existing_uuids:
                            self._device_callbacks[x['Uuid']] = {'callbackHolder': None, 'entity': None}

                    lights = [x for x in devices if
                              (x['Model'] in valid_lights)
                              or (self._switches_as_lights
                                  and (x['Model'] in valid_switches))
                              ]
                    if not self._switches_as_lights:
                        switches = [x for x in devices if x['Model'] in valid_switches]
                    else:
                        switches = []

                    self._lights = []
                    for light in lights:
                        if self._device_callbacks[light['Uuid']] and self._device_callbacks[light['Uuid']]['entity'] and \
                                self._device_callbacks[light['Uuid']]['entity'].uuid:
                            self._device_callbacks[light['Uuid']]['entity'].update_dev(light)
                        else:
                            self._device_callbacks[light['Uuid']]['entity'] = CoCoLight(light, self._device_callbacks[
                                light['Uuid']], self._client, self._profile_creation_id)
                        self._lights.append(self._device_callbacks[light['Uuid']]['entity'])
                    self._switches = []
                    for switch in switches:
                        if self._device_callbacks[switch['Uuid']] and self._device_callbacks[switch['Uuid']][
                            'entity'] and \
                                self._device_callbacks[switch['Uuid']]['entity'].uuid:
                            self._device_callbacks[switch['Uuid']]['entity'].update_dev(switch)
                        else:
                            self._device_callbacks[switch['Uuid']]['entity'] = CoCoSwitch(switch,
                                                                                          self._device_callbacks[
                                                                                              switch['Uuid']],
                                                                                          self._client,
                                                                                          self._profile_creation_id)
                        self._switches.append(self._device_callbacks[switch['Uuid']]['entity'])

                    self._lights_callback(self._lights)
                    self._switches_callback(self._switches)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_SYS_EVT) \
                    and response['Method'] == 'systeminfo.published':
                # If the connected controller publishes sysinfo... we expect something to have changed.
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP, qos=1)
                client.publish(self._profile_creation_id + MQTT_TOPIC_SUFFIX_CMD, '{"Method":"devices.list"}', 1)
                return
            if topic == (self._profile_creation_id + MQTT_TOPIC_SUFFIX_EVT) \
                    and (response['Method'] == 'devices.status' or response['Method'] == 'devices.changed'):
                devices = extract_devices(response)
                for device in devices:
                    if device['Uuid'] and self._device_callbacks[device['Uuid']]:
                        self._device_callbacks[device['Uuid']]['callbackHolder'](device)

                return

        def _on_connect(client, userdata, flags, rc):
            if rc == 0:
                _LOGGER.info('Connected!')
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_RSP, qos=1)
                client.subscribe(MQTT_TOPIC_PUBLIC_RSP, qos=1)
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_EVT, qos=1)
                client.subscribe(self._profile_creation_id + MQTT_TOPIC_SUFFIX_SYS_EVT, qos=1)
                client.publish(MQTT_TOPIC_PUBLIC_CMD, '{"Method":"systeminfo.publish"}', 1)
                client.publish(self._profile_creation_id + MQTT_TOPIC_SUFFIX_CMD, '{"Method":"devices.list"}', 1)
            elif MQTT_RC_CODES[rc]:
                raise Exception(MQTT_RC_CODES[rc])
            else:
                raise Exception('Unknown error')

        def _on_disconnect(client, userdata, rc):
            _LOGGER.warning('Disconnected')
            for uuid, device_callback in self._device_callbacks.items():
                offline = {'Online': 'False', 'Uuid': uuid}
                device_callback['callbackHolder'](offline)

        self._client.on_message = _on_message
        self._client.on_connect = _on_connect
        self._client.on_disconnect = _on_disconnect

        self._client.connect_async(self._address, self._port)
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
