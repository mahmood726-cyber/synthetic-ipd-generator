"""Generate reproducible *simulated* multivariate normal data from summary inputs.

This is a demonstration/benchmark tool, not patient-data reconstruction,
a privacy guarantee, or evidence that an original trial distribution is known.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def generate(spec: dict) -> tuple[list[str], np.ndarray]:
    """Return (column_names, samples) from a validated summary-statistics spec.

    The requested correlation is a *population* target. Sample estimates only
    approach it approximately as n grows; they are not constrained to match.
    """
    if not isinstance(spec, dict):
        raise ValueError("Specification must be a JSON object")
    n = spec.get("n")
    seed = spec.get("seed")
    if isinstance(n, bool) or not isinstance(n, int) or n < 2:
        raise ValueError("n must be an integer >= 2")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or seed < 0):
        raise ValueError("seed must be a non-negative integer or null")
    variables = spec.get("variables")
    if not isinstance(variables, list) or not variables:
        raise ValueError("variables must be a nonempty array")

    names: list[str] = []
    means: list[float] = []
    sds: list[float] = []
    for index, item in enumerate(variables):
        if not isinstance(item, dict):
            raise ValueError(f"Variable {index} must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Variable {index} needs a nonempty name")
        if name in names:
            raise ValueError(f"Duplicate variable name: {name}")
        try:
            mean, sd = float(item["mean"]), float(item["sd"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Variable {name}: mean and sd must be numeric") from exc
        if not math.isfinite(mean) or not math.isfinite(sd) or sd <= 0:
            raise ValueError(f"Variable {name}: require finite mean and positive finite sd")
        names.append(name)
        means.append(mean)
        sds.append(sd)

    try:
        corr = np.asarray(spec["correlation"], dtype=float)
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("correlation must be a numeric square matrix") from exc
    p = len(names)
    if corr.shape != (p, p) or not np.all(np.isfinite(corr)):
        raise ValueError(f"correlation must be a finite {p} x {p} matrix")
    if not np.allclose(corr, corr.T, atol=1e-10, rtol=0):
        raise ValueError("correlation must be symmetric")
    if not np.allclose(np.diag(corr), 1, atol=1e-10, rtol=0):
        raise ValueError("correlation diagonal must equal one")
    if np.any(np.abs(corr) > 1 + 1e-10):
        raise ValueError("correlation entries must be between -1 and 1")

    eigenvalues, eigenvectors = np.linalg.eigh(corr)
    if np.min(eigenvalues) < -1e-8:
        raise ValueError("correlation matrix is not positive semidefinite")
    # Eigenvalue square root supports valid singular correlations (Cholesky does not).
    transform = eigenvectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0.0)))
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, p)) @ transform.T
    samples = z * np.asarray(sds) + np.asarray(means)
    return names, samples


def run(spec_path: str | Path, out_csv: str | Path) -> dict:
    """Write a CSV and audit metadata; do not silently repair invalid inputs."""
    raw = Path(spec_path).read_bytes()
    spec = json.loads(raw)
    names, samples = generate(spec)

    output = Path(out_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(names)
        writer.writerows(samples.tolist())

    metadata = {
        "method": "multivariate normal simulation (Gaussian copula with normal marginals)",
        "source": "user-supplied aggregate statistics; not observed participant records",
        "privacy_certified": False,
        "n": int(samples.shape[0]),
        "seed": spec.get("seed"),
        "variables": names,
        "config_sha256": hashlib.sha256(raw).hexdigest(),
        "realized_mean": dict(zip(names, samples.mean(axis=0).tolist())),
        "realized_sample_sd": dict(zip(names, samples.std(axis=0, ddof=1).tolist())),
        "realized_sample_correlation": np.atleast_2d(np.corrcoef(samples, rowvar=False)).tolist(),
    }
    output.with_suffix(output.suffix + ".metadata.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="JSON specification (see examples/)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    meta = run(args.spec, args.output)
    print(f"Generated {meta['n']} simulated rows. No privacy certification is implied.")


if __name__ == "__main__":
    main()
