"""
╔══════════════════════════════════════════════════════════════╗
║  🎮 PlayStation Gaming Analytics 2025 — Python / Dash       ║
║  Alex Terán · Ciencia de Datos · Grupo 13                   ║
║                                                              ║
║  Instalación:                                                ║
║    pip install dash dash-bootstrap-components pandas plotly  ║
║                                                              ║
║  Ejecución:                                                  ║
║    python app.py  →  http://127.0.0.1:8050                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import dash
from dash import dcc, html, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ════════════════════════════════════════════════════════════════
# PALETA Y TEMA
# ════════════════════════════════════════════════════════════════
PS_BLUE  = "#003087"
PS_RED   = "#E63946"
PS_LIGHT = "#A8DADC"
PS_DARK  = "#001A52"
PS_GOLD  = "#F4A261"
PS_BG    = "#F0F4FF"

COLORS = [PS_BLUE, "#0055b3", "#0070CC", PS_LIGHT,
          "#4D9AC2", "#93C6E0", PS_GOLD, PS_RED]

TEMPLATE = dict(layout=dict(
    font=dict(family="Segoe UI, Arial, sans-serif", size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    title=dict(font=dict(color=PS_BLUE, size=14)),
    xaxis=dict(gridcolor="#e0e8ff", linecolor="#ccc", showgrid=True),
    yaxis=dict(gridcolor="#e0e8ff", linecolor="#ccc", showgrid=True),
    colorway=COLORS
))

# ════════════════════════════════════════════════════════════════
# CARGA Y PREPARACIÓN DE DATOS
# ════════════════════════════════════════════════════════════════
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load():
    g  = pd.read_csv(f"{DATA}/games.csv",   low_memory=False)
    pl = pd.read_csv(f"{DATA}/players.csv", low_memory=False)
    pr = pd.read_csv(f"{DATA}/prices.csv",  low_memory=False)

    for df in (g, pl, pr):
        df.columns = df.columns.str.lower().str.strip()

    # Limpieza games
    g["release_date"]  = pd.to_datetime(g["release_date"], errors="coerce")
    g["year"]          = g["release_date"].dt.year
    g["genres_clean"]  = g["genres"].fillna("").str.replace(r"[\[\]']", "", regex=True)
    g["pub_clean"]     = g["publishers"].fillna("").str.replace(r"[\[\]']", "", regex=True)
    g = g.drop_duplicates()

    # Limpieza players
    pl = pl.dropna(subset=["country"]).drop_duplicates()
    pl["country"] = pl["country"].str.strip()

    # Limpieza prices
    pr = pr[(pr["usd"].notna()) & (pr["usd"] > 0) & (pr["usd"] < 150)]
    pr["date_acquired"] = pd.to_datetime(pr["date_acquired"], errors="coerce")
    pr = pr.drop_duplicates()

    # Géneros expandidos
    g_exp = g[g["genres_clean"] != ""].copy()
    g_exp = g_exp.assign(genre=g_exp["genres_clean"].str.split(",")) \
                 .explode("genre")
    g_exp["genre"] = g_exp["genre"].str.strip()
    g_exp = g_exp[g_exp["genre"] != ""]

    # Precio por género
    gp = g.merge(pr[["gameid","usd"]], on="gameid", how="inner")
    gp_exp = gp.assign(genre=gp["genres_clean"].str.split(",")).explode("genre")
    gp_exp["genre"] = gp_exp["genre"].str.strip()
    gp_exp = gp_exp[gp_exp["genre"] != ""]
    precio_gen = (gp_exp.groupby("genre")["usd"]
                  .agg(["mean","count"])
                  .reset_index()
                  .rename(columns={"mean":"precio_prom","count":"n"})
                  .query("n >= 15"))

    return g, pl, pr, g_exp, precio_gen

games, players, prices, genres_exp, precio_genero = load()

N_GAMES     = len(games)
N_PLAYERS   = len(players)
N_COUNTRIES = players["country"].nunique()
MED_PRICE   = prices["usd"].median()
PLATFORMS   = ["Todas"] + sorted(games["platform"].dropna().unique().tolist())
YEARS       = sorted(games["year"].dropna().unique().astype(int).tolist())
GENRES_LIST = sorted(genres_exp["genre"].dropna().unique().tolist())

# ════════════════════════════════════════════════════════════════
# HELPERS UI
# ════════════════════════════════════════════════════════════════
def kpi_card(titulo, valor, emoji, color):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(emoji, style={"fontSize":"2rem"}),
                html.Div([
                    html.P(titulo.upper(), className="mb-0 text-muted",
                           style={"fontSize":"0.72rem","fontWeight":700}),
                    html.H3(valor, className="mb-0 fw-bold",
                            style={"color":color,"fontSize":"1.75rem"})
                ], className="ms-3")
            ], className="d-flex align-items-center")
        ]),
        className="shadow-sm border-0 mb-3",
        style={"borderLeft":f"4px solid {color}","borderRadius":"10px","background":"white"}
    )

def insight_card(emoji, titulo, texto):
    return dbc.Alert([
        html.Strong(f"{emoji} {titulo}: "),
        texto
    ], color="info",
       style={"fontSize":"0.86rem","borderRadius":"8px","padding":"8px 12px",
              "marginBottom":"8px","borderLeft":f"4px solid {PS_BLUE}"})

def card_graph(title, graph_id, height="360px", **kwargs):
    return dbc.Card([
        dbc.CardHeader(html.B(title),
                       style={"backgroundColor":PS_BLUE,"color":"white",
                              "padding":"8px 15px","fontSize":"0.9rem"}),
        dbc.CardBody(dcc.Graph(id=graph_id, style={"height":height},
                               config={"displayModeBar":False}),
                     style={"padding":"10px"})
    ], className="shadow-sm border-0 mb-3",
       style={"borderRadius":"10px"})

# ════════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════════
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    title="PlayStation Analytics · Alex Terán",
    suppress_callback_exceptions=True
)

# ════════════════════════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════════════════════════
navbar = dbc.Navbar(
    dbc.Container([
        html.Span("🎮 ", style={"fontSize":"1.6rem"}),
        dbc.NavbarBrand("PlayStation Analytics 2025",
                        style={"color":"white","fontWeight":"bold","fontSize":"1.2rem"}),
        html.Small(" · Alex Terán · Ciencia de Datos · Grupo 13",
                   style={"color":PS_LIGHT,"fontSize":"0.8rem","marginLeft":"8px"})
    ], fluid=True),
    color=PS_DARK, dark=True,
    style={"boxShadow":"0 2px 10px rgba(0,0,0,.4)","padding":"8px 20px"}
)

# Filtros globales (sidebar)
filtros = dbc.Card([
    dbc.CardHeader(html.B("⚙️ Filtros globales"),
                   style={"backgroundColor":PS_DARK,"color":"white","fontSize":"0.85rem"}),
    dbc.CardBody([
        html.Label("Plataforma", className="fw-semibold small"),
        dcc.Dropdown(id="f-plat",
                     options=[{"label":p,"value":p} for p in PLATFORMS],
                     value="Todas", clearable=False),
        html.Br(),
        html.Label("Año de lanzamiento", className="fw-semibold small"),
        dcc.RangeSlider(id="f-year", min=2010, max=2024,
                        value=[2015, 2024], step=1,
                        marks={y:{"label":str(y),
                                  "style":{"fontSize":"10px"}}
                               for y in range(2010,2025,2)},
                        tooltip={"placement":"bottom","always_visible":False})
    ], style={"padding":"12px"})
], className="shadow-sm border-0 mb-3",
   style={"borderRadius":"10px"})

tabs_main = dbc.Tabs([
    dbc.Tab(label="🏠 Resumen",    tab_id="t-resumen",    label_style={"fontSize":"0.9rem"}),
    dbc.Tab(label="🎮 Catálogo",   tab_id="t-catalogo",   label_style={"fontSize":"0.9rem"}),
    dbc.Tab(label="👥 Jugadores",  tab_id="t-jugadores",  label_style={"fontSize":"0.9rem"}),
    dbc.Tab(label="💰 Precios",    tab_id="t-precios",    label_style={"fontSize":"0.9rem"}),
    dbc.Tab(label="🔍 Explorador", tab_id="t-explorador", label_style={"fontSize":"0.9rem"}),
], id="tabs", active_tab="t-resumen",
   style={"borderBottom":f"3px solid {PS_BLUE}"})

app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col(filtros, md=2, className="pt-3"),
        dbc.Col([
            html.Div(className="pt-3"),
            tabs_main,
            html.Div(id="content", className="mt-3")
        ], md=10)
    ])
], fluid=True, style={"background":PS_BG,"minHeight":"100vh",
                       "fontFamily":"Segoe UI, Arial, sans-serif"})

# ════════════════════════════════════════════════════════════════
# LAYOUTS POR PESTAÑA
# ════════════════════════════════════════════════════════════════
def lay_resumen():
    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card("Juegos en catálogo", f"{N_GAMES:,}",   "🎮", PS_BLUE),  md=3),
            dbc.Col(kpi_card("Jugadores",          f"{N_PLAYERS:,}", "👥", "#6A0DAD"),md=3),
            dbc.Col(kpi_card("Países",             str(N_COUNTRIES), "🌍", "#2ecc71"),md=3),
            dbc.Col(kpi_card("Precio mediano",     f"${MED_PRICE:.2f}", "💰", PS_RED), md=3),
        ]),
        dbc.Row([
            dbc.Col(card_graph("🎮 Juegos por plataforma", "g-plat", "280px"), md=5),
            dbc.Col(card_graph("📈 Lanzamientos por año y plataforma", "g-años", "280px"), md=7),
        ]),
        dbc.Row([
            dbc.Col(card_graph("🌍 Top 10 países (jugadores)", "g-mapa", "280px"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.B("💡 Insights clave del análisis"),
                               style={"backgroundColor":PS_GOLD,"color":PS_DARK,"fontSize":"0.9rem"}),
                dbc.CardBody([
                    insight_card("📌","PS4 sigue dominando",
                        "Con 14.163 juegos (61% del catálogo), PS4 supera a PS5 a pesar de llevar 4+ años en el mercado."),
                    insight_card("📌","Crecimiento explosivo",
                        "Los lanzamientos crecieron un 1.570% en una década: de 305 en 2013 a 5.091 en 2024."),
                    insight_card("📌","Mercado ultra-accesible",
                        "El 86% de los juegos cuesta menos de $20. Mediana: $7.99. PlayStation apuesta por volumen."),
                    insight_card("📌","EE.UU. + Europa concentran el 59%",
                        "Los 6 principales países representan más de la mitad de toda la base de usuarios global."),
                    insight_card("📌","El indie mueve el catálogo",
                        "Los 3 publishers más activos (eastasiasoft, Ratalaika, ThiGames) son indies de alto volumen."),
                ])
            ], className="shadow-sm border-0 mb-3",
               style={"borderRadius":"10px"}), md=6),
        ])
    ])

def lay_catalogo():
    return html.Div([
        html.Div(id="kpis-catalogo"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.B("⚙️ Top N géneros"),
                                   style={"backgroundColor":PS_BLUE,"color":"white"}),
                    dbc.CardBody([
                        dcc.Slider(id="sl-gen", min=5, max=20, step=1, value=12,
                                   marks={i:str(i) for i in range(5,21,5)},
                                   tooltip={"always_visible":False}),
                        dcc.Graph(id="g-gen", style={"height":"340px"},
                                  config={"displayModeBar":False})
                    ])
                ], className="shadow-sm border-0 mb-3", style={"borderRadius":"10px"})
            ], md=6),
            dbc.Col(card_graph("🏢 Top 10 publishers", "g-pub", "400px"), md=6),
        ]),
        card_graph("💰 Top 10 géneros por precio promedio (USD)", "g-precio-gen", "280px"),
        dbc.Card([
            dbc.CardHeader(html.B("📋 Catálogo de juegos"),
                           style={"backgroundColor":PS_BLUE,"color":"white"}),
            dbc.CardBody([
                dash_table.DataTable(
                    id="tabla-cat",
                    page_size=8, filter_action="native", sort_action="native",
                    style_header={"backgroundColor":PS_BLUE,"color":"white","fontWeight":"bold"},
                    style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#eef2ff"}],
                    style_table={"overflowX":"auto"},
                    style_cell={"fontSize":"12px","padding":"6px 10px"}
                )
            ])
        ], className="shadow-sm border-0 mb-3", style={"borderRadius":"10px"})
    ])

def lay_jugadores():
    paises = ["Todos"] + sorted(players["country"].dropna().unique().tolist())
    return html.Div([
        html.Div(id="kpis-jug"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.B("⚙️ Filtros"),
                               style={"backgroundColor":"#856404","color":"white"}),
                dbc.CardBody([
                    html.Label("País:", className="fw-semibold small"),
                    dcc.Dropdown(id="dd-pais",
                                 options=[{"label":p,"value":p} for p in paises],
                                 value="Todos", clearable=False),
                    html.Br(),
                    html.Label("Top N países:", className="fw-semibold small"),
                    dcc.Slider(id="sl-paises", min=5, max=30, step=5, value=15,
                               marks={i:str(i) for i in [5,10,15,20,25,30]},
                               tooltip={"always_visible":False})
                ])
            ], className="shadow-sm border-0 mb-3", style={"borderRadius":"10px"}), md=3),
            dbc.Col(card_graph("🌍 Jugadores por país", "g-paises", "420px"), md=9),
        ]),
        dbc.Row([
            dbc.Col(card_graph("🫧 Concentración geográfica (burbuja)", "g-burbuja", "340px"), md=8),
            dbc.Col(card_graph("🥧 Top 6 países (proporción)", "g-pie-paises", "340px"), md=4),
        ])
    ])

def lay_precios():
    return html.Div([
        html.Div(id="kpis-precio"),
        dbc.Row([
            dbc.Col(card_graph("📊 Distribución de precios (USD)", "g-hist", "340px"), md=7),
            dbc.Col(card_graph("📦 Rangos de precio", "g-rangos", "340px"), md=5),
        ]),
        dbc.Row([
            dbc.Col(card_graph("🔀 Precios por moneda (boxplot)", "g-box-monedas", "300px"), md=6),
            dbc.Col(card_graph("🔗 Correlación entre monedas", "g-corr", "300px"), md=6),
        ])
    ])

def lay_explorador():
    return html.Div([
        dbc.Card([
            dbc.CardHeader(html.B("🔎 Filtros de búsqueda"),
                           style={"backgroundColor":"#856404","color":"white"}),
            dbc.CardBody(dbc.Row([
                dbc.Col([
                    html.Label("Precio USD:", className="fw-semibold small"),
                    dcc.RangeSlider(id="exp-precio", min=0, max=100,
                                    value=[0,60], step=1,
                                    marks={0:"$0",20:"$20",40:"$40",60:"$60",
                                           80:"$80",100:"$100"},
                                    tooltip={"always_visible":False})
                ], md=4),
                dbc.Col([
                    html.Label("Plataforma:", className="fw-semibold small"),
                    dcc.Dropdown(id="exp-plat",
                                 options=[{"label":p,"value":p} for p in PLATFORMS],
                                 value="Todas", clearable=False)
                ], md=4),
                dbc.Col([
                    html.Label("Género:", className="fw-semibold small"),
                    dcc.Dropdown(id="exp-gen",
                                 options=[{"label":g,"value":g}
                                          for g in ["Todos"]+GENRES_LIST],
                                 value="Todos", clearable=False)
                ], md=4),
            ]))
        ], className="shadow-sm border-0 mb-3", style={"borderRadius":"10px"}),

        dbc.Row([
            dbc.Col(card_graph("💎 USD vs EUR — dispersión por juego", "exp-scatter", "360px"), md=7),
            dbc.Col(card_graph("📊 Precio por género (filtrado)", "exp-gen-precio", "360px"), md=5),
        ]),
        dbc.Card([
            dbc.CardHeader(html.B("📋 Resultados filtrados"),
                           style={"backgroundColor":PS_BLUE,"color":"white"}),
            dbc.CardBody(dash_table.DataTable(
                id="exp-tabla",
                page_size=8, filter_action="native", sort_action="native",
                export_format="csv",
                style_header={"backgroundColor":PS_BLUE,"color":"white","fontWeight":"bold"},
                style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#eef2ff"}],
                style_table={"overflowX":"auto"},
                style_cell={"fontSize":"12px","padding":"6px 10px"}
            ))
        ], className="shadow-sm border-0", style={"borderRadius":"10px"})
    ])

# ════════════════════════════════════════════════════════════════
# CALLBACKS
# ════════════════════════════════════════════════════════════════

@app.callback(Output("content","children"),
              Input("tabs","active_tab"))
def render_tab(tab):
    if tab == "t-resumen":    return lay_resumen()
    if tab == "t-catalogo":   return lay_catalogo()
    if tab == "t-jugadores":  return lay_jugadores()
    if tab == "t-precios":    return lay_precios()
    if tab == "t-explorador": return lay_explorador()

# ── Filtro datos con f-plat y f-year ────────────────────────────
def filter_games(plat, years):
    df = games.copy()
    if plat != "Todas": df = df[df["platform"] == plat]
    df = df[(df["year"] >= years[0]) & (df["year"] <= years[1])]
    return df

def filter_prices(plat):
    df = prices.copy()
    if plat != "Todas":
        ids = games[games["platform"] == plat]["gameid"].tolist()
        df  = df[df["gameid"].isin(ids)]
    return df

# ── TAB RESUMEN ─────────────────────────────────────────────────
@app.callback(
    [Output("g-plat","figure"), Output("g-años","figure"),
     Output("g-mapa","figure")],
    [Input("f-plat","value"), Input("f-year","value")],
    prevent_initial_call=False
)
def upd_resumen(plat, years):
    gf = filter_games(plat, years)

    # Plataforma
    df_plat = gf["platform"].value_counts().reset_index()
    df_plat.columns = ["platform","n"]
    df_plat["pct"] = (df_plat["n"]/len(gf)*100).round(1)
    fig_plat = px.bar(df_plat, x="n", y="platform", orientation="h",
                      color="n", color_continuous_scale=[PS_LIGHT, PS_BLUE],
                      text=df_plat.apply(lambda r: f"{r['n']:,} ({r['pct']}%)", axis=1))
    fig_plat.update_coloraxes(showscale=False)
    fig_plat.update_traces(textposition="outside")
    fig_plat.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Juegos", yaxis_title="",
                           margin=dict(l=0,r=30,t=10,b=10))

    # Años
    años = gf[gf["year"].notna()].groupby(["year","platform"]).size().reset_index(name="n")
    fig_años = px.bar(años, x="year", y="n", color="platform",
                      color_discrete_sequence=COLORS, barmode="stack")
    fig_años.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Año", yaxis_title="Juegos",
                           xaxis=dict(dtick=2),
                           legend=dict(orientation="h", y=-0.3),
                           margin=dict(t=10,b=40))

    # Mapa
    df_map = players["country"].value_counts().head(10).reset_index()
    df_map.columns = ["country","n"]
    df_map["pct"] = (df_map["n"]/N_PLAYERS*100).round(1)
    fig_map = px.bar(df_map, x="n", y="country", orientation="h",
                     color="n", color_continuous_scale=["#c3e6cb","#155724"],
                     text=df_map.apply(lambda r: f"{r['n']:,} ({r['pct']}%)", axis=1))
    fig_map.update_coloraxes(showscale=False)
    fig_map.update_traces(textposition="outside")
    fig_map.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Jugadores", yaxis_title="",
                           margin=dict(l=0,r=80,t=10,b=10))

    return fig_plat, fig_años, fig_map

# ── TAB CATÁLOGO ────────────────────────────────────────────────
@app.callback(
    [Output("g-gen","figure"), Output("g-pub","figure"),
     Output("g-precio-gen","figure"), Output("tabla-cat","data"),
     Output("tabla-cat","columns"), Output("kpis-catalogo","children")],
    [Input("f-plat","value"), Input("f-year","value"),
     Input("sl-gen","value")],
    prevent_initial_call=False
)
def upd_catalogo(plat, years, n_gen):
    gf = filter_games(plat, years)

    # Géneros
    gexp = gf[gf["genres_clean"] != ""].copy()
    gexp = gexp.assign(g=gexp["genres_clean"].str.split(",")).explode("g")
    gexp["g"] = gexp["g"].str.strip()
    gexp = gexp[gexp["g"] != ""]
    top_gen = gexp["g"].value_counts().head(n_gen).reset_index()
    top_gen.columns = ["genre","n"]
    fig_gen = px.bar(top_gen, x="n", y="genre", orientation="h",
                     color="n", color_continuous_scale=[PS_LIGHT,PS_BLUE])
    fig_gen.update_coloraxes(showscale=False)
    fig_gen.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Juegos", yaxis_title="",
                           margin=dict(l=0,r=10,t=5,b=20))

    # Publishers
    pexp = gf[gf["pub_clean"] != ""].copy()
    pexp = pexp.assign(p=pexp["pub_clean"].str.split(",")).explode("p")
    pexp["p"] = pexp["p"].str.strip()
    pexp = pexp[pexp["p"] != ""]
    top_pub = pexp["p"].value_counts().head(10).reset_index()
    top_pub.columns = ["publisher","n"]
    fig_pub = px.bar(top_pub, x="n", y="publisher", orientation="h",
                     color_discrete_sequence=[PS_BLUE])
    fig_pub.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Juegos", yaxis_title="",
                           margin=dict(l=0,r=10,t=5,b=20))

    # Precio por género
    fig_pg = px.bar(precio_genero.nlargest(10,"precio_prom"),
                    x="precio_prom", y="genre", orientation="h",
                    color="precio_prom",
                    color_continuous_scale=[PS_LIGHT, PS_GOLD],
                    text=precio_genero.nlargest(10,"precio_prom")["precio_prom"]
                    .apply(lambda x: f"${x:.2f}"))
    fig_pg.update_coloraxes(showscale=False)
    fig_pg.update_traces(textposition="outside")
    fig_pg.update_layout(**TEMPLATE["layout"],
                          xaxis_title="Precio promedio (USD)", yaxis_title="",
                          margin=dict(l=0,r=60,t=5,b=20))

    # Tabla
    tabla = gf[["gameid","title","platform","year",
                "genres_clean","pub_clean"]].rename(columns={
        "gameid":"ID","title":"Título","platform":"Plataforma",
        "year":"Año","genres_clean":"Géneros","pub_clean":"Publisher"
    }).head(300)
    cols = [{"name":c,"id":c} for c in tabla.columns]

    # KPIs
    n_gen_u = gexp["g"].nunique()
    kpis = dbc.Row([
        dbc.Col(kpi_card("Juegos",       f"{len(gf):,}",   "🎮", PS_BLUE),  md=4),
        dbc.Col(kpi_card("Plataformas",  str(gf["platform"].nunique()), "💿", "#6A0DAD"), md=4),
        dbc.Col(kpi_card("Géneros únicos", str(n_gen_u), "🎭", "#2ecc71"), md=4),
    ])

    return fig_gen, fig_pub, fig_pg, tabla.to_dict("records"), cols, kpis

# ── TAB JUGADORES ───────────────────────────────────────────────
@app.callback(
    [Output("g-paises","figure"), Output("g-burbuja","figure"),
     Output("g-pie-paises","figure"), Output("kpis-jug","children")],
    [Input("dd-pais","value"), Input("sl-paises","value")],
    prevent_initial_call=False
)
def upd_jugadores(pais, n):
    df = players.copy()
    if pais != "Todos": df = df[df["country"] == pais]
    top = df["country"].value_counts().head(n).reset_index()
    top.columns = ["country","n"]
    top["pct"] = (top["n"]/N_PLAYERS*100).round(1)

    fig_bar = px.bar(top, x="n", y="country", orientation="h",
                     color="n", color_continuous_scale=["#c3e6cb","#155724"],
                     text=top.apply(lambda r: f"{r['n']:,} ({r['pct']}%)", axis=1))
    fig_bar.update_coloraxes(showscale=False)
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Jugadores", yaxis_title="",
                           margin=dict(l=0,r=100,t=10,b=20))

    # Burbuja
    bub = players["country"].value_counts().head(25).reset_index()
    bub.columns = ["country","n"]
    bub["rank"] = range(1, len(bub)+1)
    fig_bub = px.scatter(bub, x="rank", y="n", size="n",
                         color="n", text="country",
                         color_continuous_scale=[PS_LIGHT, PS_BLUE])
    fig_bub.update_traces(textposition="top center")
    fig_bub.update_coloraxes(showscale=False)
    fig_bub.update_layout(**TEMPLATE["layout"],
                           xaxis_title="Ranking", yaxis_title="Jugadores",
                           showlegend=False, margin=dict(t=10,b=20))

    # Pie
    top6 = players["country"].value_counts().head(6).reset_index()
    top6.columns = ["country","n"]
    otros = pd.DataFrame({"country":["Otros"],
                          "n":[N_PLAYERS-top6["n"].sum()]})
    pie_data = pd.concat([top6, otros])
    fig_pie = px.pie(pie_data, names="country", values="n",
                     hole=0.42, color_discrete_sequence=COLORS)
    fig_pie.update_layout(**TEMPLATE["layout"], showlegend=False,
                           margin=dict(t=10,b=10))

    top1 = players["country"].value_counts().index[0]
    top1_n = players["country"].value_counts().iloc[0]
    kpis = dbc.Row([
        dbc.Col(kpi_card("Jugadores",   f"{N_PLAYERS:,}", "👥", "#6A0DAD"), md=4),
        dbc.Col(kpi_card("Países",      str(N_COUNTRIES), "🌍", "#2ecc71"), md=4),
        dbc.Col(kpi_card(f"Líder: {top1}", f"{top1_n:,}", "🥇", PS_RED),   md=4),
    ])
    return fig_bar, fig_bub, fig_pie, kpis

# ── TAB PRECIOS ─────────────────────────────────────────────────
@app.callback(
    [Output("g-hist","figure"), Output("g-rangos","figure"),
     Output("g-box-monedas","figure"), Output("g-corr","figure"),
     Output("kpis-precio","children")],
    [Input("f-plat","value")],
    prevent_initial_call=False
)
def upd_precios(plat):
    pf = filter_prices(plat)

    med_p  = pf["usd"].median()
    prom_p = pf["usd"].mean()

    # Histograma
    fig_hist = px.histogram(pf[pf["usd"]<=70], x="usd", nbins=30,
                             color_discrete_sequence=[PS_BLUE])
    fig_hist.add_vline(x=med_p, line_dash="dash", line_color=PS_RED,
                       annotation_text=f"Mediana ${med_p:.2f}",
                       annotation_position="top right",
                       annotation_font_color=PS_RED)
    fig_hist.add_vline(x=prom_p, line_dash="dot", line_color=PS_GOLD,
                       annotation_text=f"Prom. ${prom_p:.2f}",
                       annotation_position="top left",
                       annotation_font_color=PS_GOLD)
    fig_hist.update_layout(**TEMPLATE["layout"],
                            xaxis_title="Precio (USD)", yaxis_title="Frecuencia",
                            margin=dict(t=10,b=30))

    # Rangos
    pf2 = pf.copy()
    pf2["rango"] = pd.cut(pf2["usd"], bins=[0,5,20,40,70,150],
                          labels=["≤$5","$5–$20","$20–$40","$40–$70",">$70"])
    rangos = pf2["rango"].value_counts().sort_index().reset_index()
    rangos.columns = ["rango","n"]
    rangos["pct"] = (rangos["n"]/len(pf2)*100).round(1)
    fig_rang = px.bar(rangos, x="rango", y="pct",
                      color="rango",
                      color_discrete_sequence=["#001f5b","#003087","#0070CC","#4D9AC2","#93C6E0"],
                      text=rangos["pct"].apply(lambda x: f"{x}%"))
    fig_rang.update_traces(textposition="outside")
    fig_rang.update_layout(**TEMPLATE["layout"],
                            showlegend=False,
                            xaxis_title="Rango", yaxis_title="%",
                            yaxis_ticksuffix="%",
                            margin=dict(t=10,b=30))

    # Boxplot monedas
    monedas = pf[["usd","eur","gbp"]].copy()
    monedas = monedas[(monedas>0).all(axis=1) & (monedas<80).all(axis=1)].dropna()
    mlong   = monedas.melt(var_name="Moneda", value_name="Precio")
    mlong["Moneda"] = mlong["Moneda"].str.upper()
    fig_box = px.box(mlong, x="Moneda", y="Precio", color="Moneda",
                     color_discrete_sequence=[PS_BLUE,"#0070CC","#93C6E0"])
    fig_box.update_layout(**TEMPLATE["layout"], showlegend=False,
                           xaxis_title="Moneda", yaxis_title="Precio (USD)",
                           margin=dict(t=10,b=30))

    # Correlación
    cor_df = pf[["usd","eur","gbp","jpy","rub"]].dropna()
    corr   = cor_df.corr()
    fig_corr = px.imshow(corr, text_auto=".2f",
                         color_continuous_scale=[PS_LIGHT,"white",PS_BLUE],
                         zmin=-1, zmax=1,
                         aspect="auto")
    fig_corr.update_layout(**TEMPLATE["layout"], margin=dict(t=10,b=10))

    kpis = dbc.Row([
        dbc.Col(kpi_card("Precio promedio", f"${pf['usd'].mean():.2f}", "📊", PS_BLUE), md=3),
        dbc.Col(kpi_card("Precio mediana",  f"${med_p:.2f}",            "💰", "#2ecc71"), md=3),
        dbc.Col(kpi_card("Precio mínimo",   f"${pf['usd'].min():.2f}",  "⬇️", "#6A0DAD"), md=3),
        dbc.Col(kpi_card("Precio máximo",   f"${pf['usd'].max():.2f}",  "⬆️", PS_RED),   md=3),
    ])
    return fig_hist, fig_rang, fig_box, fig_corr, kpis

# ── TAB EXPLORADOR ──────────────────────────────────────────────
@app.callback(
    [Output("exp-scatter","figure"), Output("exp-gen-precio","figure"),
     Output("exp-tabla","data"), Output("exp-tabla","columns")],
    [Input("exp-precio","value"), Input("exp-plat","value"),
     Input("exp-gen","value")],
    prevent_initial_call=False
)
def upd_explorador(rango, plat, gen):
    gp = games.merge(prices, on="gameid", how="inner")
    if plat != "Todas": gp = gp[gp["platform"] == plat]
    if gen and gen != "Todos":
        gp = gp[gp["genres_clean"].str.contains(gen, case=False, na=False)]
    gp = gp[(gp["usd"] >= rango[0]) & (gp["usd"] <= rango[1])]

    # Scatter
    gp_s = gp[gp["eur"].notna() & (gp["eur"]>0) & (gp["eur"]<100)]
    fig_sc = px.scatter(gp_s, x="usd", y="eur", color="platform",
                        color_discrete_sequence=COLORS,
                        hover_data={"title":True,"platform":True,"usd":True,"eur":True},
                        opacity=0.5)
    fig_sc.update_layout(**TEMPLATE["layout"],
                          xaxis_title="Precio USD", yaxis_title="Precio EUR",
                          legend=dict(orientation="h", y=-0.25),
                          margin=dict(t=10,b=50))

    # Precio por género
    gp_exp = gp.assign(g=gp["genres_clean"].str.split(",")).explode("g")
    gp_exp["g"] = gp_exp["g"].str.strip()
    gp_exp = gp_exp[gp_exp["g"] != ""]
    gp_agg = (gp_exp.groupby("g")["usd"]
              .agg(["mean","count"]).reset_index()
              .rename(columns={"mean":"precio","count":"n"})
              .query("n >= 3")
              .nlargest(10,"precio"))
    fig_pg = px.bar(gp_agg, x="precio", y="g", orientation="h",
                    color_discrete_sequence=[PS_BLUE],
                    text=gp_agg["precio"].apply(lambda x: f"${x:.2f}"))
    fig_pg.update_traces(textposition="outside")
    fig_pg.update_layout(**TEMPLATE["layout"],
                          xaxis_title="Precio prom. (USD)", yaxis_title="",
                          margin=dict(l=0,r=60,t=5,b=20))

    # Tabla
    tabla = gp[["title","platform","year","genres_clean","pub_clean",
                "usd","eur","gbp"]].rename(columns={
        "title":"Título","platform":"Plataforma","year":"Año",
        "genres_clean":"Géneros","pub_clean":"Publisher",
        "usd":"USD","eur":"EUR","gbp":"GBP"
    }).head(300)
    cols = [{"name":c,"id":c} for c in tabla.columns]
    return fig_sc, fig_pg, tabla.to_dict("records"), cols

# ════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n🎮 PlayStation Analytics — Alex Terán")
    print(f"   Juegos:    {N_GAMES:,}")
    print(f"   Jugadores: {N_PLAYERS:,}")
    print(f"   Países:    {N_COUNTRIES}")
    print(f"\n→ Abre: http://127.0.0.1:8050\n")
    app.run(debug=False, host="127.0.0.1", port=8050)
