from machine import I2C, Pin, Timer
import time

# Settings
SAMPLE_PERIOD_MINUTES = 5
HUMIDITY_THRESHOLD = 70.0
ON_DURATION = 5  # When threshold is exceeded, turn the dehumidifier on for at least this long before rechecking

# Probably don't change this stuff
I2C_SCL_PIN = 12
I2C_SDA_PIN = 13
DHT_GND_PIN = 14
DHT_VCC_PIN = 16
DHT22_I2C_ADDRESS = 0x38
RELAY_1_PIN = 4
RELAY_2_PIN = 5
STATUS_LED_PIN = 2

# Set the GPIO pins to supply the sensor with power
Pin(DHT_VCC_PIN, Pin.OUT).on()
Pin(DHT_GND_PIN, Pin.OUT).off()

relay_1 = Pin(RELAY_1_PIN, Pin.OUT)
relay_2 = Pin(RELAY_2_PIN, Pin.OUT)
status_led = Pin(STATUS_LED_PIN, Pin.OUT)
status_led.on()  # On is actually off


def read_dht(i2c):
    i2c.writeto(DHT22_I2C_ADDRESS, b"\xac\x33\x00")
    time.sleep(0.1)
    data = i2c.readfrom(DHT22_I2C_ADDRESS, 7)
    tRaw = ((data[3] & 0xF) << 16) + (data[4] << 8) + data[5]
    temperature = 200 * float(tRaw) / 2**20 - 50
    hRaw = ((data[3] & 0xF0) >> 4) + (data[1] << 12) + (data[2] << 4)
    humidity = 100 * float(hRaw) / 2**20
    return (temperature, humidity)


def log_data(t):
    status_led.off()  # Off is actually on

    # Read the data from the sensor
    i2c = I2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=100_000)
    try:
        (temperature, humidity) = read_dht(i2c)
    except:
        print("Error taking measurement")
        return

    # Display on serial / REPL
    print(f"Temperature: {temperature:.1f} °C\t\tHumidity: {humidity:.1f}%")

    # Write to data file
    try:
        with open("data.txt", "a") as outfile:
            outfile.write(f"{temperature:.1f},{humidity:.1f}\n")
    except OSError as e:
        print(f"Error recording data: {e}")

    status_led.on()  # On is actually off

    if humidity > HUMIDITY_THRESHOLD:
        print(f"Current humidity ({humidity}) exceeds threshold ({HUMIDITY_THRESHOLD})")
        print(f"Turning on relay for {ON_DURATION} minutes")
        relay_1.on()
        time.sleep(int(ON_DURATION * 60 * 1000))
    else:
        relay_1.off()


def display_datalog():
    try:
        with open("data.txt", "r") as datafile:
            print("----- DATA LOGGED SO FAR -----")
            print()
            print("temperature,humidity")
            print(datafile.read())
    except OSError as e:
        print(f"{e}: Starting fresh data log...")
    print("\n-----   NEW DATA BELOW   -----\n")


tim = Timer(-1)
tim.init(
    period=int(SAMPLE_PERIOD_MINUTES * 60 * 1000),
    mode=Timer.PERIODIC,
    callback=log_data,
)
display_datalog()
