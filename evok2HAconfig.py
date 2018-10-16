import json
import subprocess

# ["input", "relay", "ai", "ao", "led", "wd", "neuron", "uart", "register", "wifi"]
devtypes={
  "input":{"type": "binary_sensor", "attr":{
      "state_topic":"neuron/%d/%c", 
      "value_template":"'{{value_json.value}}'",
      "payload_on":"1",
      "payload_off":"0",
      "json_attributes":["mode","ds_mode","counter"]}},
  "relay":{"type": "switch", "attr":{
      "state_topic":"neuron/%d/%c", 
      "command_topic":"neuron/%d/%c",
      "value_template":"'{{value_json.value}}'",
      "payload_on":"1",
      "payload_off":"0"}},
  #"ai":{"type": "sensor"},
  #"ao":{"type": "input_number"},
  "led":{"type": "switch", "attr":{
      "state_topic":"neuron/%d/%c", 
      "command_topic":"neuron/%d/%c",
      "value_template":"'{{value_json.value}}'",
      "payload_on":"1",
      "payload_off":"0"}},
  }

devices = json.loads(subprocess.check_output("wget http://localhost/rest/all -O - -q", shell=True))
devs={}
circuits=[]
for dev in devices:
  if dev["dev"] in devtypes:
    if devtypes[dev["dev"]]["type"] not in devs: devs[devtypes[dev["dev"]]["type"]] = [ dev ]
    else: devs[devtypes[dev["dev"]]["type"]].append(dev)
    circuit=dev["circuit"][0:dev["circuit"].rfind('_')] + "_01"
    if circuit not in circuits: circuits.append(circuit)

print "mqtt:"
print "  broker: localhost"
print "  #password: !secret mqtt"
print "  client_id: HomeAssistant"
print ""
print "shell_command:"
print "  restart_neurontcp: /usr/bin/ssh localhost systemctl restart neurontcp"
print "  restart_evok: /usr/bin/ssh localhost systemctl restart evok"
print "  restart_evok2mqtt: /usr/bin/ssh localhost systemctl restart evok2mqtt"
print ""
print "script:"
print "  evok_restart:"
print "    alias: Restart EVOK services"
print "    sequence:"
print "    - service: shell_command.restart_neurontcp"
print "    - delay: 00:00:02"
print "    - service: shell_command.restart_evok"
print "    - delay: 00:00:02"
print "    - service: shell_command.restart_evok2mqtt"
print ""
print "  evok_read_all:"
print "    alias: Read all EVOK values"
print "    sequence:"
print "    - service: mqtt.publish"
print "      data:"
print "        topic: neuron"
print "        payload: \"{\\\"cmd\\\":\\\"all\\\"}\""
print "  evok_save_config:"
print "    alias: Save config to firmware"
print "    sequence:"
for circuit in circuits:
  print "    - service: mqtt.publish"
  print "      data:"
  print "        topic: neuron/wd/" + circuit
  print '        payload: "{\\"cmd\\":\\"set\\",\\"dev\\":\\"wd\\",\\"circuit\\":\\"' + circuit + '\\",\\"value\\":\\"1\\"}"'
print "#    - service: script.turn_on"
print "#      entity_id: script.evok_read_all"
print ""
print "automation:"
print "- alias: evok_init_on_boot"
print "  initial_state: 'on'"
print "  trigger:"
print "    platform: homeassistant"
print "    event: start"
print "  action:"
print "    service: script.turn_on"
print "    entity_id: script.evok_read_all"
print ""

for devtype in devs:
  print devtype + ":"
  for dev in sorted(devs[devtype]):
    print "  - platform: mqtt"
    print "    name: EVOK_" + dev["dev"].upper() + "_" + dev["circuit"]
    for attr in devtypes[dev["dev"]]["attr"]:
      avals=devtypes[dev["dev"]]["attr"][attr]
      if type(avals) is str:
        print "    " + attr + ": " + avals.replace("%c", dev["circuit"]).replace("%d", dev["dev"])
      elif type(avals) is list:
        print "    " + attr + ":"
        for att in devtypes[dev["dev"]]["attr"][attr]:
          print "    - " + att
  print ""

groups={}
for dev in devices:
  if dev["dev"] in devtypes:
    key1 = dev["dev"].upper()
    key2 = dev["circuit"][:dev["circuit"].rfind("_")]
    key = key1 + " " + key2
    #key3 = dev["circuit"][dev["circuit"].rfind("_")+1:]
    if key in groups: groups[key].append(devtypes[dev["dev"]]["type"] + ".evok_" + dev["dev"].lower() + "_" + dev["circuit"].lower())
    else: groups[key] = [ devtypes[dev["dev"]]["type"] + ".evok_" + dev["dev"].lower() + "_" + dev["circuit"].lower() ]

print "group:"
print "  grp_evok_mgmt:"
print "    name: EVOK Management"
print "    control: hidden"
print "    entities:"
print "    - script.evok_read_all"
print "    - script.evok_restart"
print "    - script.evok_save_config"

for group in sorted(groups):
  print "  grp_evok_" + group.lower().replace(' ', '_') + ":"
  print "    name: EVOK " + group
  print "    entities:"
  for dev in sorted(groups[group]):
    print "    - " + dev

print "  grp_evok:"
print "    name: EVOK"
print "    view: yes"
print "    entities:"
print "    - group.grp_evok_mgmt"
for group in sorted(groups):
  print "    - group.grp_evok_" + group.lower().replace(' ', '_')
