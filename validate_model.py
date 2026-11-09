
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import (
    train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = Path("processed/sampled_dataset.csv")

df = pd.read_csv(DATA_PATH, low_memory=False)

df.columns = df.columns.str.strip()
df = df.replace([np.inf, -np.inf], np.nan)

# Keep classes with at least 100 records
counts = df["Label"].value_counts()
valid_classes = counts[counts >= 100].index

df = df[df["Label"].isin(valid_classes)].copy()

# Remove exact duplicate records before splitting
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)

print("Duplicates removed:", before - len(df))

# Select numerical features
X = df.drop(columns=["Label"])
X = X.select_dtypes(include=[np.number])
X = X.dropna(axis=1, how="all")

y = df["Label"]

# Split: 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)

print("\nDataset split:")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))

pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", RandomForestClassifier(
        n_estimators=100,
        max_depth=16,
        min_samples_leaf=2,
        class_weight="balanced",
        n_jobs=2,
        random_state=42
    ))
])

print("\nTraining model...")
pipeline.fit(X_train, y_train)

print("\nVALIDATION RESULTS")
val_predictions = pipeline.predict(X_val)

print("Validation Accuracy:",
      accuracy_score(y_val, val_predictions))

print(classification_report(
    y_val,
    val_predictions,
    zero_division=0
))

print("\nFINAL TEST RESULTS")
test_predictions = pipeline.predict(X_test)

print("Test Accuracy:",
      accuracy_score(y_test, test_predictions))

print(classification_report(
    y_test,
    test_predictions,
    zero_division=0
))

import joblib

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

joblib.dump(
    {
        "pipeline": pipeline,
        "features": X.columns.tolist(),
        "classes": pipeline.classes_.tolist(),
        "model_version": "validated_v1"
    },
    MODEL_DIR / "cybersentinel_validated.pkl"
)

print("\nValidated model saved successfully!")
