"""
Sentinel AI — Statistical Drift Detectors

Implements 10 independent statistical drift detection algorithms:
1. Population Stability Index (PSI)
2. Jensen-Shannon Distance
3. KL Divergence
4. Wasserstein Distance (Earth Mover's Distance)
5. Mean Drift
6. Standard Deviation Drift
7. Missing Value Drift
8. Cardinality Drift
9. Category Distribution Drift
10. Numeric Distribution Drift
"""

import math
from collections import Counter
from typing import Any

import numpy as np

from app.drift_engine.base_detector import BaseDriftDetector, DriftResultItem
from app.models.enums import DetectorType, DriftSeverity


def _clean_numeric(data: list[Any]) -> list[float]:
    """Filter non-null numeric values."""
    res = []
    for x in data:
        if x is not None:
            try:
                val = float(x)
                if not (math.isnan(val) or math.isinf(val)):
                    res.append(val)
            except (ValueError, TypeError):
                pass
    return res


# ── 1. PSI Detector ───────────────────────────────────────────────────────────
class PSIDetector(BaseDriftDetector):
    """Calculates Population Stability Index (PSI) using binned quantile distributions."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.PSI

    @property
    def default_threshold(self) -> float:
        return 0.1  # PSI > 0.1 indicates moderate drift, > 0.2 indicates significant drift

    def detect(
        self,
        baseline_data: list[Any],
        current_data: list[Any],
        column_name: str,
        column_type: str = "numeric",
        threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        base_clean = _clean_numeric(baseline_data)
        curr_clean = _clean_numeric(current_data)

        if not base_clean or not curr_clean:
            return DriftResultItem(
                column_name=column_name,
                column_type=column_type,
                detector_type=self.detector_type,
                drift_detected=False,
                drift_score=0.0,
                threshold=thresh,
                severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for PSI calculation",
            )

        # Create 10 quantile bins based on baseline
        quantiles = np.linspace(0, 100, 11)
        bins = np.percentile(base_clean, quantiles)
        bins = np.unique(bins)
        if len(bins) < 2:
            bins = np.array([min(base_clean) - 1e-5, max(base_clean) + 1e-5])

        base_counts, _ = np.histogram(base_clean, bins=bins)
        curr_counts, _ = np.histogram(curr_clean, bins=bins)

        base_pcts = base_counts / max(len(base_clean), 1)
        curr_pcts = curr_counts / max(len(curr_clean), 1)

        # Avoid zero division
        eps = 1e-4
        base_pcts = np.where(base_pcts == 0, eps, base_pcts)
        curr_pcts = np.where(curr_pcts == 0, eps, curr_pcts)

        psi_val = float(np.sum((curr_pcts - base_pcts) * np.log(curr_pcts / base_pcts)))
        psi_score = round(max(0.0, psi_val), 4)

        drift_detected = psi_score >= thresh
        if psi_score >= 0.25:
            sev = DriftSeverity.CRITICAL
        elif psi_score >= 0.15:
            sev = DriftSeverity.HIGH
        elif psi_score >= 0.1:
            sev = DriftSeverity.MEDIUM
        elif psi_score >= 0.05:
            sev = DriftSeverity.LOW
        else:
            sev = DriftSeverity.INFO

        exp = (
            f"PSI score {psi_score:.4f} exceeds threshold {thresh:.2f} (Significant population shift)"
            if drift_detected
            else f"PSI score {psi_score:.4f} within threshold {thresh:.2f}"
        )

        return DriftResultItem(
            column_name=column_name,
            column_type=column_type,
            detector_type=self.detector_type,
            drift_detected=drift_detected,
            drift_score=psi_score,
            threshold=thresh,
            severity=sev,
            explanation=exp,
            metrics_data={"psi": psi_score, "bin_count": len(bins) - 1},
        )


# ── 2. Jensen-Shannon Distance Detector ────────────────────────────────────────
class JensenShannonDetector(BaseDriftDetector):
    """Calculates Jensen-Shannon distance between baseline and current distributions."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.JENSEN_SHANNON

    @property
    def default_threshold(self) -> float:
        return 0.15

    def detect(
        self,
        baseline_data: list[Any],
        current_data: list[Any],
        column_name: str,
        column_type: str = "numeric",
        threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name,
                column_type=column_type,
                detector_type=self.detector_type,
                drift_detected=False,
                drift_score=0.0,
                threshold=thresh,
                severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for JS distance",
            )

        bins = 10
        min_v = min(min(b_clean), min(c_clean))
        max_v = max(max(b_clean), max(c_clean))
        if min_v == max_v:
            max_v += 1.0

        p, _ = np.histogram(b_clean, bins=bins, range=(min_v, max_v), density=True)
        q, _ = np.histogram(c_clean, bins=bins, range=(min_v, max_v), density=True)

        p = np.where(p == 0, 1e-6, p)
        q = np.where(q == 0, 1e-6, q)
        p = p / np.sum(p)
        q = q / np.sum(q)

        m = 0.5 * (p + q)
        kl_pm = np.sum(p * np.log2(p / m))
        kl_qm = np.sum(q * np.log2(q / m))
        js_dist = math.sqrt(max(0.0, float(0.5 * (kl_pm + kl_qm))))
        js_score = round(js_dist, 4)

        drift_detected = js_score >= thresh
        sev = DriftSeverity.HIGH if js_score >= 0.3 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name,
            column_type=column_type,
            detector_type=self.detector_type,
            drift_detected=drift_detected,
            drift_score=js_score,
            threshold=thresh,
            severity=sev,
            explanation=f"Jensen-Shannon distance is {js_score:.4f} (threshold {thresh:.2f})",
            metrics_data={"js_distance": js_score},
        )


