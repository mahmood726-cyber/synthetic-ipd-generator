
# Synthetic IPD Generator (Gaussian Copulas)

A methodology tool for generating privacy-preserving Synthetic Individual Participant Data (IPD) for clinical trials.

## The Bottleneck
Developing and validating new IPD meta-analysis algorithms (like one-stage mixed models or quantile meta-analyses) requires raw patient data. However, real clinical trial data is heavily restricted by HIPAA/GDPR and data-sharing agreements, stunting methodological research.

## The Solution
This Python/R pipeline takes published summary statistics (Means, SDs, Correlation Matrices) and uses **Gaussian Copulas** and **Cholesky Decomposition** to simulate synthetic patient cohorts. 

The generated synthetic IPD strictly preserves the marginal distributions and correlation structures of the original trial without containing a single row of real human data, completely bypassing privacy restrictions.

