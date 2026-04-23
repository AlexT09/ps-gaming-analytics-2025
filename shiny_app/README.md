# 🎮 PlayStation Analytics — Dashboard R / Shiny

> **Proyecto ejemplo** para la entrega de Visualización de Datos

---

## 📌 Descripción

Dashboard web construido en **R** con **Shiny** y **Plotly** para explorar el dataset *Gaming Profiles 2025* de PlayStation.

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

Asegúrate de tener R instalado. Instala los paquetes necesarios:

```r
install.packages(c("shiny", "shinydashboard", "tidyverse", "plotly", "DT", "scales", "lubridate"))
```

---

## 🚀 Ejecución

```r
cd shiny_app
shiny::runApp()
```

O abre `app.R` en RStudio y ejecuta la aplicación.