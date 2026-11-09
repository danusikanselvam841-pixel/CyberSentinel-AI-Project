
from url_validator_v68 import validate_url

test_cases = [
    ("https:///example.com", False),
    ("https://example.com:", False),
    ("https://example.com:abc", False),
    ("https://example.com:443", True),
    ("https://example.com:80", True),
    ("https://example.com.", True),
    ("https://example.com//login", True),
    ("https://example.com/%2Fadmin", True),
    ("https://example.com?next=https://evil.com", True),
    ("https://example.com#fragment", True),
    ("https://[::1]", False),
    ("https://[2001:db8::1]", False),
    ("https://256.256.256.256", False),
    ("https://example.com:443:80", False),
    ("https://example.com%40evil.com", False),
]

passed = 0

print("=" * 65)
print("CYBERSENTINEL AI - EDGE CASE SECURITY TEST")
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

    print(f"{status:<5} | {url}")

print("\n" + "=" * 65)
print(f"PASSED: {passed}/{len(test_cases)}")
print(f"FAILED: {len(test_cases) - passed}")

if passed == len(test_cases):
    print("ALL TESTS PASSED")
else:
    print("EDGE CASES REQUIRE FIXES")
