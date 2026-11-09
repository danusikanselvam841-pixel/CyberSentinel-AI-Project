
import ipaddress
import math
from urllib.parse import urlsplit


FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "hostname_dot_count",
    "hostname_hyphen_count",
    "hostname_digit_count",
    "path_digit_count",
    "at_symbol_count",
    "question_mark_count",
    "equals_count",
    "percent_count",
    "subdomain_count",
    "is_ip_address",
    "has_username",
    "hostname_entropy"
]


def get_url_features(url):
    if not isinstance(url, str):
        return [0.0] * len(FEATURE_NAMES)

    url = url.strip()

    if not url:
        return [0.0] * len(FEATURE_NAMES)

    prepared = (
        url if "://" in url
        else "http://" + url
    )

    try:
        parsed = urlsplit(prepared)
        hostname = (parsed.hostname or "").lower()

        if not hostname:
            return [0.0] * len(FEATURE_NAMES)

        path = parsed.path or ""
        query = parsed.query or ""

        try:
            ipaddress.ip_address(hostname)
            is_ip = 1
        except ValueError:
            is_ip = 0

        # Remove scheme from lexical feature calculations
        lexical_url = (
            parsed.netloc
            + path
            + ("?" + query if query else "")
        )

        counts = {
            c: hostname.count(c)
            for c in set(hostname)
        }

        entropy = -sum(
            (count / len(hostname))
            * math.log2(count / len(hostname))
            for count in counts.values()
        )

        if is_ip:
            subdomain_count = 0
        else:
            # Approximation for ordinary domains
            subdomain_count = max(
                0,
                len(hostname.split(".")) - 2
            )

        return [
            len(lexical_url),
            len(hostname),
            len(path),
            len(query),
            hostname.count("."),
            hostname.count("-"),
            sum(c.isdigit() for c in hostname),
            sum(c.isdigit() for c in path),
            lexical_url.count("@"),
            lexical_url.count("?"),
            lexical_url.count("="),
            lexical_url.count("%"),
            subdomain_count,
            is_ip,
            int(parsed.username is not None),
            entropy
        ]

    except (ValueError, TypeError):
        return [0.0] * len(FEATURE_NAMES)


if __name__ == "__main__":

    examples = [
        "google.com",
        "http://google.com",
        "https://google.com",
        "http://192.168.1.1/login",
        "https://example.com@fake-login.test"
    ]

    print("CYBERSENTINEL V6.2 - FEATURE VALIDATION")
    print("=" * 55)

    for url in examples:
        print("\nURL:", url)

        features = get_url_features(url)

        for name, value in zip(
            FEATURE_NAMES,
            features
        ):
            print(f"{name}: {value}")

    a = get_url_features("google.com")
    b = get_url_features("http://google.com")
    c = get_url_features("https://google.com")

    assert a == b == c, (
        "Scheme invariance test failed!"
    )

    print("\nSCHEME INVARIANCE TEST: PASSED")
