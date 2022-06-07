import json
import requests
import paho.mqtt.client as mqtt
import time
import websocket


evokhost = 'http://192.168.0.20:88'
mqtthost = '192.168.0.21'

#devtypes = {'input':'binary_sensor', 'relay':'switch', 'ai':'sensor', 'ao':'number', 'led':'switch'}
devtypes = {'input':'binary_sensor', 'relay':'switch', 'led':'switch'}
configs = {
  'input': { 'payload_on':'1','payload_off':'0','initial_state':'0' },
  'relay': { 'payload_on':'1','payload_off':'0' },
  'ao': {'min':0, 'max':10,'step':.1},
  'led': { 'payload_on':'1','payload_off':'0' },
}

def get_entity(dev, circuit):
  return 'evok2_' + dev + '_' + circuit

def get_topic(dev, circuit, sub=''):
  return 'homeassistant/' + devtypes[dev] + '/neuron-m203/' + circuit + ('/' + sub if sub else '')

def publish_dev_config():
  rest_all = requests.get(evokhost + '/rest/all')
  rest_all_devs = json.loads(rest_all.content.decode('utf-8'))

  for dev in rest_all_devs:
    if (dev['dev'] in devtypes):
      config_topic = get_topic(dev['dev'], dev['circuit'], 'config')
      state_topic = get_topic(dev['dev'], dev['circuit'], 'state')
      command_topic = get_topic(dev['dev'], dev['circuit'], 'set')
      ha_id = 'evok_' + dev['dev'] + '_' + dev['circuit']
      ha_name = 'Evok2 ' + dev['dev'].capitalize() + ' ' + dev['circuit']

      payload = {
        'unique_id': ha_id,
        'name': ha_name,
        'state_topic':state_topic,
        'command_topic':command_topic
      }
      if (dev['dev'] in configs):
        payload = dict(list(payload.items()) + list(configs[dev['dev']].items()))

      mc.publish(config_topic, payload=json.dumps(payload), qos=1, retain=True)
      mc.publish(state_topic, payload=dev['value'], qos=1)

def mc_connect(mc, userdata, flags, rc):
  for devtype in devtypes:
    print('subscribe homeassistant/' + devtype + '/neuron-m203/+/set')
    mc.subscribe('homeassistant/' + devtype + '/neuron-m203/+/set')

def ws_msg(ws, msg):
    objs = json.loads(msg)
    for obj in objs:
      if obj['dev'] in devtypes:
        topic = get_topic(obj['dev'], obj['circuit'], 'state')
        mc.publish(topic, payload=obj['value'], qos=1)

def mc_msg(mc, userdata, message):
  topics = message.topic.split('/')
  print(topics)
  if len(topics) >= 4:
    if topics[2] == 'neuron-m203' and topics[4] == 'set':
      dev = list(devtypes.keys())[list(devtypes.values()).index(topics[1])]
      print(message.payload)
      payload = {
            'cmd': 'set',
            'dev':dev,
            'circuit':topics[3],
            'value':int(message.payload),
            }
      ws.send(json.dumps(payload))




mc = mqtt.Client(client_id="evok2", clean_session=False)
mc.on_connect = mc_connect
mc.on_message = mc_msg
mc.connect(mqtthost)
mc.loop_start()

publish_dev_config()

ws = websocket.WebSocketApp('ws://192.168.0.20:8080/ws',
        on_message = ws_msg
        )
ws.run_forever()

mc.loop_stop()
mc.disconnect
