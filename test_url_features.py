
from urllib.parse import urlsplit
from url_features import extract_hostname

test_urls = [
    "https://example.com",
    "https://example.com/login",
    "https://example.com@fake-login.test/verify",
    "https://192.0.2.1/login",
    "https://fake-login.example.org/?email=user@example.com"
]

for url in test_urls:
    hostname = extract_hostname(url)

    parsed = urlsplit(
        url if "://" in url else "http://" + url
    )

    print("\nURL:", url)
    print("Hostname:", hostname)
    print("Path:", parsed.path)
    print("Query:", parsed.query)
    print("Username:", parsed.username)
    print("HTTPS:", parsed.scheme == "https")
    print("-" * 50)
