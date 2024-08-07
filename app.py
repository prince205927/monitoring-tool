from flask import Flask, render_template, request, redirect, url_for, jsonify
import paramiko
import re
from threading import Thread
import time
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime  # Import datetime module

app = Flask(__name__)

# Global variables to store data and manage intervals
server_data = []
update_interval = 5  # Default interval in seconds
stop_thread = False
background_thread = None  # To keep track of the background thread

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'stats'
}

def get_server_stats(ip, username, password, port):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        # Retrieve CPU usage from /proc/stat
        stdin, stdout, stderr = ssh.exec_command("cat /proc/stat | grep '^cpu '")
        cpu_line = stdout.read().decode().strip()
        cpu_times = list(map(int, cpu_line.split()[1:]))
        idle_time = cpu_times[3]
        total_time = sum(cpu_times)
        used_cpu = 100.0 * (1 - idle_time / total_time)

        # Retrieve Memory usage from /proc/meminfo
        stdin, stdout, stderr = ssh.exec_command("cat /proc/meminfo")
        mem_info = stdout.read().decode().strip().split('\n')
        mem_total = int(mem_info[0].split()[1]) // 1024  # Convert kB to MB
        mem_free = int(mem_info[1].split()[1]) // 1024  # Convert kB to MB
        mem_available = int(mem_info[2].split()[1]) // 1024  # Convert kB to MB
        mem_used = mem_total - mem_available

        # Retrieve Storage usage from df
        stdin, stdout, stderr = ssh.exec_command("df -h --output=source,size,used,pcent | grep '^/'")
        storage_lines = stdout.read().decode().strip().split('\n')
        storage_usage = []
        for line in storage_lines:
            parts = re.split(r'\s+', line)
            filesystem, total, used, used_percent = parts[0], parts[1], parts[2], parts[3]
            storage_usage.append({
                'filesystem': filesystem,
                'total': total,
                'used': used,
                'used_percent': used_percent
            })

        ssh.close()

        return {
            'cpu_usage': used_cpu,
            'mem_total': mem_total,
            'mem_used': mem_used,
            'storage_usage': storage_usage
        }

    except Exception as e:
        return {'error': str(e)}

def insert_stats_into_db(stats):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Convert UNIX timestamp to DATETIME format
        timestamp_str = datetime.fromtimestamp(stats['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        query = """INSERT INTO server_stats (timestamp, cpu_usage, mem_total, mem_used, storage_usage) 
                   VALUES (%s, %s, %s, %s, %s)"""
        data = (timestamp_str, stats['cpu_usage'], stats['mem_total'], stats['mem_used'], 
                json.dumps(stats['storage_usage']))
        cursor.execute(query, data)
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error inserting data: {e}")

def background_task(ip, username, password, port):
    global server_data, stop_thread
    while not stop_thread:
        stats = get_server_stats(ip, username, password, port)
        stats['timestamp'] = time.time()
        insert_stats_into_db(stats)  # Insert data into the database
        server_data.append(stats)
        # Keep only the last 100 data points
        if len(server_data) > 100:
            server_data = server_data[-100:]
        time.sleep(update_interval)

@app.route("/", methods=["GET", "POST"])
def index():
    global update_interval, stop_thread, background_thread
    if request.method == "POST":
        ip = request.form["ip"]
        username = request.form["username"]
        password = request.form["password"]
        port = int(request.form["port"])
        update_interval = int(request.form["interval"])
       
        # Stop existing thread if running
        if stop_thread:
            stop_thread = True
            if background_thread:
                background_thread.join()  # Ensure the old thread has stopped
       
        # Start new background thread
        stop_thread = False
        background_thread = Thread(target=background_task, args=(ip, username, password, port))
        background_thread.start()
       
        return redirect(url_for('result'))
   
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/stats")
def stats():
    global server_data
    return jsonify(server_data)

@app.route("/update_interval", methods=["POST"])
def update_interval():
    global update_interval
    new_interval = int(request.form["interval"])
    update_interval = new_interval / 1000  # Convert milliseconds to seconds
    return jsonify({"status": "success", "new_interval": new_interval / 1000})  # Return interval in seconds

if __name__ == "__main__":
    app.run(debug=True)
