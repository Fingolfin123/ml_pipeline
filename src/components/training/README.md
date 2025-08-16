# Model Training Pipeline with Auto Feature Cleaning & Dynamic Hyperparameter Tuning

## Overview
This pipeline automatically:
1. Cleans and preprocesses features before training.
2. Dynamically adjusts hyperparameter search spaces based on dataset size.
3. Runs Bayesian optimization (`BayesSearchCV`) to find the best model parameters.
4. Reports R² scores for all tested models.

## Feature Cleaning Steps
1. **Remove near-zero variance features**
   - Uses `VarianceThreshold` to drop columns with constant values.
   
2. **Remove highly correlated features**
   - Calculates correlation matrix and drops one column from any pair with correlation > **0.95**.

3. **Scale numeric features**
   - Standardizes features to mean=0 and variance=1 (required for models like KNN, Linear Regression, and boosting algorithms).

## Dynamic Hyperparameter Tuning
Hyperparameter ranges are automatically adjusted based on:
- **Number of features** → affects `max_depth`
- **Number of rows** → affects `n_estimators`
- **Search range expansion** for `learning_rate` when dataset grows.

Example adjustments:
```python
RandomForest:
  n_estimators: 100 → up to 1000
  max_depth: 5 → up to 30
  min_samples_split: 2 → up to 20

GradientBoosting:
  n_estimators: 100 → up to 1000
  learning_rate: 0.005 → 0.3
  max_depth: 3 → up to 30



# 🎯 Model Training Module Checklist

This module contains all logic for training machine learning models, including dataset preparation, training loop, hyperparameter tuning, checkpointing, and integration with experiment tracking tools.

---

## 📁 Training Pipeline

- [ ] Load and preprocess training data (ensure consistency with inference)
- [ ] Split data into training, validation, and test sets
- [ ] Define model architecture or selection logic
- [ ] Log dataset version and metadata

---

## 🧪 Hyperparameter Tuning

- [ ] Support grid/random/Bayesian search (e.g., `sklearn`, `optuna`, `Ray Tune`)
- [ ] Track best parameters and performance
- [ ] Allow reproducible search with seed and config
- [ ] Save tuning results for analysis

---

## 🏋️ Model Training

- [ ] Train model with specified hyperparameters
- [ ] Track training/validation metrics (e.g., loss, accuracy, AUC)
- [ ] Add callbacks for early stopping, learning rate scheduling, etc.
- [ ] Run multiple trials for robustness (e.g., with cross-validation or bootstrapping)

---

## 💾 Checkpointing & Saving

- [ ] Save model weights at checkpoints and final epoch
- [ ] Store additional metadata (e.g., epoch, loss, config)
- [ ] Version model artifacts with date/hash/version tag
- [ ] Upload to model registry or object storage

---

## 🧾 Experiment Tracking

- [ ] Integrate with MLFlow, Weights & Biases, or custom tracker
- [ ] Record model parameters, metrics, and artifacts
- [ ] Tag experiments with descriptive metadata (e.g., purpose, data version, user)
- [ ] Visualize training performance over time

---

## 🔄 Reproducibility

- [ ] Seed all libraries (`numpy`, `random`, `torch`, etc.)
- [ ] Log exact code, config, and environment
- [ ] Enable deterministic training modes if supported
- [ ] Store all dependencies in `pyproject.toml` or `requirements.txt`

---

> ✅ Tip: Train models in parallel or on the cloud to save time and scale to larger datasets.