# ── 3. KL Divergence Detector ──────────────────────────────────────────────────
class KLDivergenceDetector(BaseDriftDetector):
    """Calculates Kullback-Leibler (KL) Divergence."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.KL_DIVERGENCE

    @property
    def default_threshold(self) -> float:
        return 0.20

    def detect(
        self,
        baseline_data: list[Any],
        current_data: list[Any],
        column_name: str,
        column_type: str = "numeric",
        threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name, column_type=column_type, detector_type=self.detector_type,
                drift_detected=False, drift_score=0.0, threshold=thresh, severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for KL divergence",
            )

        min_v = min(min(b_clean), min(c_clean))
        max_v = max(max(b_clean), max(c_clean)) + 1e-5
        p, _ = np.histogram(b_clean, bins=10, range=(min_v, max_v))
        q, _ = np.histogram(c_clean, bins=10, range=(min_v, max_v))

        p_pct = np.where(p == 0, 1e-4, p) / len(b_clean)
        q_pct = np.where(q == 0, 1e-4, q) / len(c_clean)

        kl_div = float(np.sum(q_pct * np.log(q_pct / p_pct)))
        score = round(max(0.0, kl_div), 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.4 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"KL divergence is {score:.4f} (threshold {thresh:.2f})",
            metrics_data={"kl_divergence": score},
        )


# ── 4. Wasserstein Distance Detector ──────────────────────────────────────────
class WassersteinDetector(BaseDriftDetector):
    """Calculates Wasserstein Distance (Earth Mover's Distance)."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.WASSERSTEIN

    @property
    def default_threshold(self) -> float:
        return 0.10

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "numeric", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name, column_type=column_type, detector_type=self.detector_type,
                drift_detected=False, drift_score=0.0, threshold=thresh, severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for Wasserstein distance",
            )

        b_sorted = np.sort(b_clean)
        c_sorted = np.sort(c_clean)

        # Standardized scale normalization
        std_base = np.std(b_clean) or 1.0
        b_norm = b_sorted / std_base
        c_norm = c_sorted / std_base

        # Quantile alignment
        quants = np.linspace(0, 1, 100)
        b_q = np.quantile(b_norm, quants)
        c_q = np.quantile(c_norm, quants)

        distance = float(np.mean(np.abs(c_q - b_q)))
        score = round(distance, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.25 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Wasserstein distance normalized is {score:.4f} (threshold {thresh:.2f})",
            metrics_data={"wasserstein_distance": score},
        )


# ── 5. Mean Drift Detector ─────────────────────────────────────────────────────
class MeanDriftDetector(BaseDriftDetector):
    """Calculates relative shift in statistical mean (|mean_current - mean_base| / std_base)."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.MEAN_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.15  # 15% standard deviation shift

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "numeric", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name, column_type=column_type, detector_type=self.detector_type,
                drift_detected=False, drift_score=0.0, threshold=thresh, severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for mean drift",
            )

        m_base = float(np.mean(b_clean))
        m_curr = float(np.mean(c_clean))
        std_base = float(np.std(b_clean)) or 1e-5

        rel_shift = abs(m_curr - m_base) / std_base
        score = round(rel_shift, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.3 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Mean shifted by {score:.2f} std dev (Base: {m_base:.2f}, Curr: {m_curr:.2f})",
            metrics_data={"baseline_mean": m_base, "current_mean": m_curr, "relative_shift": score},
        )


# ── 6. Standard Deviation Drift Detector ───────────────────────────────────────
class StdDriftDetector(BaseDriftDetector):
    """Calculates variance shift in standard deviation (|std_curr - std_base| / std_base)."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.STD_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.20  # 20% variance shift

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "numeric", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name, column_type=column_type, detector_type=self.detector_type,
                drift_detected=False, drift_score=0.0, threshold=thresh, severity=DriftSeverity.INFO,
                explanation="Insufficient data for std dev drift",
            )

        std_base = float(np.std(b_clean)) or 1e-5
        std_curr = float(np.std(c_clean))

        shift = abs(std_curr - std_base) / std_base
        score = round(shift, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Standard deviation shifted by {score * 100:.1f}% (Base: {std_base:.2f}, Curr: {std_curr:.2f})",
            metrics_data={"baseline_std": std_base, "current_std": std_curr, "variance_ratio": score},
        )


