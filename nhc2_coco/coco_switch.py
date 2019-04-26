from .helpers import status_prop_in_object_is_on, extract_status_object
from .coco_entity import CoCoEntity
import json

TOPIC_SUFFIX_CMD = '/control/devices/cmd'


class CoCoSwitch(CoCoEntity):

    @property
    def is_on(self):
        return self._state

    def __init__(self, dev, callback_container, client, profile_creation_id):
        super().__init__(dev, callback_container, client, profile_creation_id)
        self.update_dev(dev, callback_container)

    def turn_on(self):
        self._change_status('On')

    def turn_off(self):
        self._change_status('Off')

    def update_dev(self, dev, callback_container=None):
        has_changed = super().update_dev(dev, callback_container)
        status_object = extract_status_object(dev)
        if self._check_for_status_change(status_object):
            self._state = status_prop_in_object_is_on(status_object)
            has_changed = True
        return has_changed

    def _update(self, dev):
        has_changed = self.update_dev(dev)
        if has_changed:
            self._state_changed()

    def _check_for_status_change(self, property_object_with_status):
        return property_object_with_status \
               and 'Status' in property_object_with_status \
               and self._state != (status_prop_in_object_is_on(property_object_with_status))

    def _change_status(self, status):
        command = {"Method": "devices.control", "Params": [
            {"Devices": [{"Properties": [{"Status": status}], "Uuid": self._uuid}]}
        ]}
        self._client.publish(self._profile_creation_id + TOPIC_SUFFIX_CMD, json.dumps(command), 1)
