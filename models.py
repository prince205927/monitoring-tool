# models.py

from pymongo import MongoClient
import config

# For PostgreSQL (if needed in future, commented out here)
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# Uncomment and configure PostgreSQL client if needed in future
# class PostgreSQLClient:
#     def __init__(self):
#         self.engine = db.get_engine()
#
#     def store_data(self, data):
#         with self.engine.connect() as conn:
#             conn.execute(
#                 'INSERT INTO system_info (cpu, memory, storage, network, timestamp) VALUES (%s, %s, %s, %s, %s)',
#                 (data['cpu'], data['memory'], data['storage'], data['network'], data['timestamp'])
#             )

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(config.Config.MONGO_URI)
        self.db = self.client.monitoring

    def store_data(self, data):
        self.db.system_info.insert_one(data)

    def fetch_data(self):
        return list(self.db.system_info.find())
