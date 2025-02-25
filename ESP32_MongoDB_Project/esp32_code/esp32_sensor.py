import network
import time
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C, ADC, PWM
import dht
import ssd1306
from pymongo import MongoClient
from datetime import datetime

UBIDOTS_TOKEN = "BBUS-5d877a76foJ5qKNRCoaLnXQEe5YRIi"
WIFI_SSID = "hsc388"
WIFI_PASS = "Rai12345*"
DEVICE_LABEL = "esp32-dashboard"
VARIABLE_TEMP = "temperature"
VARIABLE_HUM = "humidity"
VARIABLE_GAS = "gas_mq2"
VARIABLE_WATER = "water_level"

MQTT_BROKER = "industrial.api.ubidots.com"
MQTT_TOPIC = f"/v1.6/devices/{DEVICE_LABEL}"

MONGO_URI = "mongodb+srv://raikanaeru:rai12345@cluster0.oif98.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "sensor_db"
MONGO_COLLECTION_NAME = "sensor_data"

dht_sensor = dht.DHT11(Pin(4))

mq2_pin = ADC(Pin(34))
mq2_pin.atten(ADC.ATTN_11DB)

water_sensor = ADC(Pin(35))
water_sensor.atten(ADC.ATTN_11DB)

led_hijau = Pin(26, Pin.OUT)
led_kuning = Pin(27, Pin.OUT)
led_merah = Pin(14, Pin.OUT)
buzzer = PWM(Pin(25))
buzzer.freq(1000)

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Fungsi koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    print("🔗 Menghubungkan ke WiFi...", end="")
    for _ in range(10):
        if wlan.isconnected():
            print("\n✅ Terhubung ke WiFi! IP:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
        print(".", end="")

    print("\n❌ Gagal konek WiFi! Mode lokal aktif.")
    return False

# Fungsi koneksi ke MongoDB
def connect_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        print("✅ Koneksi MongoDB sukses!")
        return collection
    except Exception as e:
        print("❌ Gagal konek MongoDB:", e)
        return None

# Fungsi untuk mengirim data ke Ubidots
def send_data(temp, hum, gas_ppm, water_level):
    client = MQTTClient("esp32", MQTT_BROKER, user=UBIDOTS_TOKEN, password="")
    try:
        print("📡 Menghubungkan ke Ubidots MQTT...")
        client.connect()
        payload = ujson.dumps({
            VARIABLE_TEMP: {"value": temp},
            VARIABLE_HUM: {"value": hum},
            VARIABLE_GAS: {"value": gas_ppm},
            VARIABLE_WATER: {"value": water_level}
        })
        print("📤 Mengirim data:", payload)
        client.publish(MQTT_TOPIC, payload)
        print("✅ Data berhasil dikirim ke Ubidots!")
        client.disconnect()
        return True
    except Exception as e:
        print("❌ Gagal kirim data MQTT!", e)
        return False

# Fungsi untuk menyimpan data ke MongoDB
def send_to_mongodb(temp, hum, gas_ppm, water_level):
    if mongo_collection:
        try:
            data = {
                "temperature": temp,
                "humidity": hum,
                "gas_mq2": gas_ppm,
                "water_level": water_level,
                "timestamp": datetime.utcnow()
            }
            mongo_collection.insert_one(data)
            print("✅ Data berhasil disimpan ke MongoDB!")
        except Exception as e:
            print("❌ Gagal menyimpan data ke MongoDB:", e)
    else:
        print("⚠️ Tidak terhubung ke MongoDB, data tidak tersimpan.")

# Fungsi untuk menampilkan data di OLED
def display_oled(temp, hum, gas_ppm, water_level, status):
    oled.fill(0)
    oled.text("ESP32SensorData", 10, 0)
    oled.text(f"TEMP: {temp} C", 10, 13)
    oled.text(f"HUM : {hum} %", 10, 25)
    oled.text(f"GAS : {gas_ppm:.2f} ppm", 10, 37)
    oled.text(f"WATER: {water_level}", 10, 49)
    oled.text("Sent: " + ("Yes" if status else "No"), 10, 57)
    oled.show()

# Koneksi ke WiFi dan MongoDB
wifi_connected = connect_wifi()
mongo_collection = connect_mongodb()

# Loop utama
while True:
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembapan = dht_sensor.humidity()
        
        nilai_gas = mq2_pin.read()
        Vout = (nilai_gas / 4095) * 3.3
        gas_ppm = 100 * (Vout / 3.3) ** -1.5
        
        nilai_air = water_sensor.read()
        water_level = (nilai_air / 4095) * 100
        
        print(f"🌡️ Suhu: {suhu} C, 💧 Kelembapan: {kelembapan} %, 🔥 Gas: {nilai_gas} ADC, {gas_ppm:.2f} ppm, 💦 Air: {water_level:.2f} %")
        
        led_hijau.value(0)
        led_kuning.value(0)
        led_merah.value(0)
        buzzer.duty(0)

        if gas_ppm < 40000 and water_level < 50:
            led_hijau.value(1)
        elif 4000 <= gas_ppm < 70000 or 50 <= water_level < 80:
            led_kuning.value(1)
        else:
            led_merah.value(1)
            buzzer.duty(712)

        status = send_data(suhu, kelembapan, gas_ppm, water_level) if wifi_connected else False
        send_to_mongodb(suhu, kelembapan, gas_ppm, water_level)
        display_oled(suhu, kelembapan, gas_ppm, water_level, status)

    except Exception as e:
        print("❌ Error di loop utama!", e)
    
    time.sleep(5)
