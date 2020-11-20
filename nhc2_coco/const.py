import paho.mqtt.client as mqtt

MQTT_TLS_VERSION = 2
MQTT_PROTOCOL = mqtt.MQTTv311
MQTT_TRANSPORT = "tcp"

KEY_UUID = 'Uuid'
KEY_MODEL = 'Model'
KEY_TYPE = 'Type'
KEY_METHOD = 'Method'
KEY_ENTITY = 'entity'

DEV_TYPE_ACTION = 'action'

INTERNAL_KEY_CALLBACK = 'callbackHolder'


MQTT_METHOD_SYSINFO_PUBLISH = 'systeminfo.publish'
MQTT_METHOD_SYSINFO_PUBLISHED = 'systeminfo.published'
MQTT_METHOD_DEVICES_LIST = 'devices.list'
MQTT_METHOD_DEVICES_STATUS = 'devices.status'
MQTT_METHOD_DEVICES_CHANGED = 'devices.changed'

MQTT_RC_CODES = ['',
                 'Connection refused - incorrect protocol version',
                 'Connection refused - invalid client identifier',
                 'Connection refused - server unavailable',
                 'Connection refused - bad username or password',
                 'Connection refused - not authorised']

MQTT_TOPIC_SUFFIX_CMD = '/control/devices/cmd'
MQTT_TOPIC_SUFFIX_RSP = '/control/devices/rsp'
MQTT_TOPIC_SUFFIX_EVT = '/control/devices/evt'
MQTT_TOPIC_SUFFIX_SYS_EVT = '/system/evt'
MQTT_TOPIC_PUBLIC_CMD = '/system/cmd'
MQTT_TOPIC_PUBLIC_RSP = '/system/rsp'
MQTT_TOPIC_PUBLIC_AUTH_CMD = 'public/authentication/cmd'
MQTT_TOPIC_PUBLIC_AUTH_RSP = 'public/authentication/rsp'
