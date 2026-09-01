# 🧪 BioCostos - Sistema de Evaluación de Costos Bioquímicos

Sistema integral para la evaluación, auditoría y simulación financiera de costos en laboratorios de análisis clínicos.

---

## 🚀 Arquitectura del Sistema

* **Backend:** FastAPI (Python 3.10+) con SQLAlchemy 2.0 Async, Pydantic v2, JWT RBAC (`admin`, `bioquimico`, `consulta`), motor de cálculo analítico de alta precisión en USD y ARS.
* **Frontend:** Vue 3 (Composition API `<script setup lang="ts">`), TypeScript, Vite, Tailwind CSS, PrimeVue (tema oscuro Aura/Emerald), Pinia, Chart.js.
* **Base de Datos:** SQLite Async (aiosqlite) / PostgreSQL 16+.
* **Despliegue:** Docker, Docker Compose, Nginx Reverse Proxy (listo para ZimaBoard / CasaOS / Servidor Linux).

---

## 📦 Despliegue en ZimaBoard / Servidor con Docker (Producción)

### 1. Clonar el repositorio
```bash
git clone https://github.com/juanmaobarrio/evaluacion-costos-bioquimicos.git
cd evaluacion-costos-bioquimicos
```

### 2. Iniciar con Docker Compose
```bash
docker compose up -d --build
```

### 3. Accesos en Producción
* **Frontend Web:** `http://<IP-DE-TU-ZIMABOARD>:5174`
* **Backend API Docs (Swagger):** `http://<IP-DE-TU-ZIMABOARD>:8001/api/v1/docs`

---

## 🔑 Credenciales de Acceso Iniciales

| Rol | Correo Electrónico | Contraseña | Capacidades |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@laboratorio.com` | `admin123` | Control total, recálculo de costos, simulador y ABM |
| **Bioquímico Jefe** | `bioquimico@laboratorio.com` | `bio123` | Gestión de determinaciones, insumos, producción |
| **Consulta** | `consulta@laboratorio.com` | `consulta123` | Modo lectura de reportes y dashboard |

---

## 📐 Modelo de Costeo Analítico Implementado

### 1. Insumos y Consumibles
* **Por Tests / Determinación:** Reactivos específicos, calibradores, controles y soluciones de lavado.
  $$\text{Costo Unitario / Test} = \frac{\text{Costo Compra} \times \text{Unidades Compradas}}{\text{Determinaciones Entregadas en el Período}}$$
* **Por Paciente / Extracción:** Tubos, agujas, apósitos, alcohol y algodón.
  $$\text{Costo Unitario / Paciente} = \frac{\text{Costo Compra} \times \text{Unidades Compradas}}{\text{Pacientes Atendidos en el Período}}$$

### 2. Autoanalizadores y Equipos
* **Prorrateo de Costos Fijos:** Alquiler + Mantenimiento Oficial + Amortización + Servicio de Calibración / QC.
  $$\text{Costo Fijo / Test} = \frac{\text{Gasto Fijo Mensual Total}}{\text{Volumen Mensual de Tests Procesados}}$$

### 3. Determinaciones y Prácticas
$$\text{Costo Total Determinación} = \sum \text{Insumos Directos (USD/ARS)} + \text{Costo Equipo / Test} + \text{Mano de Obra}$$
