from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Almacenamiento temporal (RAM)
sensor_data = []

@app.route('/', methods=['GET'])
def index():
    return "✅ API IoT corriendo correctamente", 200

@app.route('/data', methods=['POST'])
def recibir_datos():
    try:
        data = request.get_json()
        if 'sensor' not in data or 'valor' not in data:
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        data['timestamp'] = datetime.utcnow().isoformat()
        sensor_data.append(data)

        return jsonify({'status': 'ok', 'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data', methods=['GET'])
def obtener_datos():
    return jsonify(sensor_data[::-1]), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'sistema': 'OK', 'registros': len(sensor_data)}), 200

@app.route('/data/reset', methods=['POST'])
def resetear_datos():
    sensor_data.clear()
    return jsonify({'status': 'datos eliminados'}), 200

if __name__ == '__main__':
    app.run(debug=True)

