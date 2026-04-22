# PS Gaming Analytics 2025

Proyecto de Visualización de Datos enfocado en el análisis de información del sector gaming, utilizando herramientas de análisis exploratorio, dashboards interactivos y reportes reproducibles.

---

## Objetivo

Analizar datos de videojuegos (precios, jugadores y comportamiento) para generar insights mediante:

- Análisis Exploratorio de Datos (EDA)
- Visualización de datos
- Dashboards interactivos
- Reporte analítico en formato Bookdown

---

## Componentes del Proyecto

### Dashboard en Python (Dash)
Aplicación interactiva desarrollada con Dash y Plotly para explorar métricas clave.

### Aplicación en R (Shiny)
Interfaz interactiva en R para visualización dinámica de los datos.

### Bookdown (Reporte Analítico)
Documento estructurado que incluye:

- Introducción  
- Marco teórico  
- Metodología  
- Análisis exploratorio  
- Resultados  
- Conclusiones  

---

## Estructura del Proyecto

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
├── rbook_dataviz3/
│   ├── data/
│   │   ├── games.csv
│   │   ├── players.csv
│   │   └── prices.csv
│   ├── index.Rmd
│   ├── 01-introduccion.Rmd
│   ├── 02-marco.Rmd
│   ├── 03-metodologia.Rmd
│   ├── 04-eda.Rmd
│   ├── 05-resultados.Rmd
│   ├── 06-conclusiones.Rmd
│   ├── _bookdown.yml
│   ├── _output.yml
│   └── style.css
├── INSTRUCCIONES.md
└── README.md
```

---

## Cómo ejecutar el proyecto

### Dashboard en Python

```bash
cd dash_app
pip install -r requirements.txt
python app.py
```

### Aplicación Shiny en R

```r
setwd("shiny_app")
shiny::runApp()
```

### Generar Bookdown

```r
setwd("rbook_dataviz3")
install.packages(c("bookdown","tidyverse","corrplot","kableExtra","ggrepel"))
bookdown::render_book("index.Rmd", "bookdown::gitbook")
```

---

## Datos

Los datasets utilizados se encuentran en las carpetas `data/` de cada módulo:

- games.csv  
- players.csv  
- prices.csv  

---

## Consideraciones

- Mantener la estructura del proyecto para evitar errores de rutas  
- Ejecutar cada componente desde su respectiva carpeta  
- Compilar el Bookdown antes de usar GitHub Pages  

---

## Autor

Alex Terán  
Proyecto académico – Visualización de Datos
