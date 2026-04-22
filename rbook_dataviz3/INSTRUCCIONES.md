# Instrucciones de entrega

## Estructura final del repositorio

- `dash_app/`
  - `app.py`
  - `requirements.txt`
  - `README.md`
  - `data/`
    - `games.csv`
    - `players.csv`
    - `prices.csv`

- `shiny_app/`
  - `app.R`
  - `README.md`
  - `data/`
    - `games.csv`
    - `players.csv`
    - `prices.csv`

- `INSTRUCCIONES.md`

> El nombre de la carpeta raíz de este proyecto idealmente debe ser `ps-gaming-analytics-2025`.

---

## Cómo ejecutar cada app

### Dash

```bash
cd dash_app
pip install -r requirements.txt
python app.py
```

Abrir luego en `http://127.0.0.1:8050`

### Shiny

```r
setwd("ruta/a/ps-gaming-analytics-2025/shiny_app")
shiny::runApp()
```

La app se abrirá en `http://127.0.0.1:XXXX`

---

## Notas

- El dataset ya está incluido en las carpetas `dash_app/data/` y `shiny_app/data/`.
- Si agregas el repositorio a GitHub, asegúrate de incluir los CSV dentro de cada `data/`.
- Este repositorio está preparado como ejemplo de entrega con las dos aplicaciones y la documentación mínima necesaria.
