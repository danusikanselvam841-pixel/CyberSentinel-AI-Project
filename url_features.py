
from urllib.parse import urlsplit
import ipaddress


def extract_hostname(url):
    url = str(url).strip()

    if not url:
        return ""

    # Support URLs without http:// or https://
    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname or ""
        return hostname.lower().rstrip(".")
    except ValueError:
        return ""


def extract_url_features(url):
    url = str(url).strip()
    hostname = extract_hostname(url)

    try:
        ipaddress.ip_address(hostname)
        is_ip = 1
    except ValueError:
        is_ip = 0

    return {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "dot_count": hostname.count("."),
        "hyphen_count": hostname.count("-"),
        "digit_count": sum(
            char.isdigit() for char in hostname
        ),
        "at_symbol_count": url.count("@"),
        "question_mark_count": url.count("?"),
        "equals_count": url.count("="),
        "slash_count": url.count("/"),
        "is_ip_address": is_ip,
    }


if __name__ == "__main__":
    test_urls = [
        "https://example.com",
        "https://example.com/login",
        "https://fake-login.example.org/?email=user@example.com",
    ]

    for url in test_urls:
        print("\nURL:", url)
        print("Hostname:", extract_hostname(url))
        print("Features:", extract_url_features(url))
