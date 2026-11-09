
from urllib.parse import urlsplit


def split_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        hostname = (parsed.hostname or "").lower()
        hostname = hostname.rstrip(".")

        path = parsed.path or "/"

        if parsed.query:
            path += "?" + parsed.query

        return hostname, path

    except (ValueError, TypeError):
        return "", "/"


if __name__ == "__main__":

    test_urls = [
        "https://google.com",
        "http://github.com/login",
        "https://microsoft.com/account/verify",
        "https://example.com/login?user=123",
        "google.com",
        "https://subdomain.example.com/path"
    ]

    for url in test_urls:
        hostname, path = split_url(url)

        print("\nURL:", url)
        print("Hostname:", hostname)
        print("Path:", path)

    print("\nURL PARSER TEST COMPLETED")

