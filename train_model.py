
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer

DATA_PATH = Path("processed/sampled_dataset.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Loading dataset...")
df = pd.read_csv(DATA_PATH, low_memory=False)

df.columns = df.columns.str.strip()
df = df.replace([np.inf, -np.inf], np.nan)

# Keep only classes with enough samples for this baseline
counts = df["Label"].value_counts()
valid_classes = counts[counts >= 100].index
df = df[df["Label"].isin(valid_classes)].copy()

# Select numerical features only
X = df.drop(columns=["Label"])
X = X.select_dtypes(include=[np.number])
X = X.dropna(axis=1, how="all")

y = df["Label"]

print(f"Records: {len(df)}")
print(f"Features: {X.shape[1]}")
print(f"Classes: {y.nunique()}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

imputer = SimpleImputer(strategy="median")

X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

print("\nTraining Random Forest...")


model = RandomForestClassifier(
    n_estimators=100,
    max_depth=16,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=2,
    random_state=42
)


model.fit(X_train, y_train)

predictions = model.predict(X_test)

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

fig, ax = plt.subplots(figsize=(14, 11))

ConfusionMatrixDisplay.from_predictions(
    y_test,
    predictions,
    labels=model.classes_,
    xticks_rotation=90,
    cmap="Blues",
    ax=ax
)

plt.title("CyberSentinel AI - Confusion Matrix")
plt.tight_layout()

fig.savefig(
    MODEL_DIR / "confusion_matrix.png",
    dpi=160,
    bbox_inches="tight"
)

plt.close(fig)

print("Confusion matrix saved successfully!")


print("\nMODEL RESULTS")
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

joblib.dump(
    {
        "model": model,
        "imputer": imputer,
        "features": X.columns.tolist()
    },
    MODEL_DIR / "cybersentinel_model.pkl"
)

print("\nModel saved successfully!")
