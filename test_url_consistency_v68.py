
from url_scanner_v67 import scan_url

test_pairs = [
    ("google.com", "https://google.com"),
    ("github.com", "https://github.com"),
    ("example.com", "https://example.com"),
    (
        "example.com/login",
        "https://example.com/login"
    ),
]

print("=" * 65)
print("CYBERSENTINEL AI - URL CONSISTENCY TEST")
print("=" * 65)

passed = 0

for url1, url2 in test_pairs:
    result1 = scan_url(url1)
    result2 = scan_url(url2)

    same_prediction = (
        result1["prediction"] == result2["prediction"]
    )

    same_score = (
        result1["threat_score"] == result2["threat_score"]
    )

    if same_prediction and same_score:
        status = "PASS"
        passed += 1
    else:
        status = "FAIL"

    print(f"\n{status} | {url1}")
    print(f"       {url2}")

    print(
        f"Prediction: {result1['prediction']} / "
        f"{result2['prediction']}"
    )

    print(
        f"Threat Score: {result1['threat_score']}% / "
        f"{result2['threat_score']}%"
    )

print("\n" + "=" * 65)
print(f"PASSED: {passed}/{len(test_pairs)}")
print(f"FAILED: {len(test_pairs) - passed}")
