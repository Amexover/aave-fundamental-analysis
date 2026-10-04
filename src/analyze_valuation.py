import json

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

TOKEN_PATH = "data/raw/aave_token_data.json"
FEES_PATH = "data/raw/aave_fees_revenue.csv"
REVENUE_PATH = "data/raw/aave_revenue.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_token_data():

    with open(
        TOKEN_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        token = json.load(file)

    return token


def load_protocol_data():

    fees = pd.read_csv(
        FEES_PATH,
        parse_dates=["date"],
    )

    revenue = pd.read_csv(
        REVENUE_PATH,
        parse_dates=["date"],
    )

    df = pd.merge(
        fees,
        revenue,
        on="date",
        how="inner",
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
    days,
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
# CALCULATE VALUATION
# ============================================================

def calculate_valuation(
    token,
    df,
):

    market_cap = token[
        "market_cap_usd"
    ]

    fdv = token[
        "fdv_usd"
    ]

    circulating_supply = token[
        "circulating_supply"
    ]

    max_supply = token[
        "max_supply"
    ]

    # --------------------------------------------------------
    # Historical protocol economics
    # --------------------------------------------------------

    fees_ttm = trailing_sum(
        df,
        "fees_usd",
        365,
    )

    revenue_ttm = trailing_sum(
        df,
        "revenue_usd",
        365,
    )

    fees_30d = trailing_sum(
        df,
        "fees_usd",
        30,
    )

    revenue_30d = trailing_sum(
        df,
        "revenue_usd",
        30,
    )

    # --------------------------------------------------------
    # Current annualized run-rate
    # --------------------------------------------------------

    fees_run_rate = (
        fees_30d
        / 30
        * 365
    )

    revenue_run_rate = (
        revenue_30d
        / 30
        * 365
    )

    # --------------------------------------------------------
    # Valuation multiples
    # --------------------------------------------------------

    market_cap_to_fees_ttm = (
        market_cap
        / fees_ttm
    )

    market_cap_to_revenue_ttm = (
        market_cap
        / revenue_ttm
    )

    fdv_to_revenue_ttm = (
        fdv
        / revenue_ttm
    )

    market_cap_to_fees_run_rate = (
        market_cap
        / fees_run_rate
    )

    market_cap_to_revenue_run_rate = (
        market_cap
        / revenue_run_rate
    )

    # --------------------------------------------------------
    # Yields
    # --------------------------------------------------------

    fee_yield_ttm = (
        fees_ttm
        / market_cap
        * 100
    )

    revenue_yield_ttm = (
        revenue_ttm
        / market_cap
        * 100
    )

    revenue_yield_run_rate = (
        revenue_run_rate
        / market_cap
        * 100
    )

    # --------------------------------------------------------
    # Supply / dilution
    # --------------------------------------------------------

    circulating_ratio = (
        circulating_supply
        / max_supply
        * 100
    )

    remaining_supply = (
        max_supply
        - circulating_supply
    )

    remaining_supply_pct = (
        remaining_supply
        / max_supply
        * 100
    )

    fdv_premium = (
        fdv
        / market_cap
        - 1
    ) * 100

    return {
        "market_cap": market_cap,
        "fdv": fdv,

        "fees_ttm": fees_ttm,
        "revenue_ttm": revenue_ttm,

        "fees_run_rate": fees_run_rate,
        "revenue_run_rate": revenue_run_rate,

        "market_cap_to_fees_ttm":
            market_cap_to_fees_ttm,

        "market_cap_to_revenue_ttm":
            market_cap_to_revenue_ttm,

        "fdv_to_revenue_ttm":
            fdv_to_revenue_ttm,

        "market_cap_to_fees_run_rate":
            market_cap_to_fees_run_rate,

        "market_cap_to_revenue_run_rate":
            market_cap_to_revenue_run_rate,

        "fee_yield_ttm":
            fee_yield_ttm,

        "revenue_yield_ttm":
            revenue_yield_ttm,

        "revenue_yield_run_rate":
            revenue_yield_run_rate,

        "circulating_ratio":
            circulating_ratio,

        "remaining_supply":
            remaining_supply,

        "remaining_supply_pct":
            remaining_supply_pct,

        "fdv_premium":
            fdv_premium,
    }


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    token,
    metrics,
):

    print()
    print("==============================================")
    print("               AAVE VALUATION")
    print("==============================================")

    print()
    print("=== TOKEN ===")

    print(
        f"Price: "
        f"${token['price_usd']:,.2f}"
    )

    print(
        f"Market Cap: "
        f"${metrics['market_cap']:,.0f}"
    )

    print(
        f"FDV: "
        f"${metrics['fdv']:,.0f}"
    )

    print()
    print("=== PROTOCOL ECONOMICS ===")

    print(
        f"TTM Fees: "
        f"${metrics['fees_ttm']:,.0f}"
    )

    print(
        f"TTM Revenue: "
        f"${metrics['revenue_ttm']:,.0f}"
    )

    print(
        f"Annualized 30d Fees: "
        f"${metrics['fees_run_rate']:,.0f}"
    )

    print(
        f"Annualized 30d Revenue: "
        f"${metrics['revenue_run_rate']:,.0f}"
    )

    print()
    print("=== TRAILING VALUATION ===")

    print(
        f"Market Cap / TTM Fees: "
        f"{metrics['market_cap_to_fees_ttm']:.2f}x"
    )

    print(
        f"Market Cap / TTM Revenue: "
        f"{metrics['market_cap_to_revenue_ttm']:.2f}x"
    )

    print(
        f"FDV / TTM Revenue: "
        f"{metrics['fdv_to_revenue_ttm']:.2f}x"
    )

    print()
    print("=== CURRENT RUN-RATE VALUATION ===")

    print(
        f"Market Cap / Annualized Fees: "
        f"{metrics['market_cap_to_fees_run_rate']:.2f}x"
    )

    print(
        f"Market Cap / Annualized Revenue: "
        f"{metrics['market_cap_to_revenue_run_rate']:.2f}x"
    )

    print()
    print("=== IMPLIED YIELDS ===")

    print(
        f"TTM Fee Yield: "
        f"{metrics['fee_yield_ttm']:.2f}%"
    )

    print(
        f"TTM Revenue Yield: "
        f"{metrics['revenue_yield_ttm']:.2f}%"
    )

    print(
        f"Current Revenue Run-rate Yield: "
        f"{metrics['revenue_yield_run_rate']:.2f}%"
    )

    print()
    print("=== SUPPLY / DILUTION ===")

    print(
        f"Circulating / Max Supply: "
        f"{metrics['circulating_ratio']:.2f}%"
    )

    print(
        f"Remaining Supply: "
        f"{metrics['remaining_supply']:,.0f} AAVE"
    )

    print(
        f"Remaining Supply %: "
        f"{metrics['remaining_supply_pct']:.2f}%"
    )

    print(
        f"FDV Premium to Market Cap: "
        f"{metrics['fdv_premium']:.2f}%"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading AAVE valuation data..."
    )

    token = load_token_data()

    df = load_protocol_data()

    print(
        f"Loaded {len(df)} daily protocol observations."
    )

    metrics = calculate_valuation(
        token,
        df,
    )

    print_results(
        token,
        metrics,
    )

    print()
    print(
        "VALUATION ANALYSIS FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()