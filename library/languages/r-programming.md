# R Quick Reference

## Language: R 4.3+
**Paradigm:** Functional, statistical computing  
**Typing:** Dynamic, vector-oriented  
**Runtime:** GNU R, also Microsoft R Open  

## Syntax Essentials

```r
name <- "Piddy"
nums <- c(1, 2, 3, 4, 5)

# Vectorized operations
nums * 2            # c(2, 4, 6, 8, 10)
sum(nums)           # 15
sqrt(nums)          # element-wise

# Indexing (1-based!)
nums[1]             # first element
nums[nums > 3]      # filter: c(4, 5)

# Data frame
df <- data.frame(name = c("A", "B"), age = c(30, 25))
df$name
subset(df, age > 28)
```

## Functions & Pipes

```r
add <- function(a, b = 0) { a + b }

# Apply family
sapply(nums, function(x) x^2)
lapply(list_of_dfs, nrow)

# Pipe (R 4.1+)
result <- nums |> sort() |> unique() |> head(5)

# Tidyverse pipe
library(dplyr)
result <- df %>%
  filter(age > 25) %>%
  arrange(desc(score)) %>%
  mutate(grade = ifelse(score > 90, "A", "B"))
```

## Tidyverse (Data Science Stack)

```r
library(tidyverse)

df %>%
  filter(year >= 2020) %>%
  group_by(category) %>%
  summarize(count = n(), avg = mean(price, na.rm=TRUE)) %>%
  arrange(desc(count))

# ggplot2
ggplot(df, aes(x=age, y=score, color=group)) +
  geom_point() + geom_smooth(method="lm") + theme_minimal()
```

## Tooling

```r
install.packages("package_name")
renv::init()
renv::snapshot()
testthat::test_dir("tests/")
```
