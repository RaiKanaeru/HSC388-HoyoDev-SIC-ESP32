README-mu sudah cukup jelas dan terstruktur. Berikut adalah perbaikannya agar lebih rapi dan mudah dipahami:  

---

# **Proyek ESP32 dengan MongoDB**

## 📌 **Deskripsi**
Proyek ini menghubungkan **ESP32** dengan sensor **DHT11**, **MQ-2**, dan **sensor air** untuk mengukur **suhu, kelembapan, kadar gas, dan level air**.  
Data dari ESP32 dikirim ke **Ubidots (melalui MQTT)** dan juga disimpan ke **MongoDB (melalui server Flask)** untuk analisis lebih lanjut.

---

## 🛠 **Struktur Proyek**
```
📂 ESP32_MongoDB_Project
├── 📂 esp32_code
│   ├── esp32_sensor.py   # Script ESP32 untuk membaca sensor dan mengirim data
│   └── requirements.txt   # Library yang dibutuhkan di Thonny IDE
├── 📂 server_code
│   ├── server.py         # Server Flask untuk menerima dan menyimpan data
│   └── requirements.txt  # Library yang dibutuhkan di VS Code
└── README.md             # Dokumentasi proyek
```

---

## 🏗 **Instalasi dan Konfigurasi**

### **1️⃣ Menjalankan ESP32 (Thonny IDE)**
1. Install **Thonny IDE** dan pastikan **ESP32 terhubung ke komputer**.
2. Instal library yang dibutuhkan dengan perintah:
   ```sh
   pip install -r requirements.txt
   ```
3. Ubah **WIFI_SSID** dan **WIFI_PASS** di `esp32_sensor.py` agar sesuai dengan jaringan WiFi yang digunakan.
4. Upload `esp32_sensor.py` ke ESP32 dan jalankan.

### **2️⃣ Menjalankan Server Flask (VS Code)**
1. Install **Python** dan pastikan **pip** sudah terpasang.
2. Instal library yang dibutuhkan dengan perintah:
   ```sh
   pip install -r requirements.txt
   ```
3. Pastikan **MongoDB berjalan** dan siap menerima data.
4. Jalankan server Flask dengan perintah:
   ```sh
   python server.py
   ```

---

## 🚀 **Cara Kerja**
1. **ESP32 membaca data sensor** dari:
   - **DHT11** → Suhu & Kelembapan  
   - **MQ-2** → Kadar gas  
   - **Sensor Air** → Level air  
2. **ESP32 mengirimkan data ke Ubidots** melalui **MQTT**.  
3. **ESP32 juga mengirim data ke server Flask** melalui **HTTP POST**.  
4. **Server Flask menyimpan data ke MongoDB** untuk analisis lebih lanjut.  
5. **Data dapat diakses melalui API Flask**.

---

## 🔗 **API Endpoint**
| **Metode** | **Endpoint** | **Deskripsi** |
|------------|-------------|--------------|
| `POST` | `/api/sensor` | Menyimpan data sensor ke MongoDB |
| `GET` | `/api/sensor` | Mengambil semua data sensor |
| `GET` | `/api/sensor/average` | Mengambil rata-rata data sensor dalam rentang waktu tertentu |

---

## 📢 **Catatan**
- Pastikan koneksi internet **stabil** agar ESP32 dapat mengirimkan data dengan lancar.
- Pastikan **MongoDB sudah berjalan** sebelum menjalankan server Flask.
- Jika terjadi masalah, periksa:
  - **Koneksi WiFi** untuk ESP32.
  - **Output serial di Thonny IDE** untuk melihat error.
  - **Server Flask** apakah berjalan dengan benar di terminal VS Code.

---

## ✨ **Kontributor**
👤 **Raihan Ariansyah**  

> 🚀 Proyek ini dibuat untuk mengintegrasikan ESP32 dengan penyimpanan data menggunakan MongoDB dan Ubidots!  

---

Perubahan utama yang saya lakukan:
✅ **Menata struktur agar lebih rapi**  
✅ **Menambahkan beberapa penjelasan supaya lebih jelas**  
✅ **Menggunakan ikon emoji agar lebih menarik**  

Kalau ada tambahan atau perubahan lain, beri tahu saya! 🔥
