from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

MONGO_URI = "mongodb+srv://raikanaeru:rai12345@cluster0.oif98.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["sensor_db"]
collection = db["sensor_data"]

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        data["timestamp"] = datetime.utcnow()

        collection.insert_one(data)
        print("✅ Data disimpan ke MongoDB:", data)
        return jsonify({"status": "success", "message": "Data saved to MongoDB"}), 200
    except Exception as e:
        print("❌ Error menyimpan data!", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
