
import pandas as pd

file_path = "processed/sampled_dataset.csv"

df = pd.read_csv(file_path, low_memory=False)

def clean_label(label):
    label = str(label).strip()

    if "Web Attack" in label:
        if "Brute Force" in label:
            return "Web Attack - Brute Force"
        if "XSS" in label:
            return "Web Attack - XSS"
        if "Sql Injection" in label:
            return "Web Attack - SQL Injection"

    return label

df["Label"] = df["Label"].apply(clean_label)

df.to_csv(file_path, index=False)

print("Labels fixed successfully!")
print("\nUpdated Classes:")
print(df["Label"].value_counts())

