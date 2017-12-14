import serial
import serial.tools.list_ports as serial_ports

class ArduinoConnection(object):

  def __init__(self):
    self.port = None
    self.arduino = None
    self.get_port()
    self.initiate_connection()

  def get_port(self):
    ports = list(serial_ports.comports())
    for port in ports:
      if 'Arduino' in port[1]:
        self.port = port[0]
  
  def initiate_connection(self):
    if self.port == None:
      print('[-] Could not find the Arduino port');
      return
    else:
      self.arduino = serial.Serial(self.port, 38400, timeout=0.1)
  
  def send_data(self):
    if self.arduino == None:
      print('[-] Could not receive any data from Arduino')
      return
    while True:
      data = self.arduino.readline()[:-2]
      if data:
        print(data)


if __name__ == '__main__':
  conn = ArduinoConnection()
  conn.send_data()
      
