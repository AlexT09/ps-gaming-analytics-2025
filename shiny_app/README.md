# 🎮 PlayStation Gaming Dashboard — Shiny App

> **Proyecto ejemplo** para la entrega de Visualización de Datos

---

## 📌 Descripción

Aplicación interactiva construida con **R Shiny** y **shinydashboard** para explorar el dataset *Gaming Profiles 2025* de PlayStation.

La aplicación permite:
- Consultar KPIs del catálogo, jugadores y precios
- Filtrar por país, género y rangos de precio
- Visualizar gráficos interactivos con Plotly
- Explorar y exportar las tablas de datos

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

### Paso 1 — Instalar R y RStudio

- R: https://cran.r-project.org/
- RStudio: https://posit.co/downloads/

### Paso 2 — Instalar dependencias

```r
install.packages(c(
  "shiny",
  "shinydashboard",
  "tidyverse",
  "plotly",
  "DT",
  "scales"
))
```

---

## ▶️ Ejecución local

```r
setwd("ruta/a/ps-gaming-analytics-2025/shiny_app")
shiny::runApp()
```

La app se abrirá en `http://127.0.0.1:XXXX`

---

## 📊 Pestañas de la aplicación

| Pestaña | Descripción |
|---------|-------------|
| 🏠 Resumen | KPIs globales · Top géneros · Suscripción · Catálogo |
| 👥 Jugadores | Distribución geográfica · Filtros por país |
| 💰 Precios | Histograma · Boxplot · Evolución temporal |
| 🔍 Explorador | Tablas interactivas con exportación CSV |

---

## 🛠️ Tecnologías

- R ≥ 4.2
- shiny
- shinydashboard
- tidyverse
- plotly
- DT
- scales

> El dataset ya está incluido en `shiny_app/data/`.
