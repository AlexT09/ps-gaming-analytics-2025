# ╔══════════════════════════════════════════════════════════════╗
# ║  🎮 PlayStation Gaming Analytics 2025                       ║
# ║  Alex Teran · Ciencia de Datos · Grupo 13                   ║
# ╚══════════════════════════════════════════════════════════════╝

library(shiny)
library(shinydashboard)
library(tidyverse)
library(plotly)
library(DT)
library(scales)
library(lubridate)

# ════════════════════════════════════════════════════════════════
# PALETA PS
# ════════════════════════════════════════════════════════════════
PS_BLUE  <- "#003087"
PS_RED   <- "#E63946"
PS_LIGHT <- "#A8DADC"
PS_DARK  <- "#001A52"
PS_GOLD  <- "#F4A261"

# ════════════════════════════════════════════════════════════════
# CARGA Y PREPARACIÓN DE DATOS
# ════════════════════════════════════════════════════════════════
base_dir <- if (file.exists("data/games.csv")) "data" else "../data"

games <- read_csv(file.path(base_dir, "games.csv"), show_col_types = FALSE) %>%
  distinct() %>%
  mutate(
    release_date     = as.Date(release_date),
    year             = year(release_date),
    genres_clean     = str_remove_all(coalesce(genres, ""), "[\\[\\]']"),
    publishers_clean = str_remove_all(coalesce(publishers, ""), "[\\[\\]']"),
    developers_clean = str_remove_all(coalesce(developers, ""), "[\\[\\]']")
  )

players <- read_csv(file.path(base_dir, "players.csv"), show_col_types = FALSE) %>%
  distinct() %>%
  filter(!is.na(country), country != "")

prices <- read_csv(file.path(base_dir, "prices.csv"), show_col_types = FALSE) %>%
  distinct() %>%
  filter(!is.na(usd), usd > 0, usd < 150) %>%
  mutate(date_acquired = as.Date(date_acquired))

# Dataset enriquecido: juegos + precios
games_prices <- games %>%
  inner_join(prices, by = "gameid")

# Géneros expandidos para análisis
genres_long <- games %>%
  filter(genres_clean != "") %>%
  separate_rows(genres_clean, sep = ",\\s*") %>%
  filter(genres_clean != "") %>%
  mutate(genres_clean = str_trim(genres_clean))

# Precio por género
precio_genero <- genres_long %>%
  inner_join(prices %>% select(gameid, usd), by = "gameid") %>%
  group_by(genres_clean) %>%
  summarise(precio_prom = mean(usd, na.rm = TRUE),
            n = n(), .groups = "drop") %>%
  filter(n >= 15)

# Métricas globales
N_GAMES      <- nrow(games)
N_PLAYERS    <- nrow(players)
N_COUNTRIES  <- n_distinct(players$country)
MED_PRICE    <- median(prices$usd, na.rm = TRUE)
PLATS        <- c("Todas", sort(unique(na.omit(games$platform))))
YEAR_RANGE   <- range(games$year, na.rm = TRUE)

