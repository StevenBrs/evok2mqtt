import json
import websocket
import paho.mqtt.client as mqtt

#try:
#  import thread
#except ImportError:
#  import _thread as thread
#import time

def ws_on_message(ws, message):
  payloads = json.loads(message)
  for payload in payloads:
    if payload['dev'] not in ['wd', 'ai']:
      print "WS IN  : ", payload
      topic = "neuron/" + payload["dev"] + "/" + payload["circuit"]
      print "MC OUT : ", topic, json.dumps(payload)
      mc.publish(topic, payload=json.dumps(payload), retain=False)

def mc_on_message(mc, userdata, message):
  print "MC IN  : ", message.topic, message.payload 
  topic = message.topic.split('/')
  try:
    cmd = json.loads(message.payload)["cmd"]
  except:
    cmd = "set"
  try:
    payload = json.loads(message.payload)["value"]
  except:
    payload = message.payload
  if len(topic) == 1:
    wsmsg = {"cmd":cmd}
  elif len(topic) == 3:
    wsmsg = {"cmd":cmd,
        "dev":topic[1],
        "circuit":topic[2],
        "value": payload
      }
  print "WS OUT : ", json.dumps(wsmsg)
  ws.send(json.dumps(wsmsg))

def ws_on_error(ws, error):
  print(error)

def ws_on_close(ws):
  print("### websocket to evok closed ###")

def mc_on_connect(mc, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  mc.subscribe("neuron/#")
  

def ws_on_open(ws):
  def run(*args):
    for i in range(3):
      time.sleep(1)
      print("Hello %d" % i)
      ws.send("Hello %d" % i)
    time.sleep(1)
    ws.close()
    print("thread terminating...")
  thread.start_new_thread(run, ())


if __name__ == "__main__":

  websocket.enableTrace(False)
  ws = websocket.WebSocketApp("ws://127.0.0.1/ws",
                on_message = ws_on_message,
                on_error = ws_on_error,
                #ws.on_open = ws_on_open
                )

  mc = mqtt.Client(client_id="evok2mqtt", clean_session=False)
  mc.on_connect = mc_on_connect
  mc.on_message = mc_on_message
  mc.connect("127.0.0.1", 1883, 60)

  try:
    mc.loop_start()
    ws.run_forever()
  except KeyboardInterrupt:
    print "Ctrl-C"

