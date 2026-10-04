import pandas as pd


def calculate_tvl_metrics(df: pd.DataFrame) -> dict:
    df = df.sort_values("date").copy()

    current_tvl = df["tvl_usd"].iloc[-1]
    current_date = df["date"].iloc[-1]

    ath_tvl = df["tvl_usd"].max()
    ath_date = df.loc[df["tvl_usd"].idxmax(), "date"]

    drawdown = (current_tvl / ath_tvl - 1) * 100

    def change_over_days(days: int) -> float:
        target_date = current_date - pd.Timedelta(days=days)

        historical = df[df["date"] <= target_date]

        if historical.empty:
            return float("nan")

        old_tvl = historical["tvl_usd"].iloc[-1]

        return (current_tvl / old_tvl - 1) * 100

    return {
        "current_tvl": current_tvl,
        "ath_tvl": ath_tvl,
        "ath_date": ath_date,
        "drawdown_pct": drawdown,
        "change_30d_pct": change_over_days(30),
        "change_90d_pct": change_over_days(90),
        "change_365d_pct": change_over_days(365),
    }