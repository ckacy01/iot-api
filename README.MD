# API IoT Smart Home con Flask

API REST para recibir, consultar y controlar datos de sensores desde un ESP32 (MicroPython, Wokwi compatible).

## Endpoints disponibles

### Sensores

- `POST /data`  
  Recibe datos JSON de sensores desde el ESP32.  
  **Campos requeridos:**  
  - `temperature` (float)
  - `humidity` (float)
  - `gas_level` (int)
  - `motion_detected` (bool)
  - `device_id` (opcional, para identificar el dispositivo)

- `GET /data`  
  Devuelve todos los datos de sensores almacenados (más recientes primero).

- `GET /latest`  
  Devuelve la última lectura de sensores recibida.

- `POST /data/reset`  
  Borra todos los datos de sensores almacenados.

### Controles remotos

- `POST /control/temperature`  
  Fija o desactiva el valor de temperatura (sobrescribe el valor recibido).

- `POST /control/humidity`  
  Fija o desactiva el valor de humedad.

- `POST /control/gas`  
  Fija o desactiva el valor de gas.

- `POST /control/motion`  
  Fija o desactiva el valor de detección de movimiento.

- `POST /control/lights`  
  Enciende o apaga las luces.

- `POST /control/alarm`  
  Activa o desactiva la alarma.

- `POST /control/simulation_mode`  
  Activa o desactiva el modo simulación.

- `GET /controls`  
  Consulta el estado actual de todos los controles.

- `POST /controls/reset`  
  Restaura todos los controles a sus valores por defecto.

### Sistema

- `GET /status`  
  Devuelve el estado del sistema, configuración y metadatos.

- `GET /health`  
  Healthcheck para monitoreo de uptime.

## Ejemplo de datos enviados

```json
{
  "temperature": 25.7,
  "humidity": 60.2,
  "gas_level": 120,
  "motion_detected": false,
  "device_id": "esp32-001"
}
```

## Notas

- Todos los endpoints devuelven respuestas en formato JSON.
- CORS habilitado para cualquier origen.
- Los controles remotos permiten forzar valores de sensores o activar dispositivos en tiempo real.
- El sistema almacena hasta 100 registros recientes por defecto (configurable).

---
© 2025 Quadcode Innovators · MIT educational
