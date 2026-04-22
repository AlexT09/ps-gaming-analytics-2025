# 🎮 PlayStation Analytics — Dashboard Python / Dash

> **Proyecto ejemplo** para la entrega de Visualización de Datos

---

## 📌 Descripción

Dashboard web construido en **Python** con **Dash** y **Plotly** para explorar el dataset *Gaming Profiles 2025* de PlayStation.

La aplicación incluye:
- KPIs del catálogo de juegos y jugadores
- Gráficos interactivos de géneros, países y precios
- Explorador de tablas con filtros y exportación CSV

---

## 📂 Estructura

```
ps-gaming-analytics-2025/
├── dash_app/
│   ├── app.py
│   ├── requirements.txt
│   ├── README.md
│   └── data/
│       ├── games.csv
│       ├── players.csv
│       └── prices.csv
├── shiny_app/
│   ├── app.R
│   ├── README.md
│   └── data/
│       ├── games.csv
│       ├── players.csv
│       └── prices.csv
└── INSTRUCCIONES.md
```

---

## ⚙️ Instalación

```bash
cd dash_app
pip install -r requirements.txt
```

---

## ▶️ Ejecución

```bash
cd dash_app
python app.py
```

Abrir luego en el navegador: `http://127.0.0.1:8050`

---

## 📊 Pestañas

| Pestaña | Contenido |
|---------|-----------|
| 🏠 Resumen | KPIs · Géneros · Suscripciones · Tabla catálogo |
| 👥 Jugadores | Top países filtrable · Scatter geográfico |
| 💰 Precios | Histograma · Boxplot · Serie de tiempo |
| 🔍 Explorador | Tablas con filtros y exportación CSV |

---

## 🛠️ Dependencias

- dash
- dash-bootstrap-components
- pandas
- plotly
- numpy

> El dataset ya está incluido en `dash_app/data/`.
