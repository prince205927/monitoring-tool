# data_collector.py

from models import MongoDBClient
import datetime

def collect_data(ip, username, password, port):
    # Collect system data (this example uses dummy data)
    data = {
        'cpu': 'Intel i7',
        'memory': '16GB',
        'storage': '512GB SSD',
        'network': 'eth0',
        'timestamp': datetime.datetime.now()
    }

    # Store data in MongoDB
    mongo_client = MongoDBClient()
    mongo_client.store_data(data)
