from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os


app = Flask(__name__)

# MongoDB connection
uri = "mongodb+srv://raikanaeru:rai12345@cluster0.oif98.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["sensor_db"]
collection = db["sensor_data"]


try:
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

@app.route('/api/sensor/data', methods=['POST'])
def receive_sensor_data():
    """
    Endpoint to receive sensor data from ESP32 and store it in MongoDB
    Expected JSON format:
    {
        "temperature": 25.5,
        "humidity": 60,
        "gas_mq2": 1200.5,
        "water_level": 35.2
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["temperature", "humidity"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Add timestamp
    data["timestamp"] = datetime.now()
    
    # Optional fields
    if "gas_mq2" in data:
        data["gas_mq2"] = float(data["gas_mq2"])
    
    if "water_level" in data:
        data["water_level"] = float(data["water_level"])
    
    # Insert data into MongoDB
    try:
        result = collection.insert_one(data)
        return jsonify({
            "message": "Data successfully saved to MongoDB",
            "id": str(result.inserted_id),
            "timestamp": data["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save data: {str(e)}"}), 500

@app.route('/api/sensor/data', methods=['GET'])
def get_sensor_data():
    """
    Endpoint to get sensor data with optional filtering
    Query parameters:
    - sensor_type: temperature, humidity, gas_mq2, water_level
    - sort_order: lowest, highest
    - limit: number of records to return
    """
    sensor_type = request.args.get('sensor_type', 'temperature')
    sort_order = request.args.get('sort_order', 'highest')
    limit = int(request.args.get('limit', 10))
    
    sort_direction = 1 if sort_order == "lowest" else -1
    
    try:
        data = list(collection.find(
            {sensor_type: {"$exists": True}},
            {"_id": 0, sensor_type: 1, "timestamp": 1}
        ).sort(sensor_type, sort_direction).limit(limit))
        
        # Convert datetime objects to string for JSON serialization
        for item in data:
            if "timestamp" in item:
                item["timestamp"] = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}"}), 500

@app.route('/api/sensor/average', methods=['GET'])
def get_average_data():
    """
    Endpoint to get average sensor data within a date range
    Query parameters:
    - sensor_type: temperature, humidity, gas_mq2, water_level
    - start_date: DD-MM-YYYY
    - end_date: DD-MM-YYYY
    """
    sensor_type = request.args.get('sensor_type', 'temperature')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400
    
    try:
        start_dt = datetime.strptime(start_date, "%d-%m-%Y")
        end_dt = datetime.strptime(end_date, "%d-%m-%Y")
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_dt, "$lte": end_dt}}},
            {"$group": {"_id": None, "avg_value": {"$avg": f"${sensor_type}"}}}
        ]
        
        result = list(collection.aggregate(pipeline))
        avg_value = result[0]["avg_value"] if result else None
        
        return jsonify({
            "sensor_type": sensor_type,
            "start_date": start_date,
            "end_date": end_date,
            "average": avg_value
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to calculate average: {str(e)}"}), 500

@app.route('/api/sensor/latest', methods=['GET'])
def get_latest_data():
    """
    Endpoint to get the latest sensor reading
    """
    try:
        latest = collection.find_one(
            sort=[("timestamp", -1)]
        )
        
        if latest:
            # Convert ObjectId to string for JSON serialization
            latest["_id"] = str(latest["_id"])
            # Convert datetime to string
            latest["timestamp"] = latest["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            return jsonify(latest), 200
        else:
            return jsonify({"message": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve latest data: {str(e)}"}), 500

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    # Run the app with debug mode enabled
    app.run(host='0.0.0.0', port=port, debug=True)
