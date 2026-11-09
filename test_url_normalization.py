
from urllib.parse import urlsplit

def normalize_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return ""

        port = f":{parsed.port}" if parsed.port else ""

        path = parsed.path or ""
        query = f"?{parsed.query}" if parsed.query else ""

        return hostname + port + path + query

    except ValueError:
        return ""

test_urls = [
    "https://example.com",
    "http://example.com",
    "https://example.com/login",
    "https://example.com@fake-login.test/verify",
    "https://google.com/search?q=python",
]

for url in test_urls:
    print("Original:  ", url)
    print("Normalized:", normalize_url(url))
    print("-" * 45)
