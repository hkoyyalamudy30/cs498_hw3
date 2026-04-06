import os
from flask import Flask, request, jsonify
from pymongo import MongoClient, WriteConcern, ReadPreference

app = Flask(__name__)

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://hk57:asdf1234@hw3.qi25nym.mongodb.net/?retryWrites=true&w=majority&appName=hw3"
)

DB_NAME = "ev_db"
COLLECTION_NAME = "vehicles"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.route("/")
def home():
    return jsonify({"message": "hw3 api running"})

@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid or missing json payload"}), 400

        fast_collection = collection.with_options(
            write_concern=WriteConcern(w=1)
        )

        result = fast_collection.insert_one(data)
        return jsonify({"inserted_id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid or missing json payload"}), 400

        safe_collection = collection.with_options(
            write_concern=WriteConcern(w="majority")
        )

        result = safe_collection.insert_one(data)
        return jsonify({"inserted_id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    try:
        primary_collection = collection.with_options(
            read_preference=ReadPreference.PRIMARY
        )

        count = primary_collection.count_documents({
            "Make": {"$regex": "^TESLA$", "$options": "i"}
        })

        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():
    try:
        secondary_collection = collection.with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )

        count = secondary_collection.count_documents({
            "Make": {"$regex": "^BMW$", "$options": "i"}
        })

        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
