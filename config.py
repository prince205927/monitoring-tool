import os
# config.py

class Config:
    # Other settings...
    MONGO_URI = 'mongodb://localhost:27017/monitoring'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/monitoring')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/monitoring')
    SCHEDULER_INTERVAL = 5  # Default interval in minutes
