# pynhc2

License: MIT

## Usage

### Create a NHC2 object

```
NHC2(address, username, password, port, ca_path)
```

* __address__ - IP or host of the connected controller 
* __username__ - The UUID of the profile
* __password__ - The password
* __port__ - (optional) The MQTT port. Default = 8883
* __ca_path__ - (optional) Path of the CA file. Default = included CA file.

 example:

 ```
 coco = NHC2('192.168.1.2', 'abcdefgh-ijkl-mnop-qrst-uvwxyz012345', 'secret_password')
 ```
 
### What now?
 TODO - write doc....
 
## What can you do to help?

 * Contribute to this project with constructive issues, suggestions, PRs, etc.
 * Help me in any way to get support for more entities (eg dimmer)
