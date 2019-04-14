import paho.mqtt.client as mqtt

MQTT_TLS_VERSION = 2
MQTT_PROTOCOL = mqtt.MQTTv311
MQTT_TRANSPORT = "tcp"

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
MQTT_TOPIC_PUBLIC_CMD = 'public/system/cmd'
MQTT_TOPIC_PUBLIC_RSP = 'public/system/rsp'
