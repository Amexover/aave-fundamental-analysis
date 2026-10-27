import math

import pandas as pd
import pytest

from src.analyze_aave import concentration_analysis, prepare_data
from src.analyze_competitors import build_peer_dataframe, safe_divide
from src.analyze_fees import calculate_period_metrics
from src.peer_valuation import calculate_valuation


def test_borrow_shares_and_concentration():
    df = pd.DataFrame({"borrowed_usd": [70, 20, 10, 0], "supplied_usd": [100] * 4,
                       "estimated_protocol_interest": [7, 2, 1, 0]})
    prepared = prepare_data(df)
    assert prepared["borrow_share_pct"].tolist() == [70, 20, 10, 0]
    assert concentration_analysis(prepared)["top3_share"] == 100


def test_fee_periods_and_annualization():
    df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=40), "fees_usd": [10] * 40})
    result = calculate_period_metrics(df)
    assert result["fees_7d"] == 70
    assert result["fees_30d"] == 300
    assert result["annualized_30d"] == 3650


def test_peer_metrics_and_missing_values():
    data = {"aave": {"tvl_usd": 1000, "fees": {"30d": 30, "1y": 300},
                     "revenue": {"30d": 3, "1y": 30}},
            "peer": {"tvl_usd": 500, "fees": {"30d": None, "1y": None},
                     "revenue": {"30d": None, "1y": None}}}
    rows = build_peer_dataframe(data).set_index("protocol")
    assert rows.loc["Aave", "annualized_fees_30d"] == 365
    assert rows.loc["Aave", "annualized_fee_tvl_pct"] == pytest.approx(36.5)
    assert math.isnan(rows.loc["Peer", "annualized_fees_30d"])
    assert safe_divide(1, 0) is None
    assert safe_divide(None, 3) is None


def test_valuation_ratios_do_not_divide_by_zero():
    df = pd.DataFrame([{"market_cap_usd": 1000, "fdv_usd": 1200, "tvl_usd": 2000,
                        "annualized_fees_30d": 100, "fees_1y": 80,
                        "annualized_revenue_30d": 0, "revenue_1y": 10}])
    result = calculate_valuation(df).iloc[0]
    assert result["fdv_to_annualized_fees"] == 12
    assert pd.isna(result["mcap_to_annualized_revenue"])
