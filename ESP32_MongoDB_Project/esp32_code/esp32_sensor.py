import network
import time
import ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C, ADC, PWM
import dht
import ssd1306
import urequests  # Tambahan untuk HTTP request ke Flask

# Konfigurasi
UBIDOTS_TOKEN = "BBUS-5d877a76foJ5qKNRCoaLnXQEe5YRIi"
WIFI_SSID = "hsc388"
WIFI_PASS = "Rai12345*"
DEVICE_LABEL = "esp32-dashboard"

FLASK_SERVER_URL = "http://192.168.1.100:5000/api/sensor"

# MQTT Ubidots
MQTT_BROKER = "industrial.api.ubidots.com"
MQTT_TOPIC = f"/v1.6/devices/{DEVICE_LABEL}"
MQTT_CLIENT_ID = "ESP32_Hoyosense"

# Inisialisasi sensor
dht_sensor = dht.DHT11(Pin(4))
mq2_pin = ADC(Pin(34))
mq2_pin.atten(ADC.ATTN_11DB)
water_sensor = ADC(Pin(35))
water_sensor.atten(ADC.ATTN_11DB)

# Output indikator
led_hijau = Pin(26, Pin.OUT)
led_kuning = Pin(27, Pin.OUT)
led_merah = Pin(14, Pin.OUT)
buzzer = PWM(Pin(25))
buzzer.freq(1000)

# OLED Display
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Fungsi koneksi WiFi
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

# Fungsi menghubungkan ke MQTT Ubidots
def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=UBIDOTS_TOKEN, password="", port=1883)
        client.connect()
        print("✅ MQTT Terhubung ke Ubidots!")
        return client
    except Exception as e:
        print("❌ Gagal konek ke MQTT Ubidots!", e)
        return None

# Fungsi mengirim data ke Flask API
def send_data_to_flask(temp, hum, gas_ppm, water_level):
    payload = {
        "temperature": temp,
        "humidity": hum,
        "gas_mq2": gas_ppm,
        "water_level": water_level
    }
    
    try:
        print("📡 Mengirim data ke Flask API...")
        response = urequests.post(FLASK_SERVER_URL, json=payload)
        print("✅ Respon Flask:", response.text)
        response.close()
        return True
    except Exception as e:
        print("❌ Gagal kirim data ke Flask!", e)
        return False

# Fungsi mengirim data ke Ubidots via MQTT
def send_data_to_ubidots(client, temp, hum, gas_ppm, water_level):
    if client is None:
        print("⚠️ MQTT Client tidak tersedia, lewati pengiriman ke Ubidots!")
        return False
    
    payload = ujson.dumps({
        "temperature": {"value": temp},
        "humidity": {"value": hum},
        "gas_mq2": {"value": gas_ppm},
        "water_level": {"value": water_level}
    })

    try:
        print("📡 Mengirim data ke Ubidots...")
        client.publish(MQTT_TOPIC, payload)
        print("✅ Data terkirim ke Ubidots!")
        return True
    except Exception as e:
        print("❌ Gagal kirim data ke Ubidots!", e)
        return False

# Fungsi menampilkan data di OLED
def display_oled(temp, hum, gas, water, status_flask, status_ubidots):
    oled.fill(0)  # Hapus layar
    oled.text("HOYOSENSE IoT", 20, 0)
    oled.text(f"Suhu: {temp} C", 0, 15)
    oled.text(f"Kelembapan: {hum} %", 0, 30)
    oled.text(f"Gas: {gas:.2f} ppm", 0, 45)
    oled.text(f"Air: {water:.2f} %", 0, 55)
    
    if status_flask:
        oled.text("Flask: OK", 80, 15)
    else:
        oled.text("Flask: ERR", 80, 15)

    if status_ubidots:
        oled.text("Ubi: OK", 80, 30)
    else:
        oled.text("Ubi: ERR", 80, 30)

    oled.show()

# Koneksi WiFi & MQTT
wifi_connected = connect_wifi()
mqtt_client = connect_mqtt() if wifi_connected else None

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
        
        # Kontrol LED dan Buzzer berdasarkan kondisi sensor
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

        # Kirim data ke Flask API
        status_flask = send_data_to_flask(suhu, kelembapan, gas_ppm, water_level) if wifi_connected else False

        # Kirim data ke Ubidots
        status_ubidots = send_data_to_ubidots(mqtt_client, suhu, kelembapan, gas_ppm, water_level) if wifi_connected else False

        # Tampilkan di OLED
        display_oled(suhu, kelembapan, gas_ppm, water_level, status_flask, status_ubidots)

    except Exception as e:
        print("❌ Error di loop utama!", e)
    
    time.sleep(5)

