# Análisis Exploratorio de Datos {#eda}

## Fundamentos del EDA

El EDA es un enfoque iterativo que examina **variación** (cómo cambian los valores de una misma variable) y **covariación** (cómo dos variables cambian conjuntamente). Técnicas utilizadas: estadísticas descriptivas, histogramas, boxplots, scatter plots con tendencias, matrices de correlación y faceting.



---

## Análisis univariado

### Distribución por plataforma


``` r
games %>%
  count(platform, sort = TRUE) %>%
  mutate(pct = round(n/sum(n)*100, 1)) %>%
  ggplot(aes(x = reorder(platform, n), y = n, fill = platform)) +
  geom_col(show.legend = FALSE, width = 0.6) +
  geom_text(aes(label = paste0(comma(n), " (", pct, "%)")), hjust = -0.05, size = 4) +
  coord_flip() +
  scale_y_continuous(expand = expansion(mult = c(0, 0.3)), labels = comma) +
  scale_fill_manual(values = c("#001f5b","#003087","#0070CC","#93C6E0")) +
  labs(title = "Juegos por plataforma PlayStation",
       subtitle = "PS4 domina con 61% del catálogo total", x = NULL, y = "Número de juegos") +
  theme_minimal(base_size = 13)
```

<div class="figure">
<img src="04-eda_files/figure-html/plataforma-1.png" alt="Distribución del catálogo por plataforma PlayStation" width="672" />
<p class="caption">(\#fig:plataforma)Distribución del catálogo por plataforma PlayStation</p>
</div>

**PS4:** 14.163 juegos (61%) | **PS5:** 6.422 (28%) | **Otras:** 11%.

### Estadísticas descriptivas globales de precios


``` r
prices_clean %>%
  summarise(N = comma(n()), Mínimo = dollar(min(usd)),
            `Q1 (25%)` = dollar(quantile(usd, 0.25)), Mediana = dollar(median(usd)),
            Media = dollar(round(mean(usd), 2)), `Q3 (75%)` = dollar(quantile(usd, 0.75)),
            Máximo = dollar(max(usd)), `Desv. Est.` = dollar(round(sd(usd), 2))) %>%
  pivot_longer(everything(), names_to = "Estadístico", values_to = "Valor") %>%
  kable(caption = "Estadísticas descriptivas del precio en USD") %>%
  kable_styling(bootstrap_options = c("striped","hover"), full_width = FALSE)
```

<table class="table table-striped table-hover" style="width: auto !important; margin-left: auto; margin-right: auto;">
<caption>(\#tab:stats-globales)(\#tab:stats-globales)Estadísticas descriptivas del precio en USD</caption>
 <thead>
  <tr>
   <th style="text-align:left;"> Estadístico </th>
   <th style="text-align:left;"> Valor </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> N </td>
   <td style="text-align:left;"> 49,251 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Mínimo </td>
   <td style="text-align:left;"> $0.02 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Q1 (25%) </td>
   <td style="text-align:left;"> $2.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Mediana </td>
   <td style="text-align:left;"> $7.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Media </td>
   <td style="text-align:left;"> $12.07 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Q3 (75%) </td>
   <td style="text-align:left;"> $17.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Máximo </td>
   <td style="text-align:left;"> $99.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Desv. Est. </td>
   <td style="text-align:left;"> $11.98 </td>
  </tr>
</tbody>
</table>

**Media ($12.07) > Mediana ($7.99):** distribución sesgada a la derecha. Mayoría de juegos baratos, minoría de títulos premium eleva el promedio.

### Histograma de precios


``` r
med_p  <- median(prices_clean$usd)
prom_p <- mean(prices_clean$usd)

prices_clean %>%
  filter(usd <= 75) %>%
  ggplot(aes(x = usd)) +
  geom_histogram(binwidth = 3, fill = "#003087", color = "white", alpha = 0.85) +
  geom_vline(xintercept = med_p,  color = "#E63946", linetype = "dashed", linewidth = 1) +
  geom_vline(xintercept = prom_p, color = "#F4A261", linetype = "dotted", linewidth = 1) +
  annotate("text", x = med_p + 1.5, y = Inf, vjust = 2,
           label = paste0("Mediana: $", round(med_p, 2)), color = "#E63946", size = 3.5, hjust = 0) +
  annotate("text", x = prom_p + 1.5, y = Inf, vjust = 4,
           label = paste0("Media: $", round(prom_p, 2)), color = "#F4A261", size = 3.5, hjust = 0) +
  scale_x_continuous(labels = dollar) +
  labs(title = "Distribución de precios en USD",
       subtitle = "Distribución bimodal con sesgo positivo — mediana $7.99, media $12.07",
       x = "Precio (USD)", y = "Frecuencia") +
  theme_minimal(base_size = 13)
```

<div class="figure">
<img src="04-eda_files/figure-html/hist-precio-1.png" alt="Distribución de precios USD — catálogo PlayStation 2025" width="672" />
<p class="caption">(\#fig:hist-precio)Distribución de precios USD — catálogo PlayStation 2025</p>
</div>

**Bimodalidad:** dos segmentos de mercado: indie barato (~$5) y estándar ($15–20). **~30%** de juegos en el rango $5–10.

---

## Análisis bivariado: Covariación género-precio

### Precio mediano por género — visión completa


``` r
generos_validos %>%
  mutate(grupo = case_when(
    precio_mediana >= 19.99 ~ "Alto (≥$20)",
    precio_mediana >= 9.99  ~ "Medio ($10–$19.99)",
    TRUE                    ~ "Bajo (<$10)"),
    grupo = factor(grupo, levels = c("Alto (≥$20)","Medio ($10–$19.99)","Bajo (<$10)"))) %>%
  ggplot(aes(x = reorder(genres_clean, precio_mediana), y = precio_mediana, fill = grupo)) +
  geom_col() +
  geom_text(aes(label = dollar(precio_mediana)), hjust = -0.1, size = 2.8) +
  coord_flip() +
  scale_y_continuous(expand = expansion(mult = c(0, 0.2)), labels = dollar) +
  scale_fill_manual(values = c("#001f5b","#0070CC","#93C6E0")) +
  labs(title = "Precio mediano por género en PlayStation",
       subtitle = "Diferencia de hasta 40x entre el género más caro y el más barato",
       x = NULL, y = "Precio mediano (USD)", fill = "Rango de precio") +
  theme_minimal(base_size = 11) + theme(legend.position = "bottom")
```

<div class="figure">
<img src="04-eda_files/figure-html/precio-genero-completo-1.png" alt="Precio mediano por género (≥50 juegos)" width="672" />
<p class="caption">(\#fig:precio-genero-completo)Precio mediano por género (≥50 juegos)</p>
</div>

**Hallazgo:** Diferencia de hasta **40 veces** entre el género más caro (*Simulation Racing*: $39.99) y el más barato (*Bowling*: $0.99).

### Top 8 géneros más caros vs. más baratos


``` r
top_caros   <- generos_validos %>% slice_max(precio_mediana, n = 8) %>% mutate(tipo = "Más caros")
top_baratos <- generos_validos %>% slice_min(precio_mediana, n = 8) %>% mutate(tipo = "Más baratos")

bind_rows(top_caros, top_baratos) %>%
  ggplot(aes(x = reorder(genres_clean, precio_mediana), y = precio_mediana, fill = tipo)) +
  geom_col(show.legend = FALSE) +
  geom_text(aes(label = dollar(precio_mediana)), hjust = -0.1, size = 3.5) +
  coord_flip() + facet_wrap(~tipo, scales = "free_y") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.25)), labels = dollar) +
  scale_fill_manual(values = c("#93C6E0","#001f5b")) +
  labs(title = "Géneros con mayor y menor precio mediano", x = NULL, y = "Precio mediano (USD)") +
  theme_minimal(base_size = 12)
```

<div class="figure">
<img src="04-eda_files/figure-html/top-caros-baratos-1.png" alt="Géneros extremos por precio mediano" width="672" />
<p class="caption">(\#fig:top-caros-baratos)Géneros extremos por precio mediano</p>
</div>

- **Más caros:** Simulation Racing ($39.99), Open World ($24.99), Action Horror ($24.99) — experiencias largas, alta producción.
- **Más baratos:** Bowling ($0.99), Pinball ($1.99), Educational & Trivia ($2.49) — alta penetración indie, sesiones cortas.

### Boxplot comparativo por género


``` r
generos_mostrar <- bind_rows(
  generos_validos %>% slice_max(precio_mediana, n = 12),
  generos_validos %>% slice_min(precio_mediana, n = 5)) %>% pull(genres_clean)

genres_long %>%
  filter(genres_clean %in% generos_mostrar, usd <= 75) %>%
  mutate(genres_clean = factor(genres_clean,
    levels = generos_validos %>% filter(genres_clean %in% generos_mostrar) %>%
      arrange(precio_mediana) %>% pull(genres_clean))) %>%
  ggplot(aes(x = genres_clean, y = usd, fill = genres_clean)) +
  geom_boxplot(show.legend = FALSE, outlier.alpha = 0.2, outlier.size = 0.8) +
  coord_flip() + scale_y_continuous(labels = dollar) +
  scale_fill_manual(values = colorRampPalette(c("#93C6E0","#001f5b"))(length(generos_mostrar))) +
  labs(title = "Distribución de precios por género",
       subtitle = "Géneros de nicho: menor variabilidad | Géneros masivos: mayor dispersión",
       x = NULL, y = "Precio (USD)") +
  theme_minimal(base_size = 11)
```

<div class="figure">
<img src="04-eda_files/figure-html/boxplot-generos-1.png" alt="Distribución de precios por género (top 12 caros + 5 baratos)" width="672" />
<p class="caption">(\#fig:boxplot-generos)Distribución de precios por género (top 12 caros + 5 baratos)</p>
</div>

- **Géneros premium** (Racing, Open World): medianas altas, cajas amplias (títulos variados).
- **Géneros masivos** (Action, Puzzle): medianas bajas, outliers hasta $50+ (confirma **H2**).
- **Géneros de nicho** (Racing Simulator, Fighting): cajas compactas — estrategia de precio homogénea.

### Relación volumen de juegos vs. precio mediano


``` r
generos_validos %>%
  ggplot(aes(x = n, y = precio_mediana, label = genres_clean)) +
  geom_point(aes(size = precio_sd, color = precio_mediana), alpha = 0.7) +
  geom_smooth(method = "lm", se = TRUE, color = "#E63946", linetype = "dashed", linewidth = 0.8) +
  ggrepel::geom_text_repel(data = . %>% filter(n > 500 | precio_mediana > 19), size = 2.8, max.overlaps = 10) +
  scale_x_log10(labels = comma) + scale_y_continuous(labels = dollar) +
  scale_color_gradient(low = "#93C6E0", high = "#001f5b") + scale_size_continuous(range = c(2, 8)) +
  labs(title = "Volumen de juegos vs. precio mediano por género",
       subtitle = "A mayor oferta de juegos, menor precio mediano",
       x = "Número de juegos (escala log)", y = "Precio mediano (USD)",
       color = "Precio\nmediano", size = "Desv.\nestándar") +
  theme_minimal(base_size = 12)
```

```
## `geom_smooth()` using formula = 'y ~ x'
```

```
## Warning: The following aesthetics were dropped during statistical transformation: label.
## ℹ This can happen when ggplot fails to infer the correct grouping structure in
##   the data.
## ℹ Did you forget to specify a `group` aesthetic or to convert a numerical
##   variable into a factor?
```

<div class="figure">
<img src="04-eda_files/figure-html/volumen-precio-1.png" alt="Saturación de mercado por género" width="672" />
<p class="caption">(\#fig:volumen-precio)Saturación de mercado por género</p>
</div>

**Tendencia negativa:** géneros con miles de títulos (Action, Puzzle, Platformer) tienen precios bajos; géneros con <200 títulos (Simulation Racing, Open World) tienen precios altos — consistente con teoría económica.

### Covariación Género × Plataforma (PS4 vs PS5)


``` r
top_gen_analisis <- generos_validos %>% slice_max(precio_mediana, n = 14) %>% pull(genres_clean)

genres_long %>%
  filter(genres_clean %in% top_gen_analisis, platform %in% c("PS4","PS5")) %>%
  group_by(genres_clean, platform) %>%
  summarise(mediana = median(usd, na.rm = TRUE), n = n(), .groups = "drop") %>%
  filter(n >= 10) %>%
  ggplot(aes(x = reorder(genres_clean, mediana), y = mediana, fill = platform)) +
  geom_col(position = "dodge") + coord_flip() +
  scale_y_continuous(labels = dollar) +
  scale_fill_manual(values = c("#003087","#0070CC")) +
  labs(title = "Precio mediano por género: PS4 vs PS5",
       subtitle = "PS5 tiende a precios más altos en géneros de experiencias largas",
       x = NULL, y = "Precio mediano (USD)", fill = "Plataforma") +
  theme_minimal(base_size = 12) + theme(legend.position = "bottom")
```

<div class="figure">
<img src="04-eda_files/figure-html/genero-plataforma-1.png" alt="Precio mediano por género: PS4 vs PS5" width="672" />
<p class="caption">(\#fig:genero-plataforma)Precio mediano por género: PS4 vs PS5</p>
</div>

**PS5 supera o iguala a PS4** en la mayoría de géneros premium, especialmente Role Playing, Open World y Action-RPG — confirma **H3**.

---

## Correlación entre monedas


``` r
cor_data <- read_csv("../../data/prices.csv", show_col_types = FALSE) %>%
  select(usd, eur, gbp, jpy, rub) %>% filter(complete.cases(.))

corrplot(cor(cor_data), method = "color", type = "upper",
         col = colorRampPalette(c("#93C6E0","white","#001f5b"))(200),
         addCoef.col = "black", number.cex = 0.85, tl.col = "black", tl.srt = 45,
         title = "Correlación entre monedas de precio", mar = c(0,0,2,0))
```

<div class="figure">
<img src="04-eda_files/figure-html/correlacion-monedas-1.png" alt="Matriz de correlación entre monedas" width="672" />
<p class="caption">(\#fig:correlacion-monedas)Matriz de correlación entre monedas</p>
</div>

**USD/EUR/GBP:** correlación perfecta (r = 1.00) — conversión automática. **JPY/RUB:** correlación ~0.95 con mayor variabilidad por ajustes de mercado regional.

---

## Síntesis del EDA


``` r
tibble(
  Pregunta = c("¿Hay relación género-precio?","¿Géneros más caros?","¿Géneros más baratos?",
               "¿Diferencia PS4 vs PS5?","¿Géneros masivos más baratos?","¿Paridad entre monedas?"),
  `Hallazgo EDA` = c(
    "Sí — diferencia de hasta 40x entre géneros",
    "Simulation Racing ($39.99), Open World ($24.99), Action Horror ($24.99)",
    "Bowling ($0.99), Pinball ($1.99), Educational & Trivia ($2.49)",
    "Sí — PS5 tiende a precios más altos en géneros premium",
    "Sí — correlación negativa: más volumen = precios más bajos",
    "USD/EUR/GBP r=1.00; JPY/RUB más variables"),
  `Tipo de análisis` = c("Covariación género-precio","Tendencia central por género",
    "Tendencia central por género","Covariación género-plataforma",
    "Relación volumen-precio","Correlación multivariada")
) %>%
  kable(caption = "Síntesis de hallazgos del EDA") %>%
  kable_styling(bootstrap_options = c("striped","hover"), full_width = TRUE) %>%
  column_spec(1, bold = TRUE, width = "25%") %>% column_spec(3, width = "25%", italic = TRUE)
```

<table class="table table-striped table-hover" style="margin-left: auto; margin-right: auto;">
<caption>(\#tab:tabla-sintesis)(\#tab:tabla-sintesis)Síntesis de hallazgos del EDA</caption>
 <thead>
  <tr>
   <th style="text-align:left;"> Pregunta </th>
   <th style="text-align:left;"> Hallazgo EDA </th>
   <th style="text-align:left;"> Tipo de análisis </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Hay relación género-precio? </td>
   <td style="text-align:left;"> Sí — diferencia de hasta 40x entre géneros </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Covariación género-precio </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Géneros más caros? </td>
   <td style="text-align:left;"> Simulation Racing ($39.99), Open World ($24.99), Action Horror ($24.99) </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Tendencia central por género </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Géneros más baratos? </td>
   <td style="text-align:left;"> Bowling ($0.99), Pinball ($1.99), Educational &amp; Trivia ($2.49) </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Tendencia central por género </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Diferencia PS4 vs PS5? </td>
   <td style="text-align:left;"> Sí — PS5 tiende a precios más altos en géneros premium </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Covariación género-plataforma </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Géneros masivos más baratos? </td>
   <td style="text-align:left;"> Sí — correlación negativa: más volumen = precios más bajos </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Relación volumen-precio </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 25%; font-weight: bold;"> ¿Paridad entre monedas? </td>
   <td style="text-align:left;"> USD/EUR/GBP r=1.00; JPY/RUB más variables </td>
   <td style="text-align:left;width: 25%; font-style: italic;"> Correlación multivariada </td>
  </tr>
</tbody>
</table>

**Conclusiones clave:** El género explica más varianza de precio que la plataforma. La distribución bimodal refleja dos segmentos (indie ~$5 vs. estándar $15–20). El análisis PS4/PS5 confirma diferenciación por generación, pero el género sigue siendo el eje principal.

<!--chapter:end:04-eda.Rmd-->
