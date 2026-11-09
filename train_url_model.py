
from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = Path("url_data/malicious_phish.csv")
MODEL_PATH = Path("models/url_threat_model.pkl")

print("Loading URL dataset...")

df = pd.read_csv(DATA_PATH, usecols=["url", "type"])

# Remove missing and duplicate URLs
df = df.dropna(subset=["url", "type"])
df["url"] = df["url"].astype(str).str.strip()
df["type"] = df["type"].astype(str).str.strip().str.lower()

df = df[df["url"] != ""]
df = df.drop_duplicates(subset=["url"])

print("Total unique URLs:", len(df))
print("\nCategories:")
print(df["type"].value_counts())

X = df["url"]
y = df["type"]

# Train / validation / test: 70 / 15 / 15
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

# Character patterns help recognize suspicious URL structures
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=3,
        max_features=100000,
        lowercase=True
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])

print("\nTraining URL threat model...")
pipeline.fit(X_train, y_train)

print("\nVALIDATION RESULTS")
val_pred = pipeline.predict(X_val)

print("Accuracy:", accuracy_score(y_val, val_pred))
print(classification_report(
    y_val,
    val_pred,
    zero_division=0
))

print("\nFINAL TEST RESULTS")
test_pred = pipeline.predict(X_test)

print("Accuracy:", accuracy_score(y_test, test_pred))
print(classification_report(
    y_test,
    test_pred,
    zero_division=0
))

MODEL_PATH.parent.mkdir(exist_ok=True)

joblib.dump({
    "pipeline": pipeline,
    "classes": pipeline.classes_.tolist(),
    "model_version": "url_detector_v1"
}, MODEL_PATH)

print("\nURL threat model saved successfully!")
print("Saved to:", MODEL_PATH)
