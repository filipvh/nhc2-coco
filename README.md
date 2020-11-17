# pynhc2

License: MIT

## Usage

### Create a NHC2 object

```
NHC2(address, username, password, port, ca_path, switches_as_lights)
```

* __address__ - IP or host of the connected controller 
* __username__ - The UUID of the profile
* __password__ - The password
* __port__ - (optional) The MQTT port. Default = 8883
* __ca_path__ - (optional) Path of the CA file. Default = included CA file.
* __switches_as_lights__ - (optional) socket and switched-generic show up as lights.

 example:

 ```
 coco = NHC2('192.168.1.2', 'abcdefgh-ijkl-mnop-qrst-uvwxyz012345', 'secret_password')
 ```
 
### What is supported?
light, socket, switched-generic, dimmer

### What now?
 TODO - write doc.
 
 TODO - refactor into logical groups that match niko documentation (NHC Relay Action, NHC Dimmer Action, etc)
 
## What can you do to help?

 * Contribute to this project with constructive issues, suggestions, PRs, etc.
 * Help me in any way to get support for more entities (eg heating)
