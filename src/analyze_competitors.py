import json

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

INPUT_PATH = (
    "data/raw/competitor_protocol_data.json"
)

OUTPUT_PATH = (
    "data/processed/lending_peer_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data


# ============================================================
# SAFE DIVISION
# ============================================================

def safe_divide(
    numerator,
    denominator,
):

    if numerator is None:
        return None

    if denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ============================================================
# BUILD PEER DATAFRAME
# ============================================================

def build_peer_dataframe(data):

    rows = []

    for name, protocol in data.items():

        if "error" in protocol:
            continue

        tvl = protocol[
            "tvl_usd"
        ]

        fees_30d = protocol[
            "fees"
        ]["30d"]

        fees_1y = protocol[
            "fees"
        ]["1y"]

        revenue_30d = protocol[
            "revenue"
        ]["30d"]

        revenue_1y = protocol[
            "revenue"
        ]["1y"]

        # ----------------------------------------------------
        # Annualized current run-rate
        # ----------------------------------------------------

        annualized_fees_30d = (
            fees_30d
            / 30
            * 365
        )

        annualized_revenue_30d = (
            revenue_30d
            / 30
            * 365
        )

        # ----------------------------------------------------
        # Take rates
        # ----------------------------------------------------

        take_rate_30d = safe_divide(
            revenue_30d,
            fees_30d,
        )

        take_rate_1y = safe_divide(
            revenue_1y,
            fees_1y,
        )

        if take_rate_30d is not None:
            take_rate_30d *= 100

        if take_rate_1y is not None:
            take_rate_1y *= 100

        # ----------------------------------------------------
        # Current capital efficiency
        #
        # IMPORTANT:
        # Annualized 30d flows / current TVL are more
        # internally consistent than 1y flows / current TVL.
        # ----------------------------------------------------

        annualized_fee_tvl = safe_divide(
            annualized_fees_30d,
            tvl,
        )

        annualized_revenue_tvl = safe_divide(
            annualized_revenue_30d,
            tvl,
        )

        if annualized_fee_tvl is not None:
            annualized_fee_tvl *= 100

        if annualized_revenue_tvl is not None:
            annualized_revenue_tvl *= 100

        # ----------------------------------------------------
        # Historical vs current activity
        #
        # Compare current annualized 30d run-rate with
        # trailing 1y flows.
        # ----------------------------------------------------

        fees_run_rate_vs_1y = safe_divide(
            annualized_fees_30d,
            fees_1y,
        )

        revenue_run_rate_vs_1y = safe_divide(
            annualized_revenue_30d,
            revenue_1y,
        )

        if fees_run_rate_vs_1y is not None:
            fees_run_rate_vs_1y = (
                fees_run_rate_vs_1y
                - 1
            ) * 100

        if revenue_run_rate_vs_1y is not None:
            revenue_run_rate_vs_1y = (
                revenue_run_rate_vs_1y
                - 1
            ) * 100

        # ----------------------------------------------------
        # Build row
        # ----------------------------------------------------

        row = {
            "protocol":
                name.capitalize(),

            "tvl_usd":
                tvl,

            "fees_30d":
                fees_30d,

            "fees_1y":
                fees_1y,

            "revenue_30d":
                revenue_30d,

            "revenue_1y":
                revenue_1y,

            "annualized_fees_30d":
                annualized_fees_30d,

            "annualized_revenue_30d":
                annualized_revenue_30d,

            "take_rate_30d_pct":
                take_rate_30d,

            "take_rate_1y_pct":
                take_rate_1y,

            "annualized_fee_tvl_pct":
                annualized_fee_tvl,

            "annualized_revenue_tvl_pct":
                annualized_revenue_tvl,

            "fees_run_rate_vs_1y_pct":
                fees_run_rate_vs_1y,

            "revenue_run_rate_vs_1y_pct":
                revenue_run_rate_vs_1y,
        }

        rows.append(row)

    df = pd.DataFrame(
        rows
    )

    return df


# ============================================================
# ADD RELATIVE SCALE
# ============================================================

def add_relative_scale(df):

    df = df.copy()

    aave_row = df[
        df["protocol"] == "Aave"
    ]

    if aave_row.empty:
        return df

    aave_tvl = (
        aave_row[
            "tvl_usd"
        ]
        .iloc[0]
    )

    aave_fees = (
        aave_row[
            "annualized_fees_30d"
        ]
        .iloc[0]
    )

    aave_revenue = (
        aave_row[
            "annualized_revenue_30d"
        ]
        .iloc[0]
    )

    df["tvl_vs_aave_pct"] = (
        df["tvl_usd"]
        / aave_tvl
        * 100
    )

    df["fees_vs_aave_pct"] = (
        df["annualized_fees_30d"]
        / aave_fees
        * 100
    )

    df["revenue_vs_aave_pct"] = (
        df["annualized_revenue_30d"]
        / aave_revenue
        * 100
    )

    return df


# ============================================================
# SAVE DATA
# ============================================================

def save_data(df):

    from pathlib import Path

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

    if abs(value) >= 1_000:

        return (
            f"${value / 1_000:.2f}K"
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


# ============================================================
# PRINT MAIN PEER TABLE
# ============================================================

def print_peer_table(df):

    print()
    print("==============================================")
    print("        DEFI LENDING PEER ANALYSIS")
    print("==============================================")

    print()
    print("=== SCALE & ECONOMICS ===")

    columns = [
        "protocol",
        "tvl_usd",
        "fees_30d",
        "revenue_30d",
        "annualized_fees_30d",
        "annualized_revenue_30d",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "tvl_usd":
                    format_usd,

                "fees_30d":
                    format_usd,

                "revenue_30d":
                    format_usd,

                "annualized_fees_30d":
                    format_usd,

                "annualized_revenue_30d":
                    format_usd,
            }
        )
    )


