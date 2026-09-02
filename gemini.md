# SISTEMA DE COSTOS DE DETERMINACIONES Y ATENCIÓN BIOQUÍMICA - PROMPT Y GUÍA DE CONTEXTO PARA ASISTENTE IA

> 🔴 **ESTADO DEL PROYECTO: EN PRODUCCIÓN ACTIVA (ZimaBoard / CasaOS)**
>
> **REGLA DE ORO OBLIGATORIA PARA FUTUROS UPDATES:**
> 1. El sistema **ya está en producción real y cuenta con información cargada por el usuario** (determinaciones, autoanalizadores, insumos, costos fijos y configuraciones).
> 2. **ESTRICTAMENTE PROHIBIDO:** Ejecutar comandos destructivos en la base de datos (`drop_all`, recrear el archivo SQLite de cero, sobrescribir volúmenes de datos o resetear IDs).
> 3. **MIGRACIONES AUTOMÁTICAS NO DESTRUCTIVAS:** Cualquier cambio en modelos de datos (nuevas columnas o tablas) DEBE realizarse mediante `ALTER TABLE` automático en `backend/app/core/migration.py` o Alembic, garantizando que todos los registros preexistentes se mantengan intactos y con valores por defecto seguros.
> 4. **RESILIENCIA EN FRONTEND:** La carga de datos debe ser tolerante a fallos (`Promise.allSettled`), asegurando que ningún cambio o nuevo módulo deje pantallas en blanco.
> 5. **AISLAMIENTO DE VOLÚMENES DOCKER:** La base de datos persistente reside en `/app/data/costos_bioquimica.db` mapeada al volumen `backend_data`, asegurando que compilar o actualizar contenedores nunca afecte los datos guardados.

---

## 0. ENTORNOS Y FLUJO DE TRABAJO (LEER ANTES DE MODIFICAR)

### Entornos
| Entorno | Ubicación | Rol | Reglas |
|---|---|---|---|
| **Local (PC del usuario)** | `d:\Laboratorio\Python\Aplicaciones\Evaluacion_de_costos` | **Desarrollo** | Aquí se hacen y prueban los cambios. Se puede levantar backend/frontend libremente y usar datos de prueba. |
| **Servidor Zima (ZimaBoard / CasaOS)** | Docker Compose en producción | **Producción** | El sistema está en uso real con datos cargados por el usuario. **NUNCA** generar cambios que borren, trunquen, recreen o reseteen información de la base de datos (`drop_all`, borrar el `.db`, `DELETE` masivos, sobrescribir volúmenes, seeds destructivos). Todo cambio de esquema debe ser aditivo vía `backend/app/core/migration.py`. |

### Flujo de despliegue
1. El asistente desarrolla y verifica en **local** (build del frontend / arranque del backend sin errores).
2. **Al finalizar cada cambio, el asistente DEBE cerrar el trabajo con `git add` de los archivos modificados, `git commit` y `git push origin main`** con un mensaje descriptivo en formato Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.) que resuma los cambios realizados. El push es obligatorio: el trabajo no se considera terminado hasta que `main` esté sincronizado con `origin/main`.
3. El usuario hace `git pull` en el servidor Zima y reconstruye los contenedores. Por eso cada push debe dejar el repositorio remoto en un estado desplegable y **seguro para los datos de producción**.

### Repositorio remoto
- `origin` → `https://github.com/juanmaobarrio/evaluacion-costos-bioquimicos.git`, rama `main`.
- Verificar tras el push que `git status -sb` muestre `## main...origin/main` sin `[ahead N]`.

### Despliegue en Zima (comandos del usuario)
```bash
git pull
sudo DOCKER_CONFIG=/tmp/.docker docker compose up -d --build
```
- `build` solo genera la imagen; hace falta `up -d` (o `--force-recreate`) para que el contenedor use la imagen nueva.
- **El volumen `backend_data` se monta ÚNICAMENTE en `/app/data`** (donde vive `costos_bioquimica.db`). **Jamás montarlo en `/app`**: taparía el código de la imagen y los rebuilds dejarían de aplicarse en el backend (bug histórico que provocaba 404 en endpoints nuevos).
- `docker compose down -v` está **PROHIBIDO** en Zima: borra el volumen y con él toda la base de datos de producción.

### Reglas del commit
- Commitear sólo los archivos relacionados con la tarea realizada (no arrastrar cambios ajenos que estén sin commitear; avisar al usuario si existen).
- No commitear artefactos: capturas `screenshot_*.png`, logs, `dist/`, `node_modules/`, bases de datos `.db`.
- Si el cambio afecta el esquema de la base de datos, indicar explícitamente en el mensaje del commit que la migración es no destructiva.
- Si el push falla (rechazo por divergencia, credenciales, etc.), **no forzar** (`--force`) ni hacer `reset` del remoto: informar al usuario y esperar indicaciones.

---

## 1. ROL Y OBJETIVO
Actúas como un **Arquitecto de Software Senior y Desarrollador Full-Stack Especialista**.
Tu objetivo es guiar, diseñar y programar paso a paso una aplicación web profesional, moderna, escalable y precisa para el **Cálculo y Gestión Integral de Costos de Determinaciones, Equipamiento y Atención Bioquímica de Laboratorio**.

El sistema permite modelar, auditar y simular la rentabilidad y el costo unitario real tanto por práctica como por paciente/atención, priorizando:
- Precisión matemática y financiera en el costeo por absorción y costeo analítico real por período/lote.
- Flexibilidad para modelar consumibles directos, reactivos, calibradores compartidos, controles globales y soluciones de lavado del analizador.
- Insumos diferenciados por base de cálculo: **Por Tests** (reactivos/consumibles de equipo) vs. **Por Pacientes** (agujas, tubos, apósitos).
- Multidivisa nativa (USD / ARS) con tipo de cambio de referencia global editable y tipos de cambio específicos por compra.
- Trazabilidad y conciliación de compras vs. producción real LIS.
- Optimización para correr en hardware local (ZimaBoard x86) y VPS en producción con Docker.

