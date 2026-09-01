# Especificación de API y Guía de Integración (LIS & n8n)

## Base URL
`http://localhost:8001/api/v1`

## Autenticación
OAuth2 Bearer Token:
- **POST** `/auth/login` con `username` y `password` (form-data). Retorna `{ "access_token": "...", "token_type": "bearer", "user": {...} }`.

---

## 1. Webhook para Ingesta Masiva de Producción (n8n / LIS)
- **Método:** `POST`
- **Endpoint:** `/produccion/webhook-import`
- **Headers:** `Content-Type: application/json`

### Payload de ejemplo:
```json
{
  "periodo_mes": 5,
  "periodo_anio": 2024,
  "fuente": "n8n_webhook",
  "items": [
    { "determinacion_codigo_o_id": "DET-001", "cantidad_estudios": 420 },
    { "determinacion_codigo_o_id": "DET-002", "cantidad_estudios": 310 },
    { "determinacion_codigo_o_id": "DET-005", "cantidad_estudios": 550 },
    { "determinacion_codigo_o_id": "DET-006", "cantidad_estudios": 180 }
  ]
}
```

---

## 2. Consulta de Conciliación de Insumos (Teórico vs Real)
- **Método:** `GET`
- **Endpoint:** `/produccion/conciliacion?mes=5&anio=2024`

Retorna la comparativa por insumo con detección automática de desvíos superiores al 15%.

---

## 3. Simulador de Sensibilidad Financiera (What-If)
- **Método:** `POST`
- **Endpoint:** `/costos/simular`
- **Payload:**
```json
{
  "variacion_usd_porcentaje": 20.0,
  "variacion_reactivos_porcentaje": 15.0,
  "variacion_fijos_porcentaje": 10.0,
  "variacion_volumen_pacientes_porcentaje": -15.0
}
```
