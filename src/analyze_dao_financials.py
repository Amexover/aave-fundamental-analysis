import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

FINANCIALS_PATH = (
    "data/raw/aave_dao_financials.csv"
)

TOKEN_PATH = (
    "data/raw/aave_token_data.json"
)

OUTPUT_PATH = (
    "data/processed/aave_dao_financial_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_financials():

    df = pd.read_csv(
        FINANCIALS_PATH
    )

    return df


def load_token_data():

    with open(
        TOKEN_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        token = json.load(file)

    return token


# ============================================================
# CALCULATE FINANCIAL METRICS
# ============================================================

def calculate_financial_metrics(df):

    df = df.copy()

    # --------------------------------------------------------
    # Expense ratio
    # --------------------------------------------------------

    df["expense_ratio_pct"] = (
        df["expenses_usd"]
        / df["revenue_usd"]
        * 100
    )

    # --------------------------------------------------------
    # Net margin
    # --------------------------------------------------------

    df["net_margin_pct"] = (
        df["net_income_usd"]
        / df["revenue_usd"]
        * 100
    )

    # --------------------------------------------------------
    # Revenue retained after expenses
    # --------------------------------------------------------

    df["revenue_retention_pct"] = (
        100
        - df["expense_ratio_pct"]
    )

    return df


# ============================================================
# CALCULATE GROWTH
# ============================================================

def calculate_ytd_comparison(df):

    full_year = df[
        df["period_type"] == "full_year"
    ]

    ytd = df[
        df["period_type"] == "ytd"
    ]

    if full_year.empty or ytd.empty:

        return None

    previous = full_year.iloc[-1]
    current = ytd.iloc[-1]

    return {
        "ytd_revenue_vs_previous_full_year_pct":
            (
                current["revenue_usd"]
                / previous["revenue_usd"]
                * 100
            ),

        "ytd_expenses_vs_previous_full_year_pct":
            (
                current["expenses_usd"]
                / previous["expenses_usd"]
                * 100
            ),

        "ytd_net_income_vs_previous_full_year_pct":
            (
                current["net_income_usd"]
                / previous["net_income_usd"]
                * 100
            ),

        "net_margin_change_pp":
            (
                current["net_margin_pct"]
                - previous["net_margin_pct"]
            ),
    }


# ============================================================
# VALUATION
# ============================================================

def calculate_valuation(
    df,
    token,
):

    df = df.copy()

    market_cap = token[
        "market_cap_usd"
    ]

    fdv = token[
        "fdv_usd"
    ]

    df["mcap_to_revenue"] = (
        market_cap
        / df["revenue_usd"]
    )

    df["mcap_to_net_income"] = (
        market_cap
        / df["net_income_usd"]
    )

    df["fdv_to_net_income"] = (
        fdv
        / df["net_income_usd"]
    )

    df["net_income_yield_pct"] = (
        df["net_income_usd"]
        / market_cap
        * 100
    )

    return df


# ============================================================
# BUYBACK CAPACITY
# ============================================================

def calculate_buyback_capacity(
    df,
    token,
):

    df = df.copy()

    price = token[
        "price_usd"
    ]

    circulating_supply = token[
        "circulating_supply"
    ]

    allocation_levels = [
        0.25,
        0.50,
        0.75,
        1.00,
    ]

    results = []

    for _, row in df.iterrows():

        for allocation in allocation_levels:

            buyback_usd = (
                row["net_income_usd"]
                * allocation
            )

            aave_bought = (
                buyback_usd
                / price
            )

            circulating_supply_pct = (
                aave_bought
                / circulating_supply
                * 100
            )

            results.append({
                "period":
                    row["period"],

                "allocation_pct":
                    allocation * 100,

                "buyback_usd":
                    buyback_usd,

                "aave_bought":
                    aave_bought,

                "circulating_supply_pct":
                    circulating_supply_pct,
            })

    return pd.DataFrame(
        results
    )


# ============================================================
# NORMALIZED NET INCOME SCENARIOS
# ============================================================

def build_net_income_sensitivity(
    token,
):

    market_cap = token[
        "market_cap_usd"
    ]

    net_income_levels = [
        25_000_000,
        40_000_000,
        50_000_000,
        75_000_000,
        100_000_000,
        125_000_000,
        150_000_000,
    ]

    rows = []

    for net_income in net_income_levels:

        multiple = (
            market_cap
            / net_income
        )

        yield_pct = (
            net_income
            / market_cap
            * 100
        )

        rows.append({
            "normalized_net_income":
                net_income,

            "mcap_to_net_income":
                multiple,

            "net_income_yield_pct":
                yield_pct,
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# SAVE
# ============================================================

def save_data(df):

    output = Path(
        OUTPUT_PATH
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output,
        index=False,
    )

    print()
    print(
        f"CSV saved to: {OUTPUT_PATH}"
    )


# ============================================================
# FORMAT HELPERS
# ============================================================

def format_usd(value):

    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000_000:

        return (
            f"${value / 1_000_000_000:.2f}B"
        )

    if abs(value) >= 1_000_000:

        return (
            f"${value / 1_000_000:.2f}M"
        )

    return f"${value:,.0f}"


def format_pct(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def format_signed_pct(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:+.2f}%"


def format_multiple(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}x"


# ============================================================
# PRINT FINANCIALS
# ============================================================

def print_financials(df):

    print()
    print("==============================================")
    print("           AAVE DAO FINANCIALS")
    print("==============================================")

    columns = [
        "period",
        "revenue_usd",
        "expenses_usd",
        "net_income_usd",
        "expense_ratio_pct",
        "net_margin_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "revenue_usd":
                    format_usd,

                "expenses_usd":
                    format_usd,

                "net_income_usd":
                    format_usd,

                "expense_ratio_pct":
                    format_pct,

                "net_margin_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT YTD COMPARISON
# ============================================================

def print_ytd_comparison(
    comparison
):

    if comparison is None:
        return

    print()
    print("=== 2026 YTD VS 2025 FULL YEAR ===")

    print(
        "Revenue already generated: "
        f"{comparison['ytd_revenue_vs_previous_full_year_pct']:.2f}%"
    )

    print(
        "Expenses already incurred: "
        f"{comparison['ytd_expenses_vs_previous_full_year_pct']:.2f}%"
    )

    print(
        "Net income already generated: "
        f"{comparison['ytd_net_income_vs_previous_full_year_pct']:.2f}%"
    )

    print(
        "Net margin change: "
        f"{comparison['net_margin_change_pp']:+.2f} pp"
    )


# ============================================================
# PRINT VALUATION
# ============================================================

def print_valuation(df):

    print()
    print("=== DAO ECONOMIC VALUATION ===")

    columns = [
        "period",
        "mcap_to_revenue",
        "mcap_to_net_income",
        "fdv_to_net_income",
        "net_income_yield_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "mcap_to_revenue":
                    format_multiple,

                "mcap_to_net_income":
                    format_multiple,

                "fdv_to_net_income":
                    format_multiple,

                "net_income_yield_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT BUYBACK CAPACITY
# ============================================================

def print_buyback_capacity(df):

    print()
    print("=== THEORETICAL BUYBACK CAPACITY ===")

    print(
        "This is a scenario analysis, "
        "not a forecast of actual buybacks."
    )

    print()

    columns = [
        "period",
        "allocation_pct",
        "buyback_usd",
        "aave_bought",
        "circulating_supply_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "allocation_pct":
                    format_pct,

                "buyback_usd":
                    format_usd,

                "aave_bought":
                    lambda x:
                        f"{x:,.0f}",

                "circulating_supply_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT NET INCOME SENSITIVITY
# ============================================================

def print_net_income_sensitivity(df):

    print()
    print("=== NORMALIZED DAO NET INCOME ===")

    columns = [
        "normalized_net_income",
        "mcap_to_net_income",
        "net_income_yield_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "normalized_net_income":
                    format_usd,

                "mcap_to_net_income":
                    format_multiple,

                "net_income_yield_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT NOTES
# ============================================================

def print_notes():

    print()
    print("==============================================")
    print("                    NOTES")
    print("==============================================")

    print(
        "1. DAO net income is more economically "
        "meaningful than gross protocol revenue "
        "for token valuation."
    )

    print(
        "2. DAO net income is NOT equivalent "
        "to AAVE tokenholder earnings."
    )

    print(
        "3. Buyback capacity assumes hypothetical "
        "allocation of net income."
    )

    print(
        "4. Actual capital allocation is determined "
        "through governance."
    )

    print(
        "5. 2026 data is YTD and must not be compared "
        "directly with a full-year period as if both "
        "covered equal time intervals."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading Aave DAO financials..."
    )

    financials = (
        load_financials()
    )

    token = (
        load_token_data()
    )

    financials = (
        calculate_financial_metrics(
            financials
        )
    )

    comparison = (
        calculate_ytd_comparison(
            financials
        )
    )

    financials = (
        calculate_valuation(
            financials,
            token,
        )
    )

    buyback_capacity = (
        calculate_buyback_capacity(
            financials,
            token,
        )
    )

    sensitivity = (
        build_net_income_sensitivity(
            token
        )
    )

    save_data(
        financials
    )

    print_financials(
        financials
    )

    print_ytd_comparison(
        comparison
    )

    print_valuation(
        financials
    )

    print_buyback_capacity(
        buyback_capacity
    )

    print_net_income_sensitivity(
        sensitivity
    )

    print_notes()

    print()
    print(
        "DAO FINANCIAL ANALYSIS FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()