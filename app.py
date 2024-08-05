# app.py

from flask import Flask, render_template, request, redirect, url_for
from data_collector import collect_data
from models import MongoDBClient

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def index():
    mongo_client = MongoDBClient()
    data = mongo_client.fetch_data()
    return render_template('index.html', data=data)

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        ip = request.form['ip']
        username = request.form['username']
        password = request.form['password']
        port = request.form['port']
        interval = int(request.form['interval'])  # In minutes

        # Store configuration details
        # Implement your scheduling logic here to call `collect_data` periodically
        return redirect(url_for('index'))

    return render_template('configure.html')

@app.route('/visualizations')
def visualizations():
    # Fetch data for visualizations
    mongo_client = MongoDBClient()
    data = mongo_client.fetch_data()
    return render_template('visualizations.html', data=data)

@app.route('/predictions')
def predictions():
    # Fetch data for predictions and display results
    mongo_client = MongoDBClient()
    data = mongo_client.fetch_data()
    # Use machine_learning.py to get predictions
    # predictions = some_ml_function(data)
    return render_template('predictions.html', data=data)  # Include predictions if available

if __name__ == '__main__':
    app.run(debug=True)
