
from url_features_v62 import (
    get_url_features,
    FEATURE_NAMES
)

urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com",
    "https://google.com/login",
    "https://example.com/account/verify"
]

for url in urls:
    print("\n" + "=" * 60)
    print("URL:", url)
    print("=" * 60)

    values = get_url_features(url)

    for name, value in zip(FEATURE_NAMES, values):
        print(f"{name:<30}: {value}")

print("\nFEATURE INSPECTION COMPLETED")