# ============================================================
# PRINT MONETIZATION
# ============================================================

def print_monetization(df):

    print()
    print("=== MONETIZATION ===")

    columns = [
        "protocol",
        "take_rate_30d_pct",
        "take_rate_1y_pct",
        "annualized_fee_tvl_pct",
        "annualized_revenue_tvl_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "take_rate_30d_pct":
                    format_pct,

                "take_rate_1y_pct":
                    format_pct,

                "annualized_fee_tvl_pct":
                    format_pct,

                "annualized_revenue_tvl_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT MOMENTUM
# ============================================================

def print_momentum(df):

    print()
    print("=== CURRENT RUN-RATE VS TRAILING 1Y ===")

    columns = [
        "protocol",
        "fees_run_rate_vs_1y_pct",
        "revenue_run_rate_vs_1y_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "fees_run_rate_vs_1y_pct":
                    format_signed_pct,

                "revenue_run_rate_vs_1y_pct":
                    format_signed_pct,
            }
        )
    )


# ============================================================
# PRINT RELATIVE SCALE
# ============================================================

def print_relative_scale(df):

    print()
    print("=== RELATIVE SCALE — AAVE = 100% ===")

    columns = [
        "protocol",
        "tvl_vs_aave_pct",
        "fees_vs_aave_pct",
        "revenue_vs_aave_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "tvl_vs_aave_pct":
                    format_pct,

                "fees_vs_aave_pct":
                    format_pct,

                "revenue_vs_aave_pct":
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
        "1. Annualized 30d metrics represent the "
        "current run-rate, not realized annual results."
    )

    print(
        "2. Annualized fee/revenue to TVL uses current "
        "TVL and the latest 30d annualized flow."
    )

    print(
        "3. Morpho revenue may be zero because protocol "
        "monetization differs from Aave and Euler."
    )

    print(
        "4. Revenue metrics should not be interpreted "
        "as tokenholder earnings."
    )

    print(
        "5. Peer valuation should only be added after "
        "token value-accrual mechanisms are reviewed."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading competitor protocol data..."
    )

    data = load_data()

    df = build_peer_dataframe(
        data
    )

    df = add_relative_scale(
        df
    )

    df = (
        df
        .sort_values(
            "tvl_usd",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    save_data(
        df
    )

    print_peer_table(
        df
    )

    print_monetization(
        df
    )

    print_momentum(
        df
    )

    print_relative_scale(
        df
    )

    print_notes()

    print()
    print(
        "COMPETITOR ANALYSIS FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()