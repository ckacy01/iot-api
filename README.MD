# API IoT con Flask

API REST para recibir y consultar datos de sensores desde un ESP32 (MicroPython).

## Rutas disponibles

- `POST /data` → Recibe datos JSON del ESP32
- `GET /data` → Lista todos los datos guardados
- `GET /status` → Muestra estado del sistema
- `POST /data/reset` → Borra todos los datos

## Ejemplo de datos enviados

```json
{
  "sensor": "temperatura",
  "valor": 25.7
}

