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

## Dataset Leakage Audit

The V6 train, validation and test splits were audited.

| Check | Train vs Validation | Train vs Test | Validation vs Test |
|---|---:|---:|---:|
| Exact normalized URL overlap | 0 | 0 | 0 |
| Exact hostname overlap | 0 | 0 | 0 |
| WWW-normalized hostname overlap | 0 | 0 | 0 |
| Registered-domain overlap | 0 | 0 | 0 |

Registered-domain counts:
- Train: 105,361
- Validation: 22,593
- Test: 22,572

No invalid or unusable URLs were reported by the
registered-domain extraction audit.

These results support domain-level separation
between the evaluated dataset splits.

Remaining limitations:
- Previous test-set usage has not been ruled out.
- Dataset label quality requires further review.
- External independent security validation is needed.
- V74, V75 and V76 are not approved for production.

Production V1 remains unchanged.
