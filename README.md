# MicroPython-Nextion-MQTT
a robust library for controlling Nextion displays using MQTT and ESP32.

Driving Nextion displays can be cumbersome task, this library helps controling the Nextion displays over the WIFI using MQTT protocol by converting json payloads into Nextion commands.

example, an MQTT payload would be an array of command objects:

    [
      {
        "f": "hour",
        "p": "txt",
        "v": "12",
        "t": "str"
	    },{
        "f": "minute",
        "p": "txt",
        "v": "10",
        "t": "str"
      }
    ]

this will be translated into two Nextion commands

    cmd1: "hour.txt=\"12\""
    cmd2: "minute.txt=\"10\""
also cmd termination will be added for each command (Nextion displays expect 3 bytes after each command [0XFF]*3)

Configurations
-------------
the file config.json contains all the needed configurations to match your needs

    {
      "network": {
        "ip": "172.27.227.104",                   #IP address to assign to chip
        "mask": "255.255.255.0",                  #subnet mask
        "gateway": "172.27.227.1",                #gateway (your router)
        "dns": "172.27.227.150"                   #dns server (usually, your router)
      },
      "mqtt": {
        "id": "ESP32_Client_Nextion",             #ID for the mqtt clientbroker.publish(cnf["mqtt"]["input"]["topic"], cmd)
        "ssl": false,                             #SSL
        "keepalive": 0,                           #TCP connection keep alive
        "host": "172.27.227.150",                 #broker IPbroker.publish(cnf["mqtt"]["input"]["topic"], cmd)
        "user": "",                               #client username
        "pass": "",                               #client password
        "port": 1883,                             #broker port
        "topics": [                               #topics that the client should subscribe to
          "/mqtt/nextion"                         #multiple values are accepted
        ],
        "isAlive": {                              #the topic and payload to send isAlive messages
          "topic": "/mqtt/nextion/isalive",
          "payload": "heartbeat"
        },
        "start": {                                #the topic and payload to send when the client starts
          "topic": "/mqtt/nextion/start",
          "payload": "started"
        },
        "input": {                                #the topic to send Nextion input to
          "topic": "/mqtt/nextion/out"
        }
      },
      "wifi": {                                   #wifi configs
        "ssid": "xxxxxxxxxx",
        "pass": "xxxxxxxxxx"
      },
      "uart": {                                   #UART configurations between the MCU and Nextion display
        "tx": 17,
        "rx": 16,
        "br": 9600
      }
    }

Nextion Functions
-------------
the file nextion.py contains all the APIs needed to communicate with Nextion displays

### nextion.connect
initializes the UART connection, it take a json object containing the needed configs

    cnf = ""
    def loadConfigs():
        global cnf
        f = open('config.json')
        cnf = json.loads(f.read())
        f.close()
    loadConfigs()
    nextion.connect(cnf)

### nextion.transmit
send a Nextion command from json object containing the following attributes:

    f: Nextion field name
    p: the property to change
    v: new value for the property
    t: type of the command (valid values "txt" for String values, 
                                         "int" for Integers,
                                         "cmd" for Nextion commands)
                                         
To send String values:

    cmds = [
      {
        "f": "hour",
        "p": "txt",
        "v": "12",
        "t": "str"
	    },{
        "f": "minute",
        "p": "txt",
        "v": "10",
        "t": "str"
      }
    ]
    for cmd in cmds:
      nextion.transmit(cmd)
      
To send Integer values:

    #Change the background color of page0
    cmd = {
        "f": "page0",
        "p": "bco",
        "v": "1001",
        "t": "int"
	    }
    nextion.transmit(cmd)

to send Nextion native command

    #set the brightness to %50
    cmd = {
        "c": "dims=50",
        "t": "cmd"
	    }
    nextion.transmit(cmd)

### nextion.getCommand
none blocking method to read the input from the Nextion display, it returns 8 bytes which then encoded into string

    cmd=nextion.getCommand()
    if(cmd):
      if("1affffff" not in cmd):      #ignore invalid input error
        broker.publish(cnf["mqtt"]["input"]["topic"], cmd)
        
### nextion.writeraw
a method to send raw data to the nextion display

### nextion.dims
a method to control the brightness of the Nextion display, valid value is 0-100

### Complete Example
    import nextion
    import json

    f = open('config.json')
    cnf = json.loads(f.read())
    f.close()
    cmd={'v': '1001', 'p': 'bco', 't': 'int', 'f': 'page1'}

    nextion.connect(cnf)
    nextion.transmit(cmd)
