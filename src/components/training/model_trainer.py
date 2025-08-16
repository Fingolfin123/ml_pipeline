import pandas as pd
import shap
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression

# ==== 1. Load your dataset ====
df = pd.read_csv("data/air_quality_health_dataset.csv")

target = 'respiratory_admissions'
features = [col for col in df.columns if col != target]
X = df[features]
y = df[target]

# ==== 2. Handle datetime fields ====
datetime_cols = []

for col in X.columns:
    # If it's already datetime dtype
    if np.issubdtype(X[col].dtype, np.datetime64):
        datetime_cols.append(col)
    # If it's object but parses as datetime
    elif X[col].dtype == 'object':
        try:
            pd.to_datetime(X[col], errors='raise')
            datetime_cols.append(col)
        except Exception:
            pass

# Option A: Drop datetime columns entirely
# X = X.drop(columns=datetime_cols)

# Option B: Extract useful components (seasonality, etc.)
for col in datetime_cols:
    X[col] = pd.to_datetime(X[col], errors='coerce')
    X[f"{col}_year"] = X[col].dt.year
    X[f"{col}_month"] = X[col].dt.month
    X[f"{col}_dayofweek"] = X[col].dt.dayofweek
    X = X.drop(columns=[col])  # Drop original datetime

# ==== 3. Encode categoricals ====
X = pd.get_dummies(X, drop_first=True)

# ==== 4. Remove near-constant features ====
constant_cols = [col for col in X.columns if X[col].nunique() <= 1]
X = X.drop(columns=constant_cols)

# ==== 5. Remove highly correlated features (> 0.9) ====
corr_matrix = X.corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
high_corr = [col for col in upper.columns if any(upper[col] > 0.9)]
X = X.drop(columns=high_corr)
print(f"Dropping highly correlated features: {high_corr}")

# ==== 6. Mutual Information filter (top 15) ====
mi_scores = mutual_info_regression(X, y, random_state=42)
mi_df = pd.DataFrame({'feature': X.columns, 'mi_score': mi_scores})
mi_df = mi_df.sort_values(by='mi_score', ascending=False)
top_features = mi_df['feature'].head(15).tolist()
X = X[top_features]
print(f"Dropping mutual infromation features: {top_features}")

# ==== 7. SHAP ranking ====
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)

shap_importance = np.abs(shap_values).mean(axis=0)
shap_df = pd.DataFrame({'feature': X_train.columns, 'shap_importance': shap_importance})
shap_df = shap_df.sort_values(by='shap_importance', ascending=False)
pritn(shap_df)
final_features = shap_df['feature'].head(10).tolist()

print("Datetime columns handled:", datetime_cols)
print("Final Selected Features:", final_features)

# ==== 8. Optional visualization ====
shap.summary_plot(shap_values, X_train, plot_type="bar")