# ════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════
ui <- dashboardPage(
  skin = "blue",

  dashboardHeader(
    title = tags$span(
      tags$img(
        src = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Playstation_logo_colour.svg/60px-Playstation_logo_colour.svg.png",
        height = "26px", style = "margin-right:8px; vertical-align:middle;"
      ),
      "Gaming Analytics 2025"
    ),
    titleWidth = 290
  ),

  dashboardSidebar(
    width = 240,
    sidebarMenu(
      id = "sidebar",
      menuItem("🏠 Resumen",         tabName = "resumen",    icon = icon("home")),
      menuItem("🎮 Catálogo",        tabName = "catalogo",   icon = icon("gamepad")),
      menuItem("👥 Jugadores",       tabName = "jugadores",  icon = icon("users")),
      menuItem("💰 Precios",         tabName = "precios",    icon = icon("dollar-sign")),
      menuItem("🔍 Explorador",      tabName = "explorador", icon = icon("table"))
    ),
    hr(),
    tags$div(style = "padding:0 15px;",
      tags$p(tags$b("Filtros globales"), style = "color:#8eb4e0; font-size:0.8rem; margin-bottom:6px;"),
      selectInput("f_plat", "Plataforma:",
                  choices = PLATS, selected = "Todas"),
      sliderInput("f_year", "Año de lanzamiento:",
                  min = YEAR_RANGE[1], max = 2024,
                  value = c(2015, 2024), sep = "", step = 1)
    ),
    hr(),
    tags$div(style = "padding:8px 15px; color:#8eb4e0; font-size:0.76rem;",
      "Alex Terán · Ciencia de Datos", br(), "Gaming Profiles 2025 · Grupo 13")
  ),

  dashboardBody(
    tags$head(tags$style(HTML(paste0("
      .skin-blue .main-header .logo,.skin-blue .main-header .navbar{background-color:", PS_DARK, ";}
      .skin-blue .main-sidebar{background-color:#001540;}
      .skin-blue .sidebar-menu>li.active>a{border-left:3px solid ", PS_LIGHT, ";background-color:#002266;}
      .skin-blue .sidebar-menu>li:hover>a{background-color:#002266;}
      .small-box h3{font-size:2rem;} .small-box .icon{font-size:52px;top:12px;}
      .box.box-primary{border-top-color:", PS_BLUE, ";}
      .insight-box{background:#eef4ff;border-left:4px solid ", PS_BLUE, ";
                   padding:10px 14px;border-radius:4px;margin-bottom:12px;font-size:0.87rem;}
      .insight-box strong{color:", PS_DARK, ";}
      body,label,.control-label{font-family:'Segoe UI',Arial,sans-serif;}
    ")))),

    tabItems(

      # ══════════════════════════════════════════════════════════
      # TAB 1: RESUMEN
      # ══════════════════════════════════════════════════════════
      tabItem(tabName = "resumen",
        fluidRow(
          valueBoxOutput("kpi_juegos",    width = 3),
          valueBoxOutput("kpi_jugadores", width = 3),
          valueBoxOutput("kpi_paises",    width = 3),
          valueBoxOutput("kpi_precio",    width = 3)
        ),

        fluidRow(
          box(title = tags$b("🎮 Juegos por plataforma"),
              status = "primary", solidHeader = TRUE, width = 5,
              plotlyOutput("p_plataforma", height = "300px")),
          box(title = tags$b("📈 Lanzamientos por año"),
              status = "primary", solidHeader = TRUE, width = 7,
              plotlyOutput("p_años", height = "300px"))
        ),

        fluidRow(
          box(title = tags$b("🗺️ Jugadores por región (Top 10)"),
              status = "success", solidHeader = TRUE, width = 6,
              plotlyOutput("p_mapa_resumen", height = "300px")),
          box(title = tags$b("💡 Insights clave del análisis"),
              status = "warning", solidHeader = TRUE, width = 6,
              tags$div(class = "insight-box",
                tags$strong("📌 PS4 sigue dominando: "),
                "Con el 61% del catálogo (14.163 juegos), PS4 supera ampliamente a PS5 a pesar de llevar 4+ años en el mercado."),
              tags$div(class = "insight-box",
                tags$strong("📌 Crecimiento explosivo: "),
                "Los lanzamientos crecieron un 1.570% en una década: de 305 juegos en 2013 a 5.091 en 2024."),
              tags$div(class = "insight-box",
                tags$strong("📌 Mercado ultra-accesible: "),
                "El 86% de los juegos cuesta menos de $20 (mediana: $7,99). PlayStation apuesta por volumen, no margen."),
              tags$div(class = "insight-box",
                tags$strong("📌 EE.UU. + Europa = 59%: "),
                "Norteamérica y Europa Occidental concentran más de la mitad de los jugadores registrados globalmente."),
              tags$div(class = "insight-box",
                tags$strong("📌 El indie es el motor: "),
                "Los 3 publishers más activos (eastasiasoft, Ratalaika, ThiGames) son indies de bajo presupuesto y alto volumen.")
          )
        )
      ),

      # ══════════════════════════════════════════════════════════
      # TAB 2: CATÁLOGO
      # ══════════════════════════════════════════════════════════
      tabItem(tabName = "catalogo",
        fluidRow(
          valueBoxOutput("cat_total",   width = 4),
          valueBoxOutput("cat_plats",   width = 4),
          valueBoxOutput("cat_generos", width = 4)
        ),
        fluidRow(
          box(title = tags$b("🎭 Top géneros"),
              status = "primary", solidHeader = TRUE, width = 6,
              sliderInput("sl_ngen", "Mostrar top N géneros:",
                          min = 5, max = 20, value = 12, step = 1),
              plotlyOutput("p_generos", height = "340px")),
          box(title = tags$b("🏢 Top publishers"),
              status = "primary", solidHeader = TRUE, width = 6,
              plotlyOutput("p_publishers", height = "390px"))
        ),
        fluidRow(
          box(title = tags$b("💰 Precio promedio por género (top 10 más caro)"),
              status = "info", solidHeader = TRUE, width = 12,
              plotlyOutput("p_precio_gen", height = "300px"))
        ),
        fluidRow(
          box(title = tags$b("📋 Catálogo completo"),
              status = "primary", solidHeader = TRUE, width = 12,
              DTOutput("tabla_catalogo"))
        )
      ),

      # ══════════════════════════════════════════════════════════
      # TAB 3: JUGADORES
      # ══════════════════════════════════════════════════════════
      tabItem(tabName = "jugadores",
        fluidRow(
          valueBoxOutput("jug_total",  width = 4),
          valueBoxOutput("jug_paises", width = 4),
          valueBoxOutput("jug_lider",  width = 4)
        ),
        fluidRow(
          box(title = tags$b("⚙️ Filtros"),
              status = "warning", solidHeader = TRUE, width = 3,
              selectInput("dd_pais", "País:",
                          choices  = c("Todos", sort(unique(players$country))),
                          selected = "Todos"),
              sliderInput("sl_top_paises", "Top N países:",
                          min = 5, max = 30, value = 15, step = 5),
              hr(),
              helpText("Selecciona un país para ver solo sus datos,",
                       "o 'Todos' para vista global.")),
          box(title = tags$b("🌍 Jugadores por país"),
              status = "success", solidHeader = TRUE, width = 9,
              plotlyOutput("p_paises", height = "400px"))
        ),
        fluidRow(
          box(title = tags$b("🫧 Concentración geográfica (burbuja)"),
              status = "success", solidHeader = TRUE, width = 8,
              plotlyOutput("p_burbuja_paises", height = "340px")),
          box(title = tags$b("🥧 Top 6 países (proporción)"),
              status = "success", solidHeader = TRUE, width = 4,
              plotlyOutput("p_pie_paises", height = "340px"))
        )
      ),

      # ══════════════════════════════════════════════════════════
      # TAB 4: PRECIOS
      # ══════════════════════════════════════════════════════════
      tabItem(tabName = "precios",
        fluidRow(
          valueBoxOutput("pr_prom",    width = 3),
          valueBoxOutput("pr_mediana", width = 3),
          valueBoxOutput("pr_min",     width = 3),
          valueBoxOutput("pr_max",     width = 3)
        ),
        fluidRow(
          box(title = tags$b("📊 Distribución de precios (USD)"),
              status = "success", solidHeader = TRUE, width = 7,
              plotlyOutput("p_hist_precio", height = "340px")),
          box(title = tags$b("📦 Rangos de precio"),
              status = "success", solidHeader = TRUE, width = 5,
              plotlyOutput("p_rangos", height = "340px"))
        ),
        fluidRow(
          box(title = tags$b("🔀 Precios por moneda (boxplot comparativo)"),
              status = "primary", solidHeader = TRUE, width = 6,
              plotlyOutput("p_box_monedas", height = "300px")),
          box(title = tags$b("🔗 Correlación entre monedas"),
              status = "primary", solidHeader = TRUE, width = 6,
              plotlyOutput("p_correlacion", height = "300px"))
        )
      ),

      # ══════════════════════════════════════════════════════════
      # TAB 5: EXPLORADOR
      # ══════════════════════════════════════════════════════════
      tabItem(tabName = "explorador",
        fluidRow(
          box(title = tags$b("🔎 Filtros de búsqueda"),
              status = "warning", solidHeader = TRUE, width = 12,
              fluidRow(
                column(4,
                  sliderInput("exp_precio", "Rango de precio USD:",
                              min = 0, max = 100, value = c(0, 60))),
                column(4,
                  selectInput("exp_plat2", "Plataforma:",
                              choices = PLATS, selected = "Todas")),
                column(4,
                  selectInput("exp_gen", "Género:", choices = NULL))
              ))
        ),
        fluidRow(
          box(title = tags$b("💎 USD vs EUR — dispersión por juego"),
              status = "primary", solidHeader = TRUE, width = 7,
              plotlyOutput("exp_scatter", height = "360px")),
          box(title = tags$b("📊 Precio promedio del filtro actual"),
              status = "primary", solidHeader = TRUE, width = 5,
              plotlyOutput("exp_gen_precio", height = "360px"))
        ),
        fluidRow(
          box(title = tags$b("📋 Resultados filtrados"),
              status = "primary", solidHeader = TRUE, width = 12,
              DTOutput("exp_tabla"))
        )
      )
    )
  )
)

# ════════════════════════════════════════════════════════════════
# SERVER
# ════════════════════════════════════════════════════════════════
server <- function(input, output, session) {

  # ── Datos reactivos con filtros globales ────────────────────
  gf <- reactive({
    df <- games
    if (input$f_plat != "Todas") df <- df %>% filter(platform == input$f_plat)
    df %>% filter(!is.na(year), year >= input$f_year[1], year <= input$f_year[2])
  })
  pf <- reactive({
    df <- prices
    if (input$f_plat != "Todas") {
      ids <- games %>% filter(platform == input$f_plat) %>% pull(gameid)
      df  <- df %>% filter(gameid %in% ids)
    }
    df
  })

  # Poblar géneros del explorador
  observe({
    gen <- genres_long %>% pull(genres_clean) %>% unique() %>% sort()
    updateSelectInput(session, "exp_gen",
                      choices = c("Todos", gen), selected = "Todos")
  })

  # ── TAB 1: RESUMEN ──────────────────────────────────────────
  output$kpi_juegos    <- renderValueBox(
    valueBox(comma(nrow(gf())), "Juegos en catálogo",
             icon = icon("gamepad"), color = "blue"))
  output$kpi_jugadores <- renderValueBox(
    valueBox(comma(N_PLAYERS), "Jugadores registrados",
             icon = icon("users"), color = "purple"))
  output$kpi_paises    <- renderValueBox(
    valueBox(N_COUNTRIES, "Países representados",
             icon = icon("globe"), color = "teal"))
  output$kpi_precio    <- renderValueBox(
    valueBox(dollar(round(median(pf()$usd, na.rm = TRUE), 2)),
             "Precio mediano (USD)", icon = icon("dollar-sign"), color = "green"))

  output$p_plataforma <- renderPlotly({
    gf() %>% count(platform, sort = TRUE) %>%
      mutate(pct = round(n/sum(n)*100, 1)) %>%
      plot_ly(x = ~n, y = ~reorder(platform, n), type = "bar",
              orientation = "h",
              marker = list(color = ~n,
                            colorscale = list(c(0, PS_LIGHT), c(1, PS_BLUE)),
                            showscale = FALSE),
              text  = ~paste0(comma(n), " (", pct, "%)"),
              hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
      layout(xaxis = list(title = "Juegos"), yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)",
             margin = list(l = 5, r = 10, t = 5, b = 30)) %>%
      config(displayModeBar = FALSE)
  })

  output$p_años <- renderPlotly({
    gf() %>% filter(!is.na(year)) %>%
      count(year, platform) %>%
      plot_ly(x = ~year, y = ~n, color = ~platform,
              colors = c("#001f5b","#003087","#0070CC","#93C6E0"),
              type = "bar",
              hovertemplate = "Año: %{x}<br>Juegos: %{y}<extra></extra>") %>%
      layout(barmode = "stack",
             xaxis = list(title = "Año", dtick = 1),
             yaxis = list(title = "Juegos lanzados"),
             legend = list(orientation = "h", y = -0.3),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_mapa_resumen <- renderPlotly({
    players %>% count(country, sort = TRUE) %>% slice_head(n = 10) %>%
      mutate(pct = round(n/N_PLAYERS*100, 1)) %>%
      plot_ly(x = ~n, y = ~reorder(country, n), type = "bar",
              orientation = "h",
              marker = list(color = ~n,
                            colorscale = list(c(0, "#c3e6cb"), c(1, "#155724")),
                            showscale = FALSE),
              text  = ~paste0(comma(n), " (", pct, "%)"),
              hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
      layout(xaxis = list(title = "Jugadores"), yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  # ── TAB 2: CATÁLOGO ─────────────────────────────────────────
  output$cat_total   <- renderValueBox(
    valueBox(comma(nrow(gf())), "Juegos", icon = icon("gamepad"), color = "blue"))
  output$cat_plats   <- renderValueBox(
    valueBox(n_distinct(gf()$platform), "Plataformas",
             icon = icon("desktop"), color = "teal"))
  output$cat_generos <- renderValueBox({
    n <- gf() %>%
      filter(genres_clean != "") %>%
      separate_rows(genres_clean, sep = ",\\s*") %>%
      filter(genres_clean != "") %>%
      pull(genres_clean) %>% n_distinct()
    valueBox(n, "Géneros únicos", icon = icon("tags"), color = "purple")
  })

  output$p_generos <- renderPlotly({
    gf() %>%
      filter(genres_clean != "") %>%
      separate_rows(genres_clean, sep = ",\\s*") %>%
      filter(genres_clean != "") %>%
      count(genres_clean, sort = TRUE) %>%
      slice_head(n = input$sl_ngen) %>%
      plot_ly(x = ~n, y = ~reorder(genres_clean, n), type = "bar",
              orientation = "h",
              marker = list(color = ~n,
                            colorscale = list(c(0, PS_LIGHT), c(1, PS_BLUE)),
                            showscale = FALSE),
              hovertemplate = "<b>%{y}</b><br>%{x:,} juegos<extra></extra>") %>%
      layout(xaxis = list(title = "Juegos"), yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_publishers <- renderPlotly({
    gf() %>%
      filter(publishers_clean != "") %>%
      separate_rows(publishers_clean, sep = ",\\s*") %>%
      filter(publishers_clean != "") %>%
      count(publishers_clean, sort = TRUE) %>%
      slice_head(n = 10) %>%
      plot_ly(x = ~n, y = ~reorder(publishers_clean, n), type = "bar",
              orientation = "h",
              marker = list(color = PS_BLUE),
              hovertemplate = "<b>%{y}</b><br>%{x:,} juegos<extra></extra>") %>%
      layout(xaxis = list(title = "Juegos"), yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_precio_gen <- renderPlotly({
    precio_genero %>%
      slice_max(precio_prom, n = 10) %>%
      plot_ly(x = ~precio_prom, y = ~reorder(genres_clean, precio_prom),
              type = "bar", orientation = "h",
              marker = list(color = ~precio_prom,
                            colorscale = list(c(0, PS_LIGHT), c(1, PS_GOLD)),
                            showscale = FALSE),
              text  = ~paste0("$", round(precio_prom, 2), " — n=", comma(n)),
              hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
      layout(xaxis = list(title = "Precio promedio (USD)", tickprefix = "$"),
             yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$tabla_catalogo <- renderDT({
    gf() %>%
      select(gameid, title, platform, year, genres_clean, publishers_clean) %>%
      rename(ID = gameid, Título = title, Plataforma = platform,
             Año = year, Géneros = genres_clean, Publisher = publishers_clean)
  }, options = list(pageLength = 8, scrollX = TRUE,
                    language = list(search = "Buscar:")),
     rownames = FALSE)

  # ── TAB 3: JUGADORES ────────────────────────────────────────
  output$jug_total  <- renderValueBox(
    valueBox(comma(N_PLAYERS), "Jugadores registrados",
             icon = icon("users"), color = "purple"))
  output$jug_paises <- renderValueBox(
    valueBox(N_COUNTRIES, "Países", icon = icon("globe"), color = "teal"))
  output$jug_lider  <- renderValueBox({
    top <- players %>% count(country, sort = TRUE) %>% slice_head(n = 1)
    valueBox(top$country, paste0("País líder (", comma(top$n), ")"),
             icon = icon("flag"), color = "blue")
  })

  jug_filtrado <- reactive({
    df <- players
    if (input$dd_pais != "Todos") df <- df %>% filter(country == input$dd_pais)
    df %>% count(country, sort = TRUE) %>% slice_head(n = input$sl_top_paises)
  })

  output$p_paises <- renderPlotly({
    jug_filtrado() %>%
      mutate(pct = round(n/N_PLAYERS*100, 1)) %>%
      plot_ly(x = ~n, y = ~reorder(country, n), type = "bar",
              orientation = "h",
              marker = list(color = ~n,
                            colorscale = list(c(0, "#c3e6cb"), c(1, "#155724")),
                            showscale = FALSE),
              text  = ~paste0(comma(n), " (", pct, "%)"),
              hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
      layout(xaxis = list(title = "Jugadores"), yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_burbuja_paises <- renderPlotly({
    players %>% count(country, sort = TRUE) %>%
      slice_head(n = 25) %>%
      mutate(rank = row_number()) %>%
      plot_ly(x = ~rank, y = ~n, type = "scatter", mode = "markers+text",
              text = ~country, textposition = "top center",
              marker = list(size = ~sqrt(n)*1.8, sizemode = "diameter",
                            color = ~n,
                            colorscale = list(c(0, PS_LIGHT), c(1, PS_BLUE)),
                            showscale = FALSE),
              hovertemplate = "<b>%{text}</b><br>%{y:,} jugadores<extra></extra>") %>%
      layout(xaxis = list(title = "Ranking del país", showgrid = FALSE),
             yaxis = list(title = "Jugadores"),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_pie_paises <- renderPlotly({
    top6 <- players %>% count(country, sort = TRUE) %>% slice_head(n = 6)
    otros <- tibble(country = "Otros", n = N_PLAYERS - sum(top6$n))
    bind_rows(top6, otros) %>%
      plot_ly(labels = ~country, values = ~n, type = "pie", hole = 0.42,
              marker = list(colors = c("#001f5b","#003087","#0055b3",
                                       "#0070CC","#4D9AC2","#93C6E0","#d0e8f5")),
              textinfo = "label+percent",
              hovertemplate = "<b>%{label}</b><br>%{value:,}<extra></extra>") %>%
      layout(showlegend = FALSE,
             paper_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  # ── TAB 4: PRECIOS ──────────────────────────────────────────
  output$pr_prom    <- renderValueBox(
    valueBox(dollar(round(mean(pf()$usd, na.rm = TRUE), 2)),
             "Precio promedio", icon = icon("chart-bar"), color = "blue"))
  output$pr_mediana <- renderValueBox(
    valueBox(dollar(round(median(pf()$usd, na.rm = TRUE), 2)),
             "Precio mediana", icon = icon("dollar-sign"), color = "green"))
  output$pr_min     <- renderValueBox(
    valueBox(dollar(min(pf()$usd, na.rm = TRUE)),
             "Precio mínimo", icon = icon("arrow-down"), color = "teal"))
  output$pr_max     <- renderValueBox(
    valueBox(dollar(max(pf()$usd, na.rm = TRUE)),
             "Precio máximo", icon = icon("arrow-up"), color = "purple"))

  output$p_hist_precio <- renderPlotly({
    med_p  <- median(pf()$usd, na.rm = TRUE)
    prom_p <- mean(pf()$usd, na.rm = TRUE)
    pf() %>% filter(usd <= 70) %>%
      plot_ly(x = ~usd, type = "histogram", nbinsx = 30,
              marker = list(color = PS_BLUE,
                            line = list(color = "white", width = 0.7)),
              hovertemplate = "$%{x:.1f} — Frecuencia: %{y:,}<extra></extra>") %>%
      layout(
        xaxis  = list(title = "Precio (USD)", tickprefix = "$"),
        yaxis  = list(title = "Frecuencia"),
        shapes = list(
          list(type = "line", x0 = med_p, x1 = med_p, y0 = 0, y1 = 1,
               yref = "paper", line = list(color = PS_RED, dash = "dash", width = 2)),
          list(type = "line", x0 = prom_p, x1 = prom_p, y0 = 0, y1 = 1,
               yref = "paper", line = list(color = PS_GOLD, dash = "dot", width = 2))
        ),
        annotations = list(
          list(x = med_p, y = 0.92, yref = "paper",
               text = paste0("Mediana $", round(med_p, 2)),
               font = list(color = PS_RED), showarrow = FALSE, xanchor = "left"),
          list(x = prom_p, y = 0.80, yref = "paper",
               text = paste0("Prom. $", round(prom_p, 2)),
               font = list(color = PS_GOLD), showarrow = FALSE, xanchor = "left")
        ),
        paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)"
      ) %>%
      config(displayModeBar = FALSE)
  })

  output$p_rangos <- renderPlotly({
    pf() %>%
      mutate(rango = factor(case_when(
        usd <= 5  ~ "≤$5",  usd <= 20 ~ "$5–$20",
        usd <= 40 ~ "$20–$40", usd <= 70 ~ "$40–$70", TRUE ~ ">$70"),
        levels = c("≤$5","$5–$20","$20–$40","$40–$70",">$70"))) %>%
      count(rango) %>%
      mutate(pct = round(n/sum(n)*100, 1)) %>%
      plot_ly(x = ~rango, y = ~pct, type = "bar",
              marker = list(color = c("#001f5b","#003087","#0070CC","#4D9AC2","#93C6E0")),
              text  = ~paste0(pct, "%"), textposition = "outside",
              hovertemplate = "%{x}<br>%{y:.1f}% de juegos<extra></extra>") %>%
      layout(yaxis = list(title = "%", ticksuffix = "%"),
             xaxis = list(title = "Rango de precio"),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)",
             showlegend = FALSE) %>%
      config(displayModeBar = FALSE)
  })

  output$p_box_monedas <- renderPlotly({
    prices %>%
      select(usd, eur, gbp) %>%
      filter(if_all(everything(), ~!is.na(.)&.>0&.<80)) %>%
      pivot_longer(everything(), names_to = "Moneda", values_to = "Precio") %>%
      mutate(Moneda = toupper(Moneda)) %>%
      plot_ly(x = ~Moneda, y = ~Precio, type = "box", color = ~Moneda,
              colors = c("#003087","#0070CC","#93C6E0"),
              hovertemplate = "%{x}: %{y:.2f}<extra></extra>") %>%
      layout(showlegend = FALSE,
             xaxis = list(title = "Moneda"),
             yaxis = list(title = "Precio", tickprefix = "$"),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$p_correlacion <- renderPlotly({
    cor_data <- prices %>%
      select(usd, eur, gbp, jpy, rub) %>%
      filter(complete.cases(.))
    cor_mat  <- cor(cor_data)
    plot_ly(z = ~cor_mat,
            x = colnames(cor_mat),
            y = rownames(cor_mat),
            type = "heatmap",
            colorscale = list(c(0,"#93C6E0"), c(0.5,"white"), c(1, PS_BLUE)),
            zmin = -1, zmax = 1,
            text  = ~round(cor_mat, 2),
            hovertemplate = "%{y} vs %{x}<br>r = %{z:.2f}<extra></extra>") %>%
      layout(paper_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  # ── TAB 5: EXPLORADOR ───────────────────────────────────────
  datos_exp <- reactive({
    df <- games_prices
    if (input$exp_plat2 != "Todas") df <- df %>% filter(platform == input$exp_plat2)
    if (!is.null(input$exp_gen) && input$exp_gen != "Todos")
      df <- df %>% filter(str_detect(genres_clean, fixed(input$exp_gen, TRUE)))
    df %>% filter(usd >= input$exp_precio[1], usd <= input$exp_precio[2])
  })

  output$exp_scatter <- renderPlotly({
    datos_exp() %>%
      filter(!is.na(eur), eur > 0, eur < 100) %>%
      plot_ly(x = ~usd, y = ~eur, type = "scatter", mode = "markers",
              color = ~platform,
              colors = c("#001f5b","#003087","#0070CC","#93C6E0"),
              marker = list(size = 5, opacity = 0.5),
              text  = ~paste0("<b>", title, "</b><br>",
                              platform, "<br>USD $", usd, " | EUR €", eur),
              hovertemplate = "%{text}<extra></extra>") %>%
      layout(xaxis = list(title = "Precio USD", tickprefix = "$"),
             yaxis = list(title = "Precio EUR", tickprefix = "€"),
             legend = list(orientation = "h", y = -0.25),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$exp_gen_precio <- renderPlotly({
    datos_exp() %>%
      filter(genres_clean != "") %>%
      separate_rows(genres_clean, sep = ",\\s*") %>%
      filter(genres_clean != "") %>%
      group_by(genres_clean) %>%
      summarise(precio = mean(usd, na.rm = TRUE), n = n(), .groups = "drop") %>%
      filter(n >= 3) %>%
      slice_max(precio, n = 10) %>%
      plot_ly(x = ~precio, y = ~reorder(genres_clean, precio),
              type = "bar", orientation = "h",
              marker = list(color = PS_BLUE),
              hovertemplate = "<b>%{y}</b><br>$%{x:.2f}<extra></extra>") %>%
      layout(xaxis = list(title = "Precio promedio", tickprefix = "$"),
             yaxis = list(title = ""),
             paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)") %>%
      config(displayModeBar = FALSE)
  })

  output$exp_tabla <- renderDT({
    datos_exp() %>%
      select(title, platform, year, genres_clean, publishers_clean, usd, eur, gbp) %>%
      rename(Título = title, Plataforma = platform, Año = year,
             Géneros = genres_clean, Publisher = publishers_clean,
             USD = usd, EUR = eur, GBP = gbp)
  }, options = list(pageLength = 6, scrollX = TRUE,
                    language = list(search = "Buscar:")),
     rownames = FALSE)
}

shinyApp(ui = ui, server = server)
