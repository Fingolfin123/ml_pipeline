# 🧠 Features Module Checklist

This module contains logic for feature engineering, selection, and transformation to prepare raw data for modeling. Use this checklist to track what’s implemented and ensure reproducibility and modularity in the feature pipeline.

---

## 🏗️ Feature Engineering

- [ ] Create derived numerical features (e.g., ratios, differences, aggregations)
- [ ] Extract time-based features (e.g., day of week, hour, seasonality)
- [ ] Encode categorical variables (e.g., one-hot, label, target)
- [ ] Generate text embeddings or NLP-derived features
- [ ] Create lag and rolling window features for time series data
- [ ] Apply domain-specific feature logic (custom transformations)

---

## 🧬 Feature Selection

- [ ] Remove constant or near-constant features
- [ ] Remove highly correlated features
- [ ] Use univariate statistical tests (e.g., ANOVA, chi-square)
- [ ] Perform model-based feature selection (e.g., Lasso, Tree-based)
- [ ] Recursive feature elimination (RFE)
- [ ] Permutation-based importance analysis

---

## 🔁 Feature Transformation

- [ ] Standardize or normalize features
- [ ] Log or Box-Cox transform skewed features
- [ ] Polynomial or interaction features
- [ ] Dimensionality reduction (e.g., PCA, UMAP, t-SNE)
- [ ] Binning and discretization

---

## 💾 Feature Persistence

- [ ] Save feature schema and pipeline for reproducibility
- [ ] Serialize transformations using `sklearn.Pipeline` or similar
- [ ] Support versioned feature sets for experiment tracking
- [ ] Document input/output contracts for downstream model use

---

> ✅ Tip: Keep transformations modular, testable, and consistent across training and inference pipelines.
