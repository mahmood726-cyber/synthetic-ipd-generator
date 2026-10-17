"""Statistical correctness and input-safety tests for simulated aggregate data."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from synthetic_ipd import generate, run


BASE = {
    "n": 20000,
    "seed": 7,
    "variables": [
        {"name": "Age", "mean": 60.0, "sd": 12.0},
        {"name": "Systolic_BP", "mean": 140.0, "sd": 20.0},
    ],
    "correlation": [[1.0, 0.55], [0.55, 1.0]],
}


class GeneratorTests(unittest.TestCase):
    def test_deterministic_and_converges_to_population_moments(self):
        names, x = generate(BASE)
        self.assertEqual(names, ["Age", "Systolic_BP"])
        self.assertTrue(np.array_equal(x, generate(BASE)[1]))
        self.assertAlmostEqual(float(x[:, 0].mean()), 60.0, delta=0.35)
        self.assertAlmostEqual(float(x[:, 1].std(ddof=1)), 20.0, delta=0.35)
        self.assertAlmostEqual(float(np.corrcoef(x, rowvar=False)[0, 1]), 0.55, delta=0.025)

    def test_rejects_non_psd_input(self):
        spec = {**BASE, "variables": [
            {"name": x, "mean": 0, "sd": 1} for x in ["a", "b", "c"]
        ], "correlation": [[1, 0.9, 0.9], [0.9, 1, -0.9], [0.9, -0.9, 1]]}
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            generate(spec)

    def test_rejects_bad_scale_and_duplicate_names(self):
        for modifications in (
            [{"name": "a", "mean": 0, "sd": 0}],
            [{"name": "a", "mean": 0, "sd": 1}, {"name": "a", "mean": 0, "sd": 1}],
        ):
            spec = {**BASE, "variables": modifications}
            with self.assertRaises(ValueError):
                generate(spec)

    def test_accepts_valid_singular_correlation(self):
        spec = {**BASE, "correlation": [[1, 1], [1, 1]], "n": 100}
        _, x = generate(spec)
        self.assertTrue(np.allclose(
            (x[:, 0] - 60) / 12, (x[:, 1] - 140) / 20, atol=1e-10
        ))

    def test_writes_traceable_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp, "spec.json")
            output = Path(tmp, "sim.csv")
            source.write_text(json.dumps(BASE), encoding="utf-8")
            meta = run(source, output)
            self.assertEqual(len(output.read_text().splitlines()), BASE["n"] + 1)
            self.assertFalse(meta["privacy_certified"])
            self.assertTrue(Path(str(output) + ".metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
