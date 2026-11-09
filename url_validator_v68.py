
import ipaddress
import re

from urllib.parse import urlsplit


MAX_URL_LENGTH = 2048

DOMAIN_LABEL = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
)


def validate_url(url):
    if not isinstance(url, str):
        raise ValueError("URL must be a string.")

    url = url.strip()

    if not url:
        raise ValueError("Please enter a URL.")

    if len(url) > MAX_URL_LENGTH:
        raise ValueError("URL is too long.")

    if any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("URL contains control characters.")

    if any(char.isspace() for char in url):
        raise ValueError("URL contains whitespace.")

    if "\\" in url:
        raise ValueError("Backslashes are not accepted.")

    # Add HTTPS to URLs without a scheme
    if "://" not in url:
        if ":" in url.split("/")[0] and not url.startswith("["):
            if not re.match(
                r"^[a-zA-Z0-9.-]+:\d+(?:[/?#]|$)", url
            ):
                raise ValueError("Invalid or unsupported URL scheme.")

        url = "https://" + url

    try:
        parsed = urlsplit(url)

        if parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(
                "Only HTTP and HTTPS URLs are supported."
            )

        if not parsed.hostname:
            raise ValueError("Invalid hostname.")

        if parsed.username is not None or parsed.password is not None:
            raise ValueError(
                "URLs containing username/password are not accepted."
            )

        hostname = parsed.hostname.rstrip(".").lower()

        if "%" in parsed.netloc:
            raise ValueError(
                "Encoded hostname characters are not accepted."
            )

        # Reject an explicitly empty port
        if parsed.netloc.endswith(":"):
            raise ValueError(
                "Port separator found without a port number."
            )

        try:
            port = parsed.port
        except ValueError:
            raise ValueError("Invalid port number.")

        if port is not None and port not in (80, 443):
            raise ValueError(
                "Only standard HTTP/HTTPS ports are accepted."
            )

        if hostname == "localhost" or hostname.endswith(".localhost"):
            raise ValueError("Localhost URLs are not accepted.")

        # Validate IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            ip = None

        if ip is not None:
            if not ip.is_global:
                raise ValueError(
                    "Private or non-public IP addresses are not accepted."
                )
        else:
            # Reject invalid IPv4-looking hostnames
            if re.fullmatch(r"[0-9.]+", hostname):
                raise ValueError("Invalid IP address.")

            labels = hostname.split(".")

            if len(labels) < 2:
                raise ValueError("Invalid domain name.")

            if len(hostname) > 253:
                raise ValueError("Domain name is too long.")

            for label in labels:
                if not DOMAIN_LABEL.fullmatch(label):
                    raise ValueError("Invalid domain label.")

            if not labels[-1].isalpha() or len(labels[-1]) < 2:
                raise ValueError("Invalid top-level domain.")

        return url

    except ValueError:
        raise


if __name__ == "__main__":

    test_urls = [
        "https://google.com",
        "github.com",
        "https://example.com/login",
        "https://google.com@fake-login.com",
        "http://localhost",
        "http://192.168.1.1",
        "https://example.com:9999",
        "https://bad domain.com",
        "https://example.com\\@evil.com",
        "https://example.com:",
        "https://256.256.256.256",
        "https://example.com",
    ]

    print("=" * 60)
    print("CYBERSENTINEL AI - URL VALIDATION TEST")
    print("=" * 60)

    for url in test_urls:
        try:
            normalized = validate_url(url)
            print(f"ACCEPT  | {url}")
        except ValueError as error:
            print(f"REJECT  | {url}")
            print(f"Reason  | {error}")

    print("\nVALIDATION TEST COMPLETED")
