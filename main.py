from machine import I2C
from machine import Pin
import time

def read_dht(i2c, address):
  i2c.writeto(address, b'\xac\x33\x00')
  time.sleep(0.08)
  data = i2c.readfrom(address, 7)
  tRaw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
  temperature = 200*float(tRaw)/2**20 - 50
  hRaw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
  humidity = 100*float(hRaw)/2**20
  return (temperature, humidity)

def main():
  i2c = I2C(scl=Pin(13), sda=Pin(2), freq=100000)

  print("----- DATA LOGGED SO FAR -----")
  print()
  print("temperature,humidity")
  with open('data.txt', 'r') as datafile:
    print(datafile.read())

  while(True):
    (temperature, humidity) = read_dht(i2c, 0x38)
    with open('data.txt', 'wa') as outfile:
      outfile.write(f"{temperature},{humidity}\r\n")

    time.sleep(60*5.0)  # Sleep 5 minutes

main()