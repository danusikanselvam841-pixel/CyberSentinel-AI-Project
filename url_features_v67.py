
import numpy as np

from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer

from url_parser_v67 import split_url


def create_vectorizers():

    hostname_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=20000,
        min_df=3,
        sublinear_tf=True,
        dtype=np.float32
    )

    path_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=20000,
        min_df=3,
        sublinear_tf=True,
        dtype=np.float32
    )

    return hostname_vectorizer, path_vectorizer


def prepare_features(
    urls,
    hostname_vectorizer,
    path_vectorizer,
    fit=False
):

    hostnames = []
    paths = []

    for url in urls:
        hostname, path = split_url(url)

        hostnames.append(hostname)
        paths.append(path)

    if fit:
        X_hostname = hostname_vectorizer.fit_transform(
            hostnames
        )

        X_path = path_vectorizer.fit_transform(
            paths
        )

    else:
        X_hostname = hostname_vectorizer.transform(
            hostnames
        )

        X_path = path_vectorizer.transform(
            paths
        )

    X_combined = hstack(
        [X_hostname, X_path],
        format="csr",
        dtype=np.float32
    )

    return X_combined


if __name__ == "__main__":

    urls = [
        "https://google.com",
        "https://github.com/login",
        "https://example.com/account/verify",
        "https://microsoft.com/login?user=123",
        "https://subdomain.example.com/path"
    ]

    hostname_vectorizer, path_vectorizer = (
        create_vectorizers()
    )

    # Small test dataset: min_df=1 for testing only
    hostname_vectorizer.set_params(min_df=1)
    path_vectorizer.set_params(min_df=1)

    X = prepare_features(
        urls,
        hostname_vectorizer,
        path_vectorizer,
        fit=True
    )

    print("Number of URLs:", len(urls))

    print(
        "Hostname features:",
        len(hostname_vectorizer.get_feature_names_out())
    )

    print(
        "Path features:",
        len(path_vectorizer.get_feature_names_out())
    )

    print("Combined shape:", X.shape)

    print("\nFEATURE EXTRACTION TEST COMPLETED")
