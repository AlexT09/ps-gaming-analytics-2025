# PS Gaming Analytics 2025 — Bookdown

Documento analítico completo sobre la relación entre el género de un
videojuego y su precio de venta en PlayStation Store, con modelado
predictivo de precios usando Lasso, Random Forest y XGBoost.

Generado con [bookdown](https://bookdown.org/) · R · ggplot2

---

## Estructura del documento

| Capítulo | Archivo | Contenido |
|---|---|---|
| 1 | `01-introduccion.Rmd` | Contexto, pregunta de investigación y objetivos |
| 2 | `02-marco.Rmd` | Economía de videojuegos digitales, precios y estrategias de mercado |
| 3 | `03-metodologia.Rmd` | Dataset, proceso ETL y decisiones de análisis |
| 4 | `04-eda.Rmd` | Análisis exploratorio: distribuciones, boxplots, comparativas PS4/PS5 |
| 5 | `05-modelos.Rmd` | Modelos predictivos: Lasso, Random Forest y XGBoost |
| 6 | `06-resultados.Rmd` | Verificación de hipótesis + resultados del modelado |
| 7 | `07-conclusiones.Rmd` | Síntesis, implicaciones prácticas y trabajo futuro |

---

## Datos

Los tres archivos CSV deben estar en `data/` relativo al directorio de trabajo:

```
r/bookdown/
└── data/
    ├── games.csv      # 23.152 juegos — género, plataforma, fecha de lanzamiento
    ├── players.csv    # 356.600 perfiles de jugadores
    └── prices.csv     # 62.816 registros de precios (snapshot febrero 2025, USD)
```

> **Fuente:** Kruglov, A. (2025). *Gaming Profiles 2025 (Steam, PlayStation, Xbox)*.  
> Kaggle · Licencia CC0 · https://www.kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox

---

## Requisitos

- R ≥ 4.3
- RStudio (recomendado) o cualquier entorno que soporte knitr

### Instalación de dependencias

```r
paquetes <- c(
  "tidyverse", "lubridate", "ggrepel", "scales",
  "kableExtra", "corrplot",
  "glmnet", "randomForest", "xgboost",
  "bookdown"
)
instalar <- paquetes[!paquetes %in% installed.packages()[, "Package"]]
if (length(instalar)) install.packages(instalar)
```

---

## Compilar el libro

### Desde RStudio

```r
bookdown::render_book("index.Rmd")
```

### Desde la consola R

```r
setwd("r/bookdown")
bookdown::render_book("index.Rmd", "bookdown::gitbook")
```

El output se genera en la carpeta **`docs/`** (según `_bookdown.yml`: `output_dir: "docs"`).
Tras compilar, abre `docs/index.html` **con un servidor local** para que el menú y la búsqueda funcionen bien:

```r
bookdown::serve_book(dir = ".", output_dir = "docs")
```

Eso evita problemas típicos al abrir el libro solo con `file://` en el navegador. Con `split_by: none` en `_output.yml`, todo el contenido queda en un solo HTML y el TOC navega por anclas dentro del mismo archivo.

### Compilar también en PDF

```r
bookdown::render_book("index.Rmd", "bookdown::pdf_book")
```

> Requiere una instalación de LaTeX. Se recomienda
> [TinyTeX](https://yihui.org/tinytex/): `tinytex::install_tinytex()`

---

## Modelos implementados

| Modelo | Librería R | Hiperparámetros clave |
|---|---|---|
| Lasso Regression | `glmnet` | λ seleccionado por CV 10-fold |
| Random Forest | `randomForest` | `ntree=500`, `mtry=2` |
| XGBoost | `xgboost` | `eta=0.05`, `max_depth=4`, early stopping 30 rondas |

Los tres modelos se evalúan con **R², RMSE y MAE** sobre un conjunto de
prueba del 20% y el modelo ganador (XGBoost) se valida adicionalmente
mediante validación cruzada de 5 pliegues.

---

## Archivos de configuración

| Archivo | Función |
|---|---|
| `index.Rmd` | YAML de configuración y prefacio del libro |
| `_bookdown.yml` | Orden de capítulos y nombre del archivo de salida |
| `_output.yml` | Formato de salida (gitbook HTML + PDF) |
| `style.css` | Estilos personalizados del gitbook |

---

## Referencias principales

- Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
- Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *ACM SIGKDD*, 785–794.
- Friedman, J., Hastie, T., & Tibshirani, R. (2010). Regularization paths via coordinate descent. *Journal of Statistical Software*, 33(1).
- Shapiro, C., & Varian, H. R. (1999). *Information Rules*. Harvard Business School Press.
