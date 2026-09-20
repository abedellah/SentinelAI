# models/alert.py
from bson import ObjectId
from datetime import datetime
from config.config import get_mongo_db

class Alert:
    @classmethod
    def get_collection(cls):
        return get_mongo_db().alerts
    
    @staticmethod
    def create(data):
        alert_doc = {
            'log_id': ObjectId(data.get('log_id')),
            'timestamp': data.get('timestamp', datetime.utcnow()),
            'alert_type': data.get('alert_type', 'unknown'),
            'description': data.get('description', ''),
            'score_risk': data.get('score_risk', 0.0),
            'status': data.get('status', 'open'),
            'analyst_notes': data.get('analyst_notes', ''),
            'user_id': int(data.get('user_id')) if data.get('user_id') else None  # SQL user ID
        }
        collection = Alert.get_collection()
        result = collection.insert_one(alert_doc)
        return result.inserted_id
    
    @staticmethod
    def find_all(limit=100, skip=0):
        collection = Alert.get_collection()
        return list(collection.find().sort('timestamp', -1).skip(skip).limit(limit))
    
    @staticmethod
    def find_by_id(alert_id):
        collection = Alert.get_collection()
        return collection.find_one({'_id': ObjectId(alert_id)})
    
    @staticmethod
    def update(alert_id, data):
        collection = Alert.get_collection()
        return collection.update_one(
            {'_id': ObjectId(alert_id)},
            {'$set': data}
        )
    
    @staticmethod
    def delete(alert_id):
        collection = Alert.get_collection()
        return collection.delete_one({'_id': ObjectId(alert_id)})
    
    @staticmethod
    def count():
        collection = Alert.get_collection()
        return collection.count_documents({})
    
    @staticmethod
    def count_by_status(status):
        collection = Alert.get_collection()
        return collection.count_documents({'status': status})
    
    @staticmethod
    def find_high_risk(threshold=7.0):
        collection = Alert.get_collection()
        return list(collection.find({'score_risk': {'$gte': threshold}}).sort('score_risk', -1))
