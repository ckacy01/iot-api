"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ HTTP API for ESP32 IoT Sensor System with                ┃
┃ Micropython Implementation for Wokwi                     ┃
┃                                                          ┃
┃ Description:                                             ┃
┃ This API allows to receive data from the wokwi and also  ┃
┃ allows the remote control of the cicuicuito being        ┃
┃ able to control it in real time.                         ┃
┃                                                          ┃       
┃ Copyright (c) 2025 Quadcode Innovators                   ┃
┃ Author: Jorge Avila                                      ┃
┃ Version: 1.0                                             ┃         
┃ Compatible: MicroPython, ESP32, Wokwi Simulator          ┃
┃ License: MIT educational                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

"""

from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# ============================================================================
# In-Memory Storage and System Configuration
# ============================================================================

sensor_data = []  # List to store recent sensor readings
device_controls = {
    'temperature_override': None,
    'humidity_override': None,
    'gas_override': None,
    'motion_override': None,
    'lights': False,
    'alarm': False,
    'simulation_mode': False
}

system_config = {
    'update_interval': 1,  # Data update interval in seconds
    'max_records': 100,    # Maximum number of stored sensor records
    'auto_cleanup': True   # Whether to remove old data automatically
}

# ============================================================================
# Background Cleanup Thread
# ============================================================================

def cleanup_old_data():
    """
    Background task that periodically removes old sensor records 
    to keep the list within 'max_records' limit.
    """
    while True:
        if len(sensor_data) > system_config['max_records']:
            sensor_data.pop(0)  # Remove oldest record
        time.sleep(60)

cleanup_thread = threading.Thread(target=cleanup_old_data, daemon=True)
cleanup_thread.start()

# ============================================================================
# Core Endpoints
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint to verify API is running"""
    return "API IoT Smart Home - running successfully", 200


@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receives sensor data from ESP32.
    Supports overriding sensor values via remote controls.
    """
    try:
        data = request.get_json()

        # Ensure required fields are present
        required_fields = ['temperature', 'humidity', 'gas_level', 'motion_detected']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Apply control overrides
        for key in ['temperature', 'humidity', 'gas_level', 'motion_detected']:
            override_key = f"{key.split('_')[0]}_override"
            if device_controls[override_key] is not None:
                data[key] = device_controls[override_key]

        # Add timestamp and control flags
        data.update({
            'timestamp': datetime.utcnow().isoformat(),
            'lights': device_controls['lights'],
            'alarm': device_controls['alarm'],
            'simulation_mode': device_controls['simulation_mode']
        })

        # Replace existing data for the same device or keep only the latest
        if 'device_id' in data:
            sensor_data[:] = [d for d in sensor_data if d.get('device_id') != data['device_id']]
        else:
            sensor_data.clear()

        sensor_data.append(data)

        return jsonify({
            'status': 'ok',
            'data': data,
            'controls': device_controls.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/data', methods=['GET'])
def get_all_data():
    """Returns all sensor data (most recent first)"""
    return jsonify({
        'data': sensor_data[::-1],
        'total_records': len(sensor_data),
        'controls': device_controls,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/latest', methods=['GET'])
def get_latest_data():
    """Returns the most recent sensor reading"""
    if sensor_data:
        return jsonify({
            'data': sensor_data[-1],
            'controls': device_controls,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    return jsonify({'message': 'No data available'}), 404

# ============================================================================
# Remote Control Endpoints
# ============================================================================

def create_control_endpoint(key, description, cast_type):
    """
    Factory to create reusable control endpoints with unique names.
    """
    def control():
        try:
            data = request.get_json()
            override_key = f"{key}_override" if key in ['temperature', 'humidity', 'gas', 'motion'] else key
            if 'value' in data:
                device_controls[override_key] = cast_type(data['value'])
                msg = f'{description} set to {data["value"]}'
            else:
                device_controls[override_key] = None
                msg = f'{description} override disabled'
            return jsonify({
                'status': 'ok',
                'message': msg,
                'current_override': device_controls.get(override_key)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Assign a unique name to the control function
    control.__name__ = f'control_{key}'

    # Register the control endpoint with Flask
    app.route(f'/control/{key}', methods=['POST'], endpoint=f'control_{key}')(control)

# Generate control endpoints
create_control_endpoint('temperature', 'Temperature', float)
create_control_endpoint('humidity', 'Humidity', float)
create_control_endpoint('gas', 'Gas level', int)
create_control_endpoint('motion', 'Motion detection', bool)
create_control_endpoint('lights', 'Lights', bool)
create_control_endpoint('alarm', 'Alarm', bool)
create_control_endpoint('simulation_mode', 'Simulation mode', bool)


@app.route('/controls', methods=['GET'])
def get_all_controls():
    """Returns the current status of all controls"""
    return jsonify({
        'controls': device_controls,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/controls/reset', methods=['POST'])
def reset_all_controls():
    """Resets all control overrides to default values"""
    global device_controls
    device_controls = {
        'temperature_override': None,
        'humidity_override': None,
        'gas_override': None,
        'motion_override': None,
        'lights': False,
        'alarm': False,
        'simulation_mode': False
    }
    return jsonify({
        'status': 'ok',
        'message': 'All controls have been reset'
    }), 200

# ============================================================================
# System Management Endpoints
# ============================================================================

@app.route('/status', methods=['GET'])
def system_status():
    """Returns system status, configuration and metadata"""
    return jsonify({
        'system': 'OK',
        'version': '2.0',
        'records': len(sensor_data),
        'active_controls': sum(1 for v in device_controls.values() if v not in [None, False]),
        'last_update': sensor_data[-1]['timestamp'] if sensor_data else None,
        'config': system_config,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/data/reset', methods=['POST'])
def reset_sensor_data():
    """Deletes all sensor data from memory"""
    sensor_data.clear()
    return jsonify({
        'status': 'sensor data cleared',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check for uptime monitoring"""
    return jsonify({
        'status': 'healthy',
        'uptime': 'running',
        'data_count': len(sensor_data),
        'last_update': sensor_data[-1]['timestamp'] if sensor_data else 'never',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# ============================================================================
# CORS Configuration
# ============================================================================

@app.after_request
def add_cors_headers(response):
    """Adds CORS headers to allow requests from any origin"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == '__main__':
    print("Starting Smart Home IoT API v2.0...")
    print("Available Endpoints:")
    print("   POST /data              - Receive sensor data")
    print("   GET  /data              - Get all sensor data")
    print("   GET  /latest            - Get latest sensor data")
    print("   POST /control/...       - Remote control commands")
    print("   GET  /controls          - Check current control status")
    print("   POST /controls/reset    - Reset all controls")
    print("   GET  /status            - System status")
    print("   POST /data/reset        - Clear all sensor data")
    app.run(debug=True, host='0.0.0.0', port=5000)
