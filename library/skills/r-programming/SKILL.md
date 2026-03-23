---
name: r-programming
description: R for statistical computing, data analysis, visualization with ggplot2, tidyverse, and Shiny applications
---

# R Programming

## Core Language
- Assignment: <- (preferred), =, ->
- Types: numeric, integer (1L), character, logical, complex
- Vectors: c(), seq(), rep(), vectorized operations
- Factors: factor(), levels, ordered factors for categorical data
- Lists: list(), named elements, nested structures
- Data frames: data.frame(), tibble() (tidyverse), column access $, [[]]
- Matrix: matrix(), nrow, ncol, array for higher dimensions
- Functions: function(args) { body }, default arguments, ... (dots)
- Control flow: if/else, for, while, repeat, break, next
- Apply family: sapply, lapply, mapply, tapply, vapply (type-safe)
- Environment and scoping: lexical scoping, parent environments

## Tidyverse
- dplyr: mutate, filter, select, arrange, group_by, summarize, across
- Pipe operator: |> (base R 4.1+) or %>% (magrittr)
- tidyr: pivot_longer, pivot_wider, separate, unite, unnest, fill
- stringr: str_detect, str_extract, str_replace, str_split
- forcats: fct_reorder, fct_collapse, fct_lump for factor manipulation
- purrr: map, map2, pmap, walk, safely, possibly (functional programming)
- readr: read_csv, read_tsv, write_csv (fast, type-inferring)
- lubridate: ymd, mdy, floor_date, interval, duration, period

## Data Visualization — ggplot2
- Grammar of Graphics: ggplot(data, aes(x, y)) + geom_*()
- Geoms: geom_point, geom_line, geom_bar, geom_histogram, geom_boxplot
- Aesthetics: color, fill, size, shape, alpha, group
- Faceting: facet_wrap(~var), facet_grid(row~col)
- Scales: scale_x_continuous, scale_color_manual, scale_fill_brewer
- Themes: theme_minimal(), theme_bw(), custom theme() modifications
- Labels: labs(title, subtitle, x, y, caption, color)
- Combined plots: patchwork package (p1 + p2), cowplot

## Statistical Analysis
- Descriptive: mean, median, sd, var, quantile, summary
- T-tests: t.test(x, y), paired, one-sample, confidence intervals
- ANOVA: aov(), TukeyHSD for post-hoc comparisons
- Linear regression: lm(y ~ x1 + x2, data), summary(), predict()
- Logistic regression: glm(y ~ x, family = binomial)
- Chi-squared: chisq.test() for categorical associations
- Correlation: cor(), cor.test(), correlation matrices
- Mixed models: lme4::lmer() for random effects

## Machine Learning in R
- caret or tidymodels for unified ML workflow
- tidymodels: recipe (preprocessing), parsnip (modeling), rsample (resampling), yardstick (metrics)
- Classification: random forest, logistic regression, SVM, XGBoost
- Cross-validation: vfold_cv, tune_grid
- Feature engineering: recipes::step_* functions

## R Markdown and Quarto
- R Markdown: YAML header, code chunks, inline R, knit to HTML/PDF/Word
- Quarto: next-gen, multi-language (.qmd), render to various formats
- Parameters: parameterized reports
- Chunk options: echo, eval, include, fig.width, fig.height, cache

## Shiny Applications
- UI: fluidPage, sidebarLayout, input*, output functions
- Server: render*, reactive(), observe(), eventReactive()
- Reactivity: reactive values, reactive expressions, observers
- Modules: modular UI and server components (ns = NS(id))
- Deployment: shinyapps.io, Posit Connect, Docker

## Package Development
- devtools: create, document, test, check, build
- roxygen2: #' comments for documentation
- testthat: test_that, expect_equal, expect_error, expect_true
- usethis: use_r, use_test, use_package, use_github_action

## Best Practices
- Use tidyverse for data manipulation over base R
- Pipe operations for readable transformation chains
- Avoid for loops when vectorized alternatives exist
- Use tibble over data.frame for consistent behavior
- Reproducibility: renv for dependency management, set.seed()
- Column-oriented thinking: operations on columns, not row-by-row
