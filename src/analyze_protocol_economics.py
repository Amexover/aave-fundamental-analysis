import pandas as pd


# ============================================================
# CONFIG
# ============================================================

FEES_PATH = "data/raw/aave_fees_revenue.csv"
REVENUE_PATH = "data/raw/aave_revenue.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    fees = pd.read_csv(
        FEES_PATH,
        parse_dates=["date"]
    )

    revenue = pd.read_csv(
        REVENUE_PATH,
        parse_dates=["date"]
    )

    df = pd.merge(
        fees,
        revenue,
        on="date",
        how="inner"
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# TRAILING SUM
# ============================================================

def trailing_sum(
    df,
    column,
    days
):

    latest_date = df["date"].max()

    start_date = (
        latest_date
        - pd.Timedelta(days=days - 1)
    )

    period = df[
        df["date"] >= start_date
    ]

    return period[column].sum()


# ============================================================
# CALCULATE ECONOMICS
# ============================================================

def calculate_economics(df):

    fees_30d = trailing_sum(
        df,
        "fees_usd",
        30
    )

    revenue_30d = trailing_sum(
        df,
        "revenue_usd",
        30
    )

    fees_90d = trailing_sum(
        df,
        "fees_usd",
        90
    )

    revenue_90d = trailing_sum(
        df,
        "revenue_usd",
        90
    )

    fees_365d = trailing_sum(
        df,
        "fees_usd",
        365
    )

    revenue_365d = trailing_sum(
        df,
        "revenue_usd",
        365
    )

    annualized_fees_30d = (
        fees_30d / 30 * 365
    )

    annualized_revenue_30d = (
        revenue_30d / 30 * 365
    )

    take_rate_30d = (
        revenue_30d
        / fees_30d
        * 100
    )

    take_rate_90d = (
        revenue_90d
        / fees_90d
        * 100
    )

    take_rate_365d = (
        revenue_365d
        / fees_365d
        * 100
    )

    return {
        "fees_30d": fees_30d,
        "revenue_30d": revenue_30d,

        "fees_90d": fees_90d,
        "revenue_90d": revenue_90d,

        "fees_365d": fees_365d,
        "revenue_365d": revenue_365d,

        "annualized_fees_30d":
            annualized_fees_30d,

        "annualized_revenue_30d":
            annualized_revenue_30d,

        "take_rate_30d":
            take_rate_30d,

        "take_rate_90d":
            take_rate_90d,

        "take_rate_365d":
            take_rate_365d,
    }


# ============================================================
# MONTHLY ECONOMICS
# ============================================================

def calculate_monthly_economics(df):

    monthly = (
        df
        .set_index("date")
        .resample("ME")
        .agg({
            "fees_usd": "sum",
            "revenue_usd": "sum",
        })
        .reset_index()
    )

    monthly["take_rate_pct"] = (
        monthly["revenue_usd"]
        / monthly["fees_usd"]
        * 100
    )

    monthly[
        "fees_growth_pct"
    ] = (
        monthly["fees_usd"]
        .pct_change()
        * 100
    )

    monthly[
        "revenue_growth_pct"
    ] = (
        monthly["revenue_usd"]
        .pct_change()
        * 100
    )

    return monthly


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(metrics):

    print()
    print("==============================================")
    print("          AAVE PROTOCOL ECONOMICS")
    print("==============================================")

    print()
    print("=== 30 DAYS ===")

    print(
        f"Fees: "
        f"${metrics['fees_30d']:,.0f}"
    )

    print(
        f"Revenue: "
        f"${metrics['revenue_30d']:,.0f}"
    )

    print(
        f"Revenue / Fees: "
        f"{metrics['take_rate_30d']:.2f}%"
    )

    print()
    print("=== 90 DAYS ===")

    print(
        f"Fees: "
        f"${metrics['fees_90d']:,.0f}"
    )

    print(
        f"Revenue: "
        f"${metrics['revenue_90d']:,.0f}"
    )

    print(
        f"Revenue / Fees: "
        f"{metrics['take_rate_90d']:.2f}%"
    )

    print()
    print("=== 365 DAYS ===")

    print(
        f"Fees: "
        f"${metrics['fees_365d']:,.0f}"
    )

    print(
        f"Revenue: "
        f"${metrics['revenue_365d']:,.0f}"
    )

    print(
        f"Revenue / Fees: "
        f"{metrics['take_rate_365d']:.2f}%"
    )

    print()
    print("=== CURRENT ANNUALIZED RUN-RATE ===")

    print(
        f"Annualized fees: "
        f"${metrics['annualized_fees_30d']:,.0f}"
    )

    print(
        f"Annualized revenue: "
        f"${metrics['annualized_revenue_30d']:,.0f}"
    )


# ============================================================
# PRINT MONTHLY DATA
# ============================================================

def print_monthly(monthly):

    print()
    print("==============================================")
    print("           MONTHLY ECONOMICS")
    print("==============================================")

    # Exclude current incomplete month.
    complete_months = monthly.iloc[:-1]

    last_12 = (
        complete_months
        .tail(12)
        .copy()
    )

    columns = [
        "date",
        "fees_usd",
        "revenue_usd",
        "take_rate_pct",
        "fees_growth_pct",
        "revenue_growth_pct",
    ]

    print(
        last_12[columns].to_string(
            index=False,
            formatters={

                "date":
                    lambda x:
                        x.strftime("%Y-%m"),

                "fees_usd":
                    lambda x:
                        f"${x:,.0f}",

                "revenue_usd":
                    lambda x:
                        f"${x:,.0f}",

                "take_rate_pct":
                    lambda x:
                        f"{x:.2f}%",

                "fees_growth_pct":
                    lambda x:
                        f"{x:+.2f}%",

                "revenue_growth_pct":
                    lambda x:
                        f"{x:+.2f}%",
            }
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading Aave fees and revenue..."
    )

    df = load_data()

    print(
        f"Loaded {len(df)} daily observations."
    )

    metrics = calculate_economics(df)

    monthly = calculate_monthly_economics(
        df
    )

    print_summary(
        metrics
    )

    print_monthly(
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