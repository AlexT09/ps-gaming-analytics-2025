# Dash App — PS Gaming Analytics 2025

Dashboard interactivo en Python con Dash + Plotly. Análisis exploratorio y predicción de precios del catálogo PlayStation Store (snapshot febrero 2025).

---

## Estructura

```
dash_app/
├── app.py              ← Punto de entrada, layout y callbacks
├── data.py             ← ETL: carga, limpieza y agregados
├── requirements.txt    ← Dependencias Python
├── Dockerfile
├── docker-compose.yml
├── README.md
├── assets/
│   └── custom.css      ← Estilos globales del dashboard
└── tabs/               ← Pestañas separadas por módulo
    ├── __init__.py
    ├── tab_introduccion.py
    ├── tab_objetivos.py
    ├── tab_metodologia.py
    ├── tab_modelos.py
    └── tab_prediccion.py
```

> Los datos se leen desde `../../data/` (raíz del proyecto). No hay carpeta `data/` local en esta app.

---

## Requisitos

- Python ≥ 3.10
- Las dependencias están en `requirements.txt`

```
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
gunicorn>=21.0.0
```

---

## Ejecución local

```bash
# 1. Crear entorno virtual (desde la carpeta dash_app)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python app.py
```

Abrir en el navegador: http://127.0.0.1:8050

---

## Ejecución con Docker

```bash
# Desde la carpeta dash_app
docker compose up --build
```

Abrir en el navegador: http://localhost:8050

---

## Pestañas disponibles

| Ruta | Sección |
|---|---|
| `/` | Resumen — KPIs, plataformas, lanzamientos anuales, calidad de datos |
| `/introduccion` | Introducción — contexto y pregunta de investigación |
| `/objetivos` | Objetivos del análisis |
| `/metodologia` | Metodología — flujo ETL paso a paso |
| `/eda` | EDA / Precios — distribuciones, outliers, PS4 vs PS5, correlaciones |
| `/simulador` | Simulador — benchmark descriptivo por género (mediana, Q1–Q3) |
| `/modelos` | Métricas — comparación Lasso, Random Forest y XGBoost |
| `/prediccion` | Predictor de precios con XGBoost |
| `/explorador` | Explorador — tabla filtrable del catálogo completo |

---

## Despliegue en Render.com

| Campo | Valor |
|---|---|
| Root directory | `python/dash_app` |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:server` |
| Puerto | `10000` (Render asigna `$PORT` automáticamente) |

> Render requiere `gunicorn` como servidor WSGI. El objeto `server = app.server` ya está expuesto en `app.py`.
