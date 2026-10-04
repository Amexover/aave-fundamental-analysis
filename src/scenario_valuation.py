import json

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

TOKEN_PATH = (
    "data/raw/aave_token_data.json"
)

REVENUE_PATH = (
    "data/raw/aave_revenue.csv"
)


# ============================================================
# SCENARIO ASSUMPTIONS
# ============================================================

SCENARIOS = {
    "Bear": {
        "revenue_usd": 50_000_000,
        "revenue_multiple": 20.0,
    },

    "Base": {
        "revenue_usd": 100_000_000,
        "revenue_multiple": 30.0,
    },

    "Bull": {
        "revenue_usd": 150_000_000,
        "revenue_multiple": 35.0,
    },
}


# ============================================================
# LOAD TOKEN DATA
# ============================================================

def load_token_data():

    with open(
        TOKEN_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        token = json.load(file)

    return token


# ============================================================
# LOAD REVENUE DATA
# ============================================================

def load_revenue_data():

    df = pd.read_csv(
        REVENUE_PATH,
        parse_dates=["date"],
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
# CURRENT ECONOMICS
# ============================================================

def calculate_current_metrics(
    token,
    revenue_df,
):

    current_price = token[
        "price_usd"
    ]

    market_cap = token[
        "market_cap_usd"
    ]

    circulating_supply = token[
        "circulating_supply"
    ]

    max_supply = token[
        "max_supply"
    ]

    revenue_30d = trailing_sum(
        revenue_df,
        "revenue_usd",
        30,
    )

    revenue_ttm = trailing_sum(
        revenue_df,
        "revenue_usd",
        365,
    )

    revenue_run_rate = (
        revenue_30d
        / 30
        * 365
    )

    current_run_rate_multiple = (
        market_cap
        / revenue_run_rate
    )

    current_ttm_multiple = (
        market_cap
        / revenue_ttm
    )

    return {
        "current_price":
            current_price,

        "market_cap":
            market_cap,

        "circulating_supply":
            circulating_supply,

        "max_supply":
            max_supply,

        "revenue_30d":
            revenue_30d,

        "revenue_ttm":
            revenue_ttm,

        "revenue_run_rate":
            revenue_run_rate,

        "current_run_rate_multiple":
            current_run_rate_multiple,

        "current_ttm_multiple":
            current_ttm_multiple,
    }


# ============================================================
# CALCULATE SCENARIOS
# ============================================================

def calculate_scenarios(
    current_metrics,
):

    rows = []

    current_price = current_metrics[
        "current_price"
    ]

    circulating_supply = current_metrics[
        "circulating_supply"
    ]

    for scenario, assumptions in (
        SCENARIOS.items()
    ):

        revenue = assumptions[
            "revenue_usd"
        ]

        multiple = assumptions[
            "revenue_multiple"
        ]

        # ----------------------------------------------------
        # Implied valuation
        # ----------------------------------------------------

        implied_market_cap = (
            revenue
            * multiple
        )

        implied_price = (
            implied_market_cap
            / circulating_supply
        )

        # ----------------------------------------------------
        # Upside / downside
        # ----------------------------------------------------

        price_return = (
            implied_price
            / current_price
            - 1
        ) * 100

        # ----------------------------------------------------
        # Revenue change vs current run-rate
        # ----------------------------------------------------

        revenue_change_vs_run_rate = (
            revenue
            / current_metrics[
                "revenue_run_rate"
            ]
            - 1
        ) * 100

        # ----------------------------------------------------
        # Revenue change vs TTM
        # ----------------------------------------------------

        revenue_change_vs_ttm = (
            revenue
            / current_metrics[
                "revenue_ttm"
            ]
            - 1
        ) * 100

        rows.append({
            "scenario":
                scenario,

            "revenue_usd":
                revenue,

            "revenue_multiple":
                multiple,

            "implied_market_cap":
                implied_market_cap,

            "implied_price":
                implied_price,

            "price_return_pct":
                price_return,

            "revenue_change_vs_run_rate_pct":
                revenue_change_vs_run_rate,

            "revenue_change_vs_ttm_pct":
                revenue_change_vs_ttm,
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# SENSITIVITY TABLE
# ============================================================

def build_sensitivity_table(
    circulating_supply,
):

    revenue_levels = [
        50_000_000,
        75_000_000,
        100_000_000,
        125_000_000,
        150_000_000,
        175_000_000,
        200_000_000,
    ]

    multiples = [
        15,
        20,
        25,
        30,
        35,
        40,
        45,
    ]

    table = pd.DataFrame(
        index=[
            f"${revenue / 1_000_000:.0f}M"
            for revenue in revenue_levels
        ],
        columns=[
            f"{multiple}x"
            for multiple in multiples
        ],
    )

    for revenue in revenue_levels:

        for multiple in multiples:

            implied_market_cap = (
                revenue
                * multiple
            )

            implied_price = (
                implied_market_cap
                / circulating_supply
            )

            table.loc[
                f"${revenue / 1_000_000:.0f}M",
                f"{multiple}x",
            ] = implied_price

    return table.astype(float)


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

    return f"${value:,.2f}"


def format_pct(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:+.2f}%"


def format_multiple(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}x"


# ============================================================
# PRINT CURRENT VALUATION
# ============================================================

def print_current_metrics(metrics):

    print()
    print("==============================================")
    print("          AAVE CURRENT VALUATION")
    print("==============================================")

    print(
        f"Current Price: "
        f"${metrics['current_price']:,.2f}"
    )

    print(
        f"Market Cap: "
        f"{format_usd(metrics['market_cap'])}"
    )

    print()
    print("=== REVENUE ===")

    print(
        f"TTM Revenue: "
        f"{format_usd(metrics['revenue_ttm'])}"
    )

    print(
        f"Annualized 30d Revenue: "
        f"{format_usd(metrics['revenue_run_rate'])}"
    )

    print()
    print("=== CURRENT MULTIPLES ===")

    print(
        f"MCap / TTM Revenue: "
        f"{format_multiple(metrics['current_ttm_multiple'])}"
    )

    print(
        f"MCap / Current Revenue Run-rate: "
        f"{format_multiple(metrics['current_run_rate_multiple'])}"
    )


# ============================================================
# PRINT SCENARIOS
# ============================================================

def print_scenarios(df):

    print()
    print("==============================================")
    print("          AAVE VALUATION SCENARIOS")
    print("==============================================")

    columns = [
        "scenario",
        "revenue_usd",
        "revenue_multiple",
        "implied_market_cap",
        "implied_price",
        "price_return_pct",
        "revenue_change_vs_run_rate_pct",
        "revenue_change_vs_ttm_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "revenue_usd":
                    format_usd,

                "revenue_multiple":
                    format_multiple,

                "implied_market_cap":
                    format_usd,

                "implied_price":
                    lambda x:
                        f"${x:,.2f}",

                "price_return_pct":
                    format_pct,

                "revenue_change_vs_run_rate_pct":
                    format_pct,

                "revenue_change_vs_ttm_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT SENSITIVITY TABLE
# ============================================================

def print_sensitivity_table(table):

    print()
    print("==============================================")
    print("      IMPLIED AAVE PRICE SENSITIVITY")
    print("==============================================")

    print()
    print(
        "Rows = Annual Protocol Revenue"
    )

    print(
        "Columns = Revenue Multiple"
    )

    print()

    print(
        table.to_string(
            formatters={
                column:
                    lambda x:
                        f"${x:,.0f}"
                for column in table.columns
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
        "1. Scenario revenue represents normalized "
        "annual protocol revenue."
    )

    print(
        "2. Revenue multiple is an analytical "
        "assumption, not an observed market fact."
    )

    print(
        "3. Implied token price uses current "
        "circulating supply."
    )

    print(
        "4. Protocol revenue is not equivalent "
        "to tokenholder earnings."
    )

    print(
        "5. Buybacks, dilution, treasury policy "
        "and governance should be analyzed "
        "separately from this revenue model."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading AAVE scenario valuation..."
    )

    token = load_token_data()

    revenue_df = (
        load_revenue_data()
    )

    current_metrics = (
        calculate_current_metrics(
            token,
            revenue_df,
        )
    )

    scenarios = (
        calculate_scenarios(
            current_metrics
        )
    )

    sensitivity = (
        build_sensitivity_table(
            current_metrics[
                "circulating_supply"
            ]
        )
    )

    print_current_metrics(
        current_metrics
    )

    print_scenarios(
        scenarios
    )

    print_sensitivity_table(
        sensitivity
    )

    print_notes()

    print()
    print(
        "SCENARIO VALUATION FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()