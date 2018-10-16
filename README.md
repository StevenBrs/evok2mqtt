# evok2mqtt
Read EVOK Websocket messages and send them to MQTT daemon


I had a hard time connecting my Home Assistant to my Unipi Neuron + extension using modbus, and performance was not acceptable.
I decided to give EVOK a try, but noticed that websockets were not usable from Home Assistant.
REST calls did work for commands, but didn't reflect state changes from other sources.

So I wrote my first Python program to act as a layer between EVOK Websockets and MQTT.

As always I try to create my programs as dynamically as possible, so I created 2 files:
* evok2mqtt: translates everything received from Websockets to Modbus.  For now the topics are 'neuron/devtype/identifier'
* evok2HAconfig: reads all devices from EVOK and creates a Home Assistant package including:
  * MQTT settings (static to localhost for now)
  * some shell commands to restart evok-related services
  * some scripts to manage evok-related services, read all device states, save unipi config to nvram
  * An automation to read all device states on HA startup
  * switches for the relays and leds
  * binary sensors for the digital inputs
  * groups per device type per unipi unit + management group
  * a view that displays all evok entities
  
usage:
(this is how I used it for now; planning on making it more versatile in the future)
  * Use the EVOK rpi image from Unipi
  * Copy of pull all files to a directory on it (eg /root/evok2mqtt)
  * Install the dependencies:
    # pip install websocket-client
    # pip install paho-mqtt
  * edit the evok2mqtt.py file to suit your needs (ip addresses in last section)
  * enable systemd service:
    # systemctl enable /path/to/evok2mqtt.service
  * edit evok2HAconfig.py file to suit your needs (ip addresses, passwords, enable/disable device types, ...)
  * Test the HA config:
    # python2 /path/to/evok2HAconfig.py
  * Create HA package for EVOK:
    # mkdir /path/to/HA/confdir/packages
    # python2 /path/to/evok2HAconfig.py > /path/to/HA/confdir/packages/evok.yaml (careful, this will overwrite without warning !!)
  * Restart Home Assistant from the webinterface or from command line. In case of a docker instance:
    # docker restart homeassistant

That's it for now.

Please note: I'm a sysadmin and I know my way around PHP and Delphi, but I'm not a programmer and I'm new to Python.
Feel free to correct my code, to explain my mistakes, and to make me smarter :-)
