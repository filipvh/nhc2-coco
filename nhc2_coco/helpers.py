
def extract_devices(response):
    params = response['Params']
    param_with_devices = next(filter((lambda x: x and 'Devices' in x), params), None)
    return param_with_devices['Devices']


def extract_status_object(dev):
    if dev and 'Properties' in dev:
        properties = dev['Properties']
        if properties:
            return next(filter((lambda x: x and 'Status' in x), properties), None)
        else:
            return None
    else:
        return None

def extract_brightness_object(dev):
    if dev and 'Properties' in dev:
        properties = dev['Properties']
        if properties:
            return next(filter((lambda x: x and 'Brightness' in x), properties), None)
        else:
            return None
    else:
        return None


def status_prop_in_object_is_on(property_object_with_status):
    return property_object_with_status['Status'] == 'On'
