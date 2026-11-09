
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report
)

df = pd.read_csv(
    "processed/sampled_dataset.csv",
    low_memory=False
)

df.columns = df.columns.str.strip()
df = df.replace([np.inf, -np.inf], np.nan)

counts = df["Label"].value_counts()
valid = counts[counts >= 100].index
df = df[df["Label"].isin(valid)].copy()

X = df.drop(columns=["Label"])
X = X.select_dtypes(include=[np.number])
X = X.dropna(axis=1, how="all")

y = df["Label"]

# Remove Destination Port for this experiment
X = X.drop(columns=["Destination Port"], errors="ignore")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

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

print("Training without Destination Port...")

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, predictions))
print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))
