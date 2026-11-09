 
import pandas as pd

df = pd.read_csv(
    "url_data/splits/train.csv",
    usecols=["url", "type"]
)

urls = df["url"].astype(str).str.lower().str.strip()

def get_scheme(url):
    if url.startswith("https://"):
        return "HTTPS"
    elif url.startswith("http://"):
        return "HTTP"
    else:
        return "NO SCHEME"

df["scheme"] = urls.map(get_scheme)

print("\nSCHEME DISTRIBUTION BY CLASS")

counts = pd.crosstab(
    df["type"],
    df["scheme"]
)

print(counts.to_string())

print("\nPERCENTAGE WITHIN EACH CLASS")

percentages = pd.crosstab(
    df["type"],
    df["scheme"],
    normalize="index"
) * 100

print(percentages.round(2).to_string())

print("\nTOTAL")
print(df["scheme"].value_counts().to_string())
