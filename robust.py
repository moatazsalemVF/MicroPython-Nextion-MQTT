import utime
import simple
import json

cnf = ""
def loadConfigs():
    global cnf
    f = open('config.json')
    cnf = json.loads(f.read())
    f.close()
loadConfigs()


class MQTTClient(simple.MQTTClient):

    DELAY = 2
    DEBUG = False

    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self):
        print("reconnecting to MQTT")
        i = 0
        while 1:
            try:
                d = super().connect(False)
                for topic in cnf["mqtt"]["topics"]:
                    super().subscribe(topic)
                print("Reconnected")
                return d
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)

    def publish(self, topic, msg, retain=False, qos=0):
        while 1:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def wait_msg(self):
        while 1:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()
