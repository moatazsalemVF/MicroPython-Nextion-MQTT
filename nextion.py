import machine
import ubinascii

uart = ""

def connect(cnf):
  global uart
  uart = machine.UART(2, tx=cnf["uart"]["tx"], rx=cnf["uart"]["rx"])
  uart.init(cnf["uart"]["br"], bits=8, parity=None, stop=1)
  
def transmit(single):
  global uart
  c = None
  if single["t"] == "str":
    c = str(single["f"]+"."+single["p"]+"=\""+single["v"]+"\"").encode()+bytearray([255]*3)
  elif single["t"] == "int":
    c = str(single["f"]+"."+single["p"]+"="+str(single["v"])).encode()+bytearray([255]*3)
  elif single["t"] == "cmd":
    c = str(single["c"]).encode()+bytearray([255]*3)
  writeraw(c)

def getCommand():
  cmd=uart.readline()
  if(cmd):
    cmd = ubinascii.hexlify(cmd).decode()
    return cmd
  return None

def writeraw(cmd):
  uart.write(cmd)

def dims(val):
  cmd = {}
  cmd["t"] = "cmd"
  cmd["c"] = "dims="+str(val)
  transmit(cmd)
