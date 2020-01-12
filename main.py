import machine
import network
import json
from time import sleep
from robust import MQTTClient
from utime import ticks_ms
import gc
import nextion

machine.freq(240000000)

cnf = ""
def loadConfigs():
    global cnf
    f = open('config.json')
    cnf = json.loads(f.read())
    f.close()
loadConfigs()


sta_if = network.WLAN(network.STA_IF)
broker = MQTTClient(cnf["mqtt"]["id"], cnf["mqtt"]["host"], port=cnf["mqtt"]["port"], user=cnf["mqtt"]["user"], password=cnf["mqtt"]["pass"], keepalive=cnf["mqtt"]["keepalive"], ssl=cnf["mqtt"]["ssl"])
now = ticks_ms()
start = ticks_ms()
heartbeat = ticks_ms()

nextion.connect(cnf)

nextion.dims(100)

def connectToWifi():
    global sta_if
    global cnf
    sta_if.active(True)
    print(" Connecting to WIFI ")
    sta_if.ifconfig((cnf["network"]["ip"], cnf["network"]["mask"], cnf["network"]["gateway"], cnf["network"]["dns"]))
    sta_if.connect(cnf["wifi"]["ssid"], cnf["wifi"]["pass"])
    while(not sta_if.isconnected()):
        sleep(0.5)
    print("  IP:"+sta_if.ifconfig()[0]+"  ")
connectToWifi()

def handleMQTT(topic, msg, connection):
  msg = msg.decode("utf-8")
  msgjson = json.loads(msg)

  for single in msgjson:
    nextion.transmit(single)

def setupMQTTConnection():
    print("connecting to mqtt")
    global broker
    broker.set_callback(handleMQTT)
    broker.connect()
    for topic in cnf["mqtt"]["topics"]:
        broker.subscribe(topic)
    print("connected to MQTT Broker")
    broker.publish(cnf["mqtt"]["start"]["topic"], cnf["mqtt"]["start"]["payload"])
setupMQTTConnection()

colorFlag = True

while True:
  cmd=nextion.getCommand()
  if(cmd):
    if("1affffff" not in cmd):
      broker.publish(cnf["mqtt"]["input"]["topic"], cmd)
  broker.check_msg()
  sleep(0.01)
  now = ticks_ms()
  if(now-start)>500:
    start = now
    colorFlag = not colorFlag
    if colorFlag:
      nextion.writeraw("r0.bco=va1.val".encode()+bytearray([255]*3))
      nextion.writeraw("r1.bco=va1.val".encode()+bytearray([255]*3))
    else:
      nextion.writeraw("r0.bco=va0.val".encode()+bytearray([255]*3))
      nextion.writeraw("r1.bco=va0.val".encode()+bytearray([255]*3))
  if(now-heartbeat)>1000:
    heartbeat = now
    broker.publish(cnf["mqtt"]["isAlive"]["topic"], cnf["mqtt"]["isAlive"]["payload"])
    gc.collect()
