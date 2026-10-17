# Synthetic IPD generator — research prototype

**Status: methods prototype; not validated for publication or clinical use.**
This repository generates **simulated rows** from user-supplied aggregate moments.
It does **not** reconstruct the original participants or create genuine
individual participant data (IPD), and it has **no certified privacy guarantee**.

## What is implemented

A reproducible multivariate-normal simulator (`synthetic_ipd.py`) given:
- a target population mean and standard deviation for each continuous variable;
- a **symmetric, positive-semidefinite correlation matrix** with unit diagonal;
- sample size and random seed.

This is the special case of a Gaussian copula with **normal marginals**. The
empirical correlations, means and standard deviations are random estimates of
those population parameters: **they are not exactly preserved**. The code
**rejects** materially non-PSD matrices rather than silently changing published
inputs. Missing or unreported correlations **cannot be inferred** here.
No categorical, skewed, survival, longitudinal, clustering, missingness, or
multi-arm treatment features are currently modelled.

## Run locally

```bash
python -m pip install -r requirements.txt
python synthetic_ipd.py --spec examples/summary_spec.json --output outputs/synthetic.csv
python -m unittest discover -s tests -v
```

The CSV contains simulated numerical records; the adjacent
`synthetic.csv.metadata.json` records the input SHA-256, seed and realised
sample moments. Do not mistake it for a reproduction of the original trial.
The example uses **illustrative parameters**, not a verified clinical cohort.

## Fundamental limitations and publication gates

1. **No patient-level truth recovery.** Aggregate means, SDs and pairwise
   correlations do not identify a unique joint distribution. This project
   provides *plausible simulated scenarios* under an explicit normality model.
2. **Privacy is not automatic.** Even synthetic outputs or aggregate inputs
   can disclose sensitive information. A privacy risk assessment, data-sharing
   rights review and relevant governance are mandatory before handling
   non-public or potentially identifiable summaries. This tool does not
   implement differential privacy.
3. **No intervention-effect interpretation.** Simulated rows must not be
   analysed as real trial observations, used to infer individual treatment
   effects, pooled as original IPD or used for clinical decisions.
4. **External validation missing.** Before publication, benchmark marginal
   recovery and correlation error across many seeds and sample sizes, compare
   with appropriately licensed real participant-level datasets, stress-test
   sparse/ill-conditioned matrices, and evaluate downstream method bias.
5. **Novelty not established.** Compare the approach against existing
   copula/synthetic-data packages. A manuscript needs a prespecified question,
   versioned benchmark corpus and statistically justified uncertainty.
6. **Reproducibility.** Pin and archive the environment and benchmark dataset
   versions, generate all figures by code, and have an independent analyst
   reproduce outputs. CI tests are a starting point, not manuscript validation.

## Background references

- Kaabachi et al. (2025), *A scoping review of privacy and utility metrics in
  medical synthetic data*, npj Digital Medicine:
  https://www.nature.com/articles/s41746-024-01359-3
- *On the fidelity versus privacy and utility trade-off of synthetic patient
  data* (2025), iScience:
  https://doi.org/10.1016/j.isci.2025.112382

**Release gate: NOT PUBLICATION READY.** This first implementation resolves
the discrepancy between a README describing a pipeline and an otherwise empty
repository; it does not provide methodological validation.
