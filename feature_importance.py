
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

MODEL_PATH = Path("models/cybersentinel_model.pkl")

saved = joblib.load(MODEL_PATH)

model = saved["model"]
features = saved["features"]

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance", ascending=False
)

print("\nTOP 20 IMPORTANT FEATURES")
print(importance.head(20).to_string(index=False))

plt.figure(figsize=(11, 8))

top = importance.head(20).iloc[::-1]

plt.barh(top["Feature"], top["Importance"])

plt.title("CyberSentinel AI - Feature Importance")
plt.xlabel("Importance")
plt.tight_layout()

plt.savefig(
    "models/feature_importance.png",
    dpi=160,
    bbox_inches="tight"
)

print("\nFeature importance chart saved!")
