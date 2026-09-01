# Documentación Técnica - Sistema de Costos Bioquímicos

## 1. Arquitectura General del Sistema

El sistema implementa una arquitectura desacoplada y modular diseñada para alta precisión financiera y escalabilidad:

- **Backend:** FastAPI (Python 3.10+) con SQLAlchemy 2.0 Async, Pydantic v2 (aritmética con `Decimal` a 4 decimales para costos unitarios), JWT y autenticación RBAC (`admin`, `bioquimico`, `consulta`).
- **Frontend:** Vue 3 (Composition API `<script setup lang="ts">`), Vite, Tailwind CSS, PrimeVue (tema moderno oscuro Aura/Emerald), Pinia, Vue Router 4 y Chart.js.
- **Base de Datos:** SQLite Async (desarrollo local / ZimaBoard) / PostgreSQL 16+ (producción).

---

## 2. Fórmulas del Motor de Costeo y Modelos Financieros

### A. Costo de Equipo / Autoanalizador Prorrateado
$$\text{Costo Mensual Total} = \text{Alquiler} + \text{Mantenimiento} + \text{Amortización} + \text{Calibración \& QC} + \sum \text{Consumibles Mensuales}$$
$$\text{Costo Unitario por Test de Equipo} = \frac{\text{Costo Mensual Total}}{\text{Volumen Mensual Estimado}}$$

### B. Costo Unitario de Insumos y Consumibles por Período / Lote Real
Para cualquier componente (reactivo específico, calibrador multi-analito, control de calidad global o solución de lavado del equipo), el impacto unitario por determinación entregada se calcula mediante:

$$\text{Costo Unitario del Insumo} = \frac{\text{Costo de Compra} \times \text{Unidades Compradas / Consumidas en el Período}}{\text{Total de Determinaciones Entregadas en el Período}}$$

### C. Costo Unitario de la Determinación
$$\text{Costo Insumos y Reactivos} = \sum_{i=1}^{n} (\text{Costo Unitario Insumo}_i \times \text{Cantidad Requerida}_i)$$
$$\text{Costo Unitario Total} = \text{Costo Insumos y Reactivos} + \text{Costo Unitario Equipo} + \text{Costo Mano de Obra}$$

### D. Costo por Protocolo / Atención por Paciente
$$\text{Overhead Fijo por Paciente} = \frac{\sum \text{Gastos Fijos Mensuales}}{\text{Volumen Mensual Pacientes}}$$
$$\text{Costo Protocolo} = \sum \text{Determinaciones} + \text{Kit Materiales Extracción} + \text{Overhead Fijo por Paciente}$$

---

## 3. Estructura de Módulos Backend

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── modules/
│   │   ├── auth/
│   │   ├── equipos/
│   │   ├── insumos/
│   │   ├── determinaciones/
│   │   ├── costos_generales/
│   │   ├── costos/ (Motor de cálculo y simulador)
│   │   └── produccion/ (Conciliación y webhook n8n)
│   └── main.py
├── seed_data.py
└── requirements.txt
```
