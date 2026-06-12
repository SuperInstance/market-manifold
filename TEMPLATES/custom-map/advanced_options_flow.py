#!/usr/bin/env python3
"""
Custom ternary map: Advanced Options Flow Analysis

Measures the ratio of bullish to bearish options contracts
and encodes it as a ternary signal.

Usage:
    ./bin/register-map --room AAPL --name options-flow \
      --module TEMPLATES/custom-map/advanced_options_flow.py
"""

from market_manifold import TernaryMap, Trit
from typing import Dict, Any


class AdvancedOptionsFlowMap(TernaryMap):
    """Encode options flow into {+1, 0, -1} with volatility weighting."""

    def encode(self, data: Dict[str, Any]) -> Trit:
        put_call_ratio = data.get("put_call_ratio", 1.0)
        implied_volatility = data.get("implied_volatility", 0.3)

        # Weighted score: ratio adjusted by volatility
        score = (1.0 - put_call_ratio) * (1.0 + implied_volatility)

        if score > 0.5:
            return Trit.POS   # Bullish flow
        elif score < -0.5:
            return Trit.NEG   # Bearish flow
        else:
            return Trit.ZERO  # Neutral flow

    def confidence(self, data: Dict[str, Any]) -> float:
        """How confident are we in this encoding?"""
        volume = data.get("total_volume", 0)
        return min(1.0, volume / 10000)  # Higher volume = higher confidence
