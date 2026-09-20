# models/log.py
from bson import ObjectId
from datetime import datetime
from config.config import get_mongo_db

class Log:
    @classmethod
    def get_collection(cls):
        return get_mongo_db().logs
    
    @staticmethod
    def create(data):
        log_doc = {
            'timestamp': data.get('timestamp', datetime.utcnow()),
            'source_ip': data.get('source_ip', ''),
            'destination_ip': data.get('destination_ip', ''),
            'source_port': data.get('source_port', 0),
            'destination_port': data.get('destination_port', 0),
            'protocol': data.get('protocol', ''),
            'event_type': data.get('event_type', ''),
            'status': data.get('status', 'pending'),
            'flow_duration': data.get('flow_duration', 0),
            'flow_bytes_per_second': data.get('flow_bytes_per_second', 0.0),
            'flow_packets_per_second': data.get('flow_packets_per_second', 0.0),
            'Label': data.get('Label', 'BENIGN'),
            'notes': data.get('notes', ''),
            'attack_details': {
                'attack_name': data.get('attack_name', ''),
                'description': data.get('description', ''),
                'severity_level': data.get('severity_level', 'low')
            }
        }
        collection = Log.get_collection()
        result = collection.insert_one(log_doc)
        return result.inserted_id
    
    @staticmethod
    def find_all(limit=100, skip=0):
        collection = Log.get_collection()
        return list(collection.find().sort('timestamp', -1).skip(skip).limit(limit))
    
    @staticmethod
    def find_by_id(log_id):
        collection = Log.get_collection()
        return collection.find_one({'_id': ObjectId(log_id)})
    
    @staticmethod
    def update(log_id, data):
        collection = Log.get_collection()
        return collection.update_one(
            {'_id': ObjectId(log_id)},
            {'$set': data}
        )
    
    @staticmethod
    def delete(log_id):
        collection = Log.get_collection()
        return collection.delete_one({'_id': ObjectId(log_id)})
    
    @staticmethod
    def count():
        collection = Log.get_collection()
        return collection.count_documents({})
    
    @staticmethod
    def find_by_label(label):
        collection = Log.get_collection()
        return list(collection.find({'Label': label}))