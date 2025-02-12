import argparse
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
import configparser
from io import StringIO
import threading
import os
import signal
import sys

# Flask app setup
app = Flask(__name__)

# Flag to control the server loop
shutdown_flag = False

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Serve the HTML file

@app.route('/generate-config', methods=['POST'])
def generate_config():
    data = request.json
    config = configparser.ConfigParser()

    # Add Simulation section
    config['Simulation'] = data.get('Simulation', {'trace_path': 'manhattan.xml'})

    # Add Drone sections
    for key, value in data.items():
        if key.startswith('Drone'):
            config[key] = value

    # Add ExportVideo section
    config['ExportVideo'] = {
        'video_directory': 'output_video',
        'only_vants': 0
    }

    # Add ExportXML section
    config['ExportXML'] = {
        'new_xml_path': 'output_simulation.xml'
    }

    # Write to a StringIO object
    config_string = StringIO()
    config.write(config_string)
    config_string.seek(0)

    return config_string.getvalue(), 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=config.ini'
    }

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global shutdown_flag
    shutdown_flag = True
    print("Shutdown signal received. Shutting down the server...")
    # Use os._exit to forcefully terminate the server
    os._exit(0)
    return 'Server is shutting down...', 200

def run_flask():
    app.run(port=5000)

def run():
    parser = argparse.ArgumentParser(description="SuUAV Application")
    parser.add_argument('--setup', action='store_true', help="Start the setup interface in the browser")
    args = parser.parse_args()

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Open the browser automatically
    webbrowser.open('http://127.0.0.1:5000')

    # Keep the main thread alive to keep Flask running
    while not shutdown_flag:
        pass

    print("Server has been shut down.")