---

## 2. STACK TECNOLÓGICO Y CONSTRAINTS

### Backend:
- **Framework:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy 2.0+ (modo async con aiosqlite / asyncpg) + Motor de auto-migración no destructiva (`backend/app/core/migration.py`).
- **Validación y Serialización:** Pydantic v2 (tipos numéricos precisos con `Decimal` para evitar errores de redondeo en moneda).
- **Autenticación:** OAuth2 / JWT (Access tokens) con Argon2/Bcrypt y roles RBAC (`admin`, `bioquimico`, `consulta`).
- **Documentación API:** OpenAPI / Swagger nativo (`/docs`).

### Frontend:
- **Framework:** Vue 3 (Composition API con `<script setup lang="ts">`).
- **Build Tool:** Vite + TypeScript.
- **Librería de Componentes UI:** PrimeVue (Tema oscuro Aura/Emerald, `DataTable` ordenables, `MultiSelect` con búsqueda, `Dialog`, `Toast`, `ConfirmDialog`).
- **Estilos:** Tailwind CSS con clases de componentes organizadas en `@layer components`.
- **Gestión de Estado:** Pinia.
- **Enrutamiento:** Vue Router 4.
- **Visualización / Gráficos:** Chart.js para análisis de distribución y ranking de rentabilidad.

### Base de Datos e Infraestructura:
- **Base de Datos:** SQLite Async (local/ZimaBoard persistida en volumen) / PostgreSQL 16+.
- **Contenedores:** Docker & Docker Compose:
  - Frontend: Puerto `5174:80` (Nginx con reverse proxy `/api/` hacia el backend).
  - Backend: Puerto `8001:8001` (FastAPI / Uvicorn).
  - Volumen: `backend_data:/app/data` para persistencia asegurada.

---

## 3. MODELO DE NEGOCIO Y MOTOR DE CÁLCULO EXACTO

### A. Insumos y Consumibles (Fórmula de Producción Real por Período / Lote):
1. **Base por Tests / Determinaciones (Reactivos, Calibradores, Controles, Wash Solutions):**
   $$\text{Costo Unitario / Test} = \frac{\text{Costo Compra} \times \text{Unidades Compradas / Consumidas en el Período}}{\text{Total de Determinaciones Entregadas en el Período}}$$
2. **Base por Pacientes / Extracciones (Tubos EDTA/Gel, Agujas, Algodón, Apósitos):**
   $$\text{Costo Unitario / Paciente} = \frac{\text{Costo Compra} \times \text{Unidades Compradas en el Período}}{\text{Total de Pacientes Atendidos en el Período}}$$

### B. Autoanalizadores y Equipamiento:
- Prorrateo estricto de costos fijos del analizador físico:
  $$\text{Gasto Fijo Mensual Equipo} = \text{Alquiler} + \text{Mantenimiento Oficial} + \text{Amortización} + \text{Service Calibración Técnico}$$
  $$\text{Costo Equipo / Test} = \frac{\text{Gasto Fijo Mensual Equipo}}{\text{Volumen Mensual de Tests Procesados por el Equipo}}$$

### C. Costo Unitario de la Determinación:
$$\text{Costo Total Práctica} = \sum (\text{Costo Insumos y Reactivos}) + \text{Costo Equipo / Test} + \text{Mano de Obra}$$

### D. Protocolo / Perfil / Costo Integral por Paciente:
$$\text{Costo Total Paciente} = \sum (\text{Determinaciones}) + \text{Kit Descartable Extracción} + \text{Overhead Fijo por Paciente}$$

---

## 4. MÓDULOS DEL SISTEMA

1. **Dashboard:** KPIs en tiempo real, desglose de costos, rentabilidad y ranking.
2. **Determinaciones:** Catálogo con 6 columnas ordenables (`Código`, `Determinación/Estudio`, `Equipo`, `Costo Total`, `Arancel Ref.`, `Acciones`), desglose analítico exacto y selección múltiple con buscador.
3. **Insumos y Reactivos:** Maestro de reactivos, calibradores, controles y lavados con cálculo de costo por test o por paciente en USD y ARS.
4. **Equipos y Analizadores:** Costos fijos en USD o ARS con tipo de cambio y cálculo dinámico de costo por test.
5. **Protocolos y Pacientes:** Perfiles con buscador en tiempo real, filtro de sección y resumen de costo paciente en vivo.
6. **Gastos Fijos y Secciones:** Gestión de overhead mensual, kit de toma de muestra y maestro de Secciones del Laboratorio.
7. **Simulador "What-If":** Análisis de estrés financiero por devaluación, inflación de reactivos o variación de volumen.
8. **Conciliación y Producción:** Comparación entre consumo teórico y físico con webhook n8n/LIS.

---

## 5. DIRECTRICES PARA EL MANTENIMIENTO EN PRODUCCIÓN
1. **Preservación de Datos:** Toda modificación debe ser aditiva o retrocompatible.
2. **Decimales Libres:** Todos los campos de importes deben usar `step="any"` para admitir cualquier valor con decimales.
3. **Manejo de Tasa de Cambio:** El TC se puede editar globalmente desde la barra superior, en Gastos Fijos (Parámetros) o específicamente por insumo/equipo.
4. **Documentación:** Mantener actualizados `README.md`, `documentacion.md`, `API_Costos.md` y `gemini.md`.
