# CyberSentinel AI - Experimental Model Evaluation

Test dataset: url_data/splits_v6/test.csv
Test records: 88,537

| Metric | V74 | V75 | V76 |
|---|---:|---:|---:|
| Accuracy | 85.84% | 85.31% | 85.65% |
| Benign FPR | 7.09% | 6.49% | 6.64% |
| WWW Benign FPR | 40.70% | 20.58% | 26.86% |
| Phishing Recall | 58.10% | 52.67% | 54.92% |
| WWW Phishing Recall | 87.82% | 78.05% | 82.27% |

## Findings

- V74 has the highest phishing recall.
- V75 has the lowest benign false-positive rate.
- V76 provides an intermediate tradeoff.
- WWW normalization is not recommended because it reduces phishing recall.
- Exact normalized URL overlap between train, validation and test was zero.
- Hostname-level leakage and prior test-set usage have not been ruled out.
- No experimental model is approved for production deployment.
- Production V1 remains unchanged.

## Next steps

Review model limitations, scanner integration compatibility,
and independent security validation before deployment.
