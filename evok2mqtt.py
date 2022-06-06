import json
import requests
import paho.mqtt.client as mqtt
import time


evokhost = 'http://192.168.0.20:88'
mqtthost = '192.168.0.21'

devtypes = {'input':'binary_sensor', 'relay':'switch', 'ai':'sensor', 'ao':'number', 'led':'switch'}
#devtypes = {'input':'binary_sensor'}
configs = {
  'input': { 'payload_on':'1','payload_off':'0','initial_state':'0' },
  'relay': { 'payload_on':'1','payload_off':'0' },
  'ao': {'min':0, 'max':10,'step':.1},
  'led': { 'payload_on':'1','payload_off':'0' },
}

def publish_dev_config():
  rest_all = requests.get(evokhost + '/rest/all')
  rest_all_devs = json.loads(rest_all.content.decode('utf-8'))

  mc = mqtt.Client(client_id="evok2", clean_session=False)
  mc.connect(mqtthost)
  mc.loop_start()

  for dev in rest_all_devs:
    if (dev['dev'] in devtypes):
      entity_id='evok2_' + dev['dev'] + '_' + dev['circuit']
      topic='homeassistant/' + devtypes[dev['dev']] + '/neuron-m203/' + entity_id

      payload = {
        'unique_id':entity_id,
        'name':entity_id,
        'state_topic':topic + '/state',
        'command_topic':topic + '/set',
      }
      if (dev['dev'] in configs):
        payload = dict(list(payload.items()) + list(configs[dev['dev']].items()))

      mc_result = mc.publish(topic + '/config', payload=json.dumps(payload), qos=1, retain=True)
      mc.publish(topic + '/state', payload=dev['value'], retain=False)

  mc.loop_stop()
  mc.disconnect




publish_dev_config()




# Configuration topic: homeassistant/switch/irrigation/config
# State topic: homeassistant/switch/irrigation/state
# Command topic: homeassistant/switch/irrigation/set
# Payload: {"name": "garden", "command_topic": "homeassistant/switch/irrigation/set", "state_topic": "homeassistant/switch/irrigation/state"}


#    payload = {
#      'unique_id':entity_id,
#      'valuetemplate':'{{value_json.value}}',
#      'state_topic':'homeassistant/sensor/' + entity_id + '/state'
#
#        'webdata_now_p':{'name':'Solis Current Power (W)', 'device_class':'power', 'state_class':'measurement', 'unit_of_measurement':'W', 'icon':'mdi:solar-power'},
#        'webdata_today_e':{'name':'Solis Yield Today (kWh)', 'device_class':'energy', 'state_class':'total_increasing', 'unit_of_measurement':'kWh', 'icon':'mdi:solar-power'},
#        'webdata_total_e':{'name':'Solis Total Yield (kWh)', 'device_class':'energy', 'state_class':'total_increasing', 'unit_of_measurement':'kWh', 'icon':'mdi:solar-power'},
#        'webdata_alarm':{'name':'Solis Alarms', 'icon':'mdi:solar-power'},
#
#  - platform: mqtt
#    name: EVOK_RELAY_1_04
#    state_topic: neuron/relay/1_04
#    payload_on: 1
#    command_topic: neuron/relay/1_04
#    payload_off: 0
#    value_template: '{{value_json.value}}'
#
#}
