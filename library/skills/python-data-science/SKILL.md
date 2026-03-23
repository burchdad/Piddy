---
name: python-data-science
description: Python for data analysis, machine learning, deep learning with pandas, numpy, scikit-learn, PyTorch, and TensorFlow
---

# Python Data Science and ML

## NumPy
- ndarray: creation (np.array, zeros, ones, arange, linspace), dtype
- Indexing: basic, boolean masking, fancy indexing
- Operations: element-wise arithmetic, broadcasting rules
- Linear algebra: np.dot, @, np.linalg.inv/solve/eig/svd
- Reshaping: reshape, flatten, ravel, squeeze, expand_dims
- Aggregations: sum, mean, std, min, max along axes
- Random: np.random.default_rng(), normal, uniform, choice, shuffle

## Pandas
- DataFrame and Series: creation, indexing (loc/iloc), dtypes
- Reading data: read_csv, read_json, read_excel, read_sql, read_parquet
- Selection: df[col], df[[cols]], df.loc[rows, cols], df.query("expr")
- Filtering: boolean indexing, isin, between, str accessor methods
- Missing data: isna, dropna, fillna, interpolate
- GroupBy: groupby, agg (named aggregation), transform, apply
- Merging: merge (SQL-like joins), concat (stacking), join
- Pivot: pivot_table, melt (wide to long), stack/unstack
- Time series: pd.to_datetime, resample, rolling, shift, date_range
- String methods: df.col.str.contains/extract/replace/split
- Categorical data: pd.Categorical, cat accessor, memory efficiency
- Performance: vectorized operations over iterrows, eval/query for large DataFrames
- Writing: to_csv, to_parquet, to_sql, to_json

## Visualization
- Matplotlib: plt.figure, plt.plot/scatter/bar/hist, subplots, customization
- Seaborn: statistical plots, heatmap, pairplot, catplot, FacetGrid
- Plotly: interactive plots, px.scatter/line/bar, dash for dashboards

## Scikit-learn
- Pipeline: Pipeline, ColumnTransformer, make_pipeline
- Preprocessing: StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
- Feature engineering: PolynomialFeatures, SelectKBest, PCA
- Classification: LogisticRegression, RandomForestClassifier, SVC, GradientBoosting
- Regression: LinearRegression, Ridge, Lasso, RandomForestRegressor, XGBRegressor
- Clustering: KMeans, DBSCAN, AgglomerativeClustering
- Model selection: train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
- Metrics: accuracy, precision, recall, f1, confusion_matrix, roc_auc, MSE, R2
- Text: TfidfVectorizer, CountVectorizer

## Deep Learning — PyTorch
- Tensors: torch.tensor, device (cpu/cuda), dtype, requires_grad
- Autograd: backward(), grad, no_grad(), detach
- nn.Module: __init__ define layers, forward() define computation
- Common layers: Linear, Conv2d, LSTM, BatchNorm, Dropout, Embedding
- Loss functions: CrossEntropyLoss, MSELoss, BCEWithLogitsLoss
- Optimizers: Adam, SGD, AdamW, learning rate schedulers
- DataLoader: Dataset, DataLoader, batch_size, shuffle, num_workers
- Training loop: zero_grad → forward → loss → backward → step
- Save/load: torch.save(model.state_dict()), load_state_dict
- Transformers: torch.nn.Transformer, HuggingFace integration

## Deep Learning — TensorFlow/Keras
- Sequential and Functional API
- Layers: Dense, Conv2D, LSTM, Embedding, BatchNormalization, Dropout
- Compilation: model.compile(optimizer, loss, metrics)
- Training: model.fit, callbacks (EarlyStopping, ModelCheckpoint, TensorBoard)
- tf.data: from_tensor_slices, batch, shuffle, prefetch, map
- SavedModel: model.save(), tf.saved_model.load

## NLP
- Tokenization: word, subword (BPE, WordPiece), sentence
- HuggingFace Transformers: AutoModel, AutoTokenizer, pipeline()
- Fine-tuning: Trainer, TrainingArguments, datasets library
- Embeddings: Word2Vec, GloVe, sentence-transformers
- LangChain: chains, agents, retrievers, vector stores for LLM applications

## Best Practices
- Use virtual environments or conda for dependency isolation
- Reproducibility: random seeds, requirements.txt/pyproject.toml
- EDA before modeling: describe(), info(), value_counts(), visualize distributions
- Train/validation/test split — never leak test data into training
- Start simple: baseline model first, then increase complexity
- Log experiments: MLflow, Weights & Biases, or simple logging
- Use GPU when available: model.to('cuda'), mixed precision training
