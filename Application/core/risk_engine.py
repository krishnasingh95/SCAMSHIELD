"""
ScamShield — Combined Risk Engine
Aggregates signals from multiple analyzers into a unified risk score.
"""
from utils.risk_levels import RiskLevel, confidence_to_risk


class RiskEngine:
    """
    Aggregates individual analyzer results into a combined risk assessment.
    Weights are configurable and reflect relative signal importance.
    """

    WEIGHTS = {
        "sms": 0.45,
        "url": 0.55,
    }

    def combine(self, results: dict) -> dict:
        """
        results: { "sms": <predict_result>, "url": <predict_result>, ... }
        Returns aggregated risk dict.
        """
        scores    = []
        component = {}

        for key, res in results.items():
            if res and res.get("status") == "ok" and res.get("confidence") is not None:
                conf   = res["confidence"]
                weight = self.WEIGHTS.get(key, 0.5)
                scores.append(conf * weight)
                component[key] = res

        if not scores:
            return {
                "status":           "no_predictions",
                "combined_score":   None,
                "risk_level":       RiskLevel.UNKNOWN,
                "components":       component,
            }

        # Base weighted average
        total_weight    = sum(self.WEIGHTS.get(k, 0.5) for k in results if results[k] and results[k].get("status") == "ok")
        weighted_avg    = sum(scores) / max(total_weight, 1e-9)

        # Pipeline Optimization: Dilution Resistance (Anti-Masking Protection)
        # Prevents an attacker from diluting a high-confidence threat in one channel (e.g. SMS)
        # simply by attaching a benign URL (e.g. google.com).
        individual_scores = [
            res["confidence"] for res in results.values()
            if res and res.get("status") == "ok" and res.get("confidence") is not None
        ]
        max_single_score = max(individual_scores) if individual_scores else 0.0

        if max_single_score >= 0.65:
            # Enforce an active threat floor (at least 85% of peak alert signal)
            combined_score = max(weighted_avg, max_single_score * 0.85)
        else:
            combined_score = weighted_avg

        risk_level      = confidence_to_risk(combined_score)

        return {
            "status":           "ok",
            "combined_score":   round(combined_score, 4),
            "risk_level":       risk_level,
            "components":       component,
            "threat_detected":  combined_score >= 0.5,
        }
