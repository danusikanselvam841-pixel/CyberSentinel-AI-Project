
from url_validator_v68 import validate_url


test_cases = [
    ("https://google.com", True),
    ("github.com", True),
    ("https://example.com/login?user=123", True),
    ("https://example.com#section", True),
    ("https://sub.example.com/path", True),

    ("http://localhost", False),
    ("http://127.0.0.1", False),
    ("http://192.168.1.1", False),
    ("http://10.0.0.1", False),
    ("http://169.254.169.254", False),

    ("https://google.com@evil.com", False),
    ("https://example.com:9999", False),
    ("https://bad domain.com", False),
    ("https://example.com\\@evil.com", False),
    ("javascript:alert(1)", False),
    ("ftp://example.com", False),

    ("https://-bad.com", False),
    ("https://bad-.com", False),
    ("https://example..com", False),
    ("https://example.c", False),
    ("", False),
]


passed = 0

print("=" * 65)
print("CYBERSENTINEL AI - ADVANCED URL SECURITY TEST")
print("=" * 65)

for url, expected in test_cases:

    try:
        validate_url(url)
        accepted = True
    except ValueError:
        accepted = False

    if accepted == expected:
        status = "PASS"
        passed += 1
    else:
        status = "FAIL"

    print(f"{status:<5} | {url!r}")


print("\n" + "=" * 65)
print(f"PASSED: {passed}/{len(test_cases)}")
print(f"FAILED: {len(test_cases) - passed}")

if passed == len(test_cases):
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED - REVIEW REQUIRED")
