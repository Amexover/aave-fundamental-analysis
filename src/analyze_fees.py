import pandas as pd


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "data/raw/aave_fees_revenue.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# PERIOD METRICS
# ============================================================

def calculate_period_metrics(df):
    """
    Calculate fees over different trailing periods.
    """

    latest_date = df["date"].max()

    def trailing_sum(days):
        start_date = latest_date - pd.Timedelta(
            days=days - 1
        )

        period = df[
            df["date"] >= start_date
        ]

        return period["fees_usd"].sum()

    fees_7d = trailing_sum(7)
    fees_30d = trailing_sum(30)
    fees_90d = trailing_sum(90)
    fees_365d = trailing_sum(365)

    # Annualized current 30-day fee run-rate
    annualized_30d = (
        fees_30d / 30 * 365
    )

    # Average daily fees over last 30 days
    avg_daily_30d = (
        fees_30d / 30
    )

    return {
        "latest_date": latest_date,
        "fees_7d": fees_7d,
        "fees_30d": fees_30d,
        "fees_90d": fees_90d,
        "fees_365d": fees_365d,
        "annualized_30d": annualized_30d,
        "avg_daily_30d": avg_daily_30d,
    }


# ============================================================
# GROWTH ANALYSIS
# ============================================================

def calculate_growth(df):
    """
    Compare current fee generation with previous periods.
    """

    latest_date = df["date"].max()

    # --------------------------------------------------------
    # Current 30 days
    # --------------------------------------------------------

    current_30_start = (
        latest_date
        - pd.Timedelta(days=29)
    )

    current_30 = df[
        df["date"] >= current_30_start
    ]["fees_usd"].sum()

    # --------------------------------------------------------
    # Previous 30 days
    # --------------------------------------------------------

    previous_30_end = (
        current_30_start
        - pd.Timedelta(days=1)
    )

    previous_30_start = (
        previous_30_end
        - pd.Timedelta(days=29)
    )

    previous_30 = df[
        (df["date"] >= previous_30_start)
        & (df["date"] <= previous_30_end)
    ]["fees_usd"].sum()

    if previous_30 > 0:
        mom_growth = (
            current_30 / previous_30 - 1
        ) * 100
    else:
        mom_growth = float("nan")

    # --------------------------------------------------------
    # Current 90 days
    # --------------------------------------------------------

    current_90_start = (
        latest_date
        - pd.Timedelta(days=89)
    )

    current_90 = df[
        df["date"] >= current_90_start
    ]["fees_usd"].sum()

    # --------------------------------------------------------
    # Previous 90 days
    # --------------------------------------------------------

    previous_90_end = (
        current_90_start
        - pd.Timedelta(days=1)
    )

    previous_90_start = (
        previous_90_end
        - pd.Timedelta(days=89)
    )

    previous_90 = df[
        (df["date"] >= previous_90_start)
        & (df["date"] <= previous_90_end)
    ]["fees_usd"].sum()

    if previous_90 > 0:
        growth_90d = (
            current_90 / previous_90 - 1
        ) * 100
    else:
        growth_90d = float("nan")

    # --------------------------------------------------------
    # Current 365 days
    # --------------------------------------------------------

    current_365_start = (
        latest_date
        - pd.Timedelta(days=364)
    )

    current_365 = df[
        df["date"] >= current_365_start
    ]["fees_usd"].sum()

    # --------------------------------------------------------
    # Previous 365 days
    # --------------------------------------------------------

    previous_365_end = (
        current_365_start
        - pd.Timedelta(days=1)
    )

    previous_365_start = (
        previous_365_end
        - pd.Timedelta(days=364)
    )

    previous_365 = df[
        (df["date"] >= previous_365_start)
        & (df["date"] <= previous_365_end)
    ]["fees_usd"].sum()

    if previous_365 > 0:
        yoy_growth = (
            current_365 / previous_365 - 1
        ) * 100
    else:
        yoy_growth = float("nan")

    return {
        "previous_30": previous_30,
        "mom_growth": mom_growth,
        "previous_90": previous_90,
        "growth_90d": growth_90d,
        "previous_365": previous_365,
        "yoy_growth": yoy_growth,
    }


# ============================================================
# MONTHLY DATA
# ============================================================

def calculate_monthly_fees(df):
    """
    Aggregate daily fees into calendar months.
    """

    monthly = (
        df
        .set_index("date")
        ["fees_usd"]
        .resample("ME")
        .sum()
        .reset_index()
    )

    monthly["growth_pct"] = (
        monthly["fees_usd"]
        .pct_change()
        * 100
    )

    return monthly


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    metrics,
    growth,
    monthly
):

    print()
    print("==============================================")
    print("              AAVE FEES ANALYSIS")
    print("==============================================")

    print(
        f"Latest date: "
        f"{metrics['latest_date'].date()}"
    )

    print()
    print("=== TRAILING FEES ===")

    print(
        f"7d fees: "
        f"${metrics['fees_7d']:,.0f}"
    )

    print(
        f"30d fees: "
        f"${metrics['fees_30d']:,.0f}"
    )

    print(
        f"90d fees: "
        f"${metrics['fees_90d']:,.0f}"
    )

    print(
        f"365d fees: "
        f"${metrics['fees_365d']:,.0f}"
    )

    print()
    print("=== CURRENT RUN-RATE ===")

    print(
        f"30d average daily fees: "
        f"${metrics['avg_daily_30d']:,.0f}"
    )

    print(
        f"Annualized 30d fee run-rate: "
        f"${metrics['annualized_30d']:,.0f}"
    )

    print()
    print("=== GROWTH ===")

    print(
        f"Previous 30d fees: "
        f"${growth['previous_30']:,.0f}"
    )

    print(
        f"30d vs previous 30d: "
        f"{growth['mom_growth']:+.2f}%"
    )

    print(
        f"Previous 90d fees: "
        f"${growth['previous_90']:,.0f}"
    )

    print(
        f"90d vs previous 90d: "
        f"{growth['growth_90d']:+.2f}%"
    )

    print(
        f"Previous 365d fees: "
        f"${growth['previous_365']:,.0f}"
    )

    print(
        f"365d YoY: "
        f"{growth['yoy_growth']:+.2f}%"
    )

    print()
    print("=== LAST 12 MONTHS ===")

    last_12 = monthly.tail(12)

    print(
        last_12.to_string(
            index=False,
            formatters={
                "date":
                    lambda x:
                        x.strftime("%Y-%m"),

                "fees_usd":
                    lambda x:
                        f"${x:,.0f}",

                "growth_pct":
                    lambda x: (
                        f"{x:+.2f}%"
                        if pd.notna(x)
                        else "N/A"
                    ),
            }
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading historical Aave fees..."
    )

    df = load_data()

    print(
        f"Loaded {len(df)} daily observations."
    )

    metrics = calculate_period_metrics(df)

    growth = calculate_growth(df)

    monthly = calculate_monthly_fees(df)

    print_results(
        metrics,
        growth,
        monthly
    )

    print()
    print(
        "ANALYSIS FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()