# ── 7. Missing Value Drift Detector ───────────────────────────────────────────
class MissingValueDriftDetector(BaseDriftDetector):
    """Detects absolute shift in null value percentage between dataset versions."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.MISSING_VALUE_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.05  # 5% shift in null percentage

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "numeric", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold

        b_nulls = sum(1 for x in baseline_data if x is None)
        c_nulls = sum(1 for x in current_data if x is None)

        b_rate = b_nulls / max(len(baseline_data), 1)
        c_rate = c_nulls / max(len(current_data), 1)

        diff = abs(c_rate - b_rate)
        score = round(diff, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.15 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Null rate changed by {score * 100:.1f}% (Base: {b_rate * 100:.1f}%, Curr: {c_rate * 100:.1f}%)",
            metrics_data={"baseline_null_rate": b_rate, "current_null_rate": c_rate, "null_diff": score},
        )


# ── 8. Cardinality Drift Detector ─────────────────────────────────────────────
class CardinalityDriftDetector(BaseDriftDetector):
    """Detects changes in unique value count (cardinality)."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.CARDINALITY_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.10  # 10% change in distinct categories

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "categorical", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold

        b_unique = len(set(x for x in baseline_data if x is not None))
        c_unique = len(set(x for x in current_data if x is not None))

        diff = abs(c_unique - b_unique) / max(b_unique, 1)
        score = round(diff, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Distinct categories changed by {score * 100:.1f}% (Base: {b_unique}, Curr: {c_unique})",
            metrics_data={"baseline_unique": b_unique, "current_unique": c_unique, "diff_ratio": score},
        )


# ── 9. Category Distribution Drift Detector ───────────────────────────────────
class CategoryDistributionDetector(BaseDriftDetector):
    """Calculates frequency vector distance for categorical features."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.CATEGORY_DISTRIBUTION_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.10

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "categorical", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold

        b_counts = Counter(str(x) for x in baseline_data if x is not None)
        c_counts = Counter(str(x) for x in current_data if x is not None)

        all_cats = set(b_counts.keys()).union(set(c_counts.keys()))
        b_total = max(sum(b_counts.values()), 1)
        c_total = max(sum(c_counts.values()), 1)

        l1_diff = 0.0
        for cat in all_cats:
            p = b_counts[cat] / b_total
            q = c_counts[cat] / c_total
            l1_diff += abs(p - q)

        score = round(float(0.5 * l1_diff), 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.25 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Categorical distribution variation distance is {score:.4f} (threshold {thresh:.2f})",
            metrics_data={"variation_distance": score, "categories_count": len(all_cats)},
        )


# ── 10. Numeric Distribution Drift Detector ───────────────────────────────────
class NumericDistributionDetector(BaseDriftDetector):
    """Calculates Kolmogorov-Smirnov style max cumulative distribution function (CDF) distance."""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.NUMERIC_DISTRIBUTION_DRIFT

    @property
    def default_threshold(self) -> float:
        return 0.10

    def detect(
        self, baseline_data: list[Any], current_data: list[Any], column_name: str, column_type: str = "numeric", threshold: float | None = None,
    ) -> DriftResultItem:
        thresh = threshold if threshold is not None else self.default_threshold
        b_clean = _clean_numeric(baseline_data)
        c_clean = _clean_numeric(current_data)

        if not b_clean or not c_clean:
            return DriftResultItem(
                column_name=column_name, column_type=column_type, detector_type=self.detector_type,
                drift_detected=False, drift_score=0.0, threshold=thresh, severity=DriftSeverity.INFO,
                explanation="Insufficient numeric data for distribution comparison",
            )

        b_sorted = np.sort(b_clean)
        c_sorted = np.sort(c_clean)

        all_vals = np.sort(np.concatenate([b_sorted, c_sorted]))
        b_cdf = np.searchsorted(b_sorted, all_vals, side="right") / len(b_sorted)
        c_cdf = np.searchsorted(c_sorted, all_vals, side="right") / len(c_sorted)

        ks_stat = float(np.max(np.abs(b_cdf - c_cdf)))
        score = round(ks_stat, 4)
        drift_detected = score >= thresh
        sev = DriftSeverity.HIGH if score >= 0.25 else (DriftSeverity.MEDIUM if drift_detected else DriftSeverity.INFO)

        return DriftResultItem(
            column_name=column_name, column_type=column_type, detector_type=self.detector_type,
            drift_detected=drift_detected, drift_score=score, threshold=thresh, severity=sev,
            explanation=f"Maximum CDF distribution distance (KS-statistic) is {score:.4f} (threshold {thresh:.2f})",
            metrics_data={"ks_statistic": score},
        )
