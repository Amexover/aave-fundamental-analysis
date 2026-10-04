import json

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

PROTOCOL_PATH = (
    "data/processed/lending_peer_analysis.csv"
)

TOKEN_PATH = (
    "data/raw/peer_token_data.json"
)

OUTPUT_PATH = (
    "data/processed/lending_peer_valuation.csv"
)


# ============================================================
# TOKEN -> PROTOCOL MAPPING
# ============================================================

TOKEN_TO_PROTOCOL = {
    "AAVE": "Aave",
    "MORPHO": "Morpho",
    "EUL": "Euler",
}


# ============================================================
# LOAD PROTOCOL DATA
# ============================================================

def load_protocol_data():

    df = pd.read_csv(
        PROTOCOL_PATH
    )

    return df


# ============================================================
# LOAD TOKEN DATA
# ============================================================

def load_token_data():

    with open(
        TOKEN_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        raw = json.load(file)

    rows = []

    for symbol, token in raw.items():

        if "error" in token:
            continue

        protocol = TOKEN_TO_PROTOCOL.get(
            symbol
        )

        if protocol is None:
            continue

        rows.append({
            "protocol":
                protocol,

            "token":
                symbol,

            "price_usd":
                token.get(
                    "price_usd"
                ),

            "market_cap_usd":
                token.get(
                    "market_cap_usd"
                ),

            "fdv_usd":
                token.get(
                    "fdv_usd"
                ),

            "circulating_supply":
                token.get(
                    "circulating_supply"
                ),

            "max_supply":
                token.get(
                    "max_supply"
                ),

            "circulating_ratio_pct":
                token.get(
                    "circulating_ratio_pct"
                ),

            "remaining_supply_pct":
                token.get(
                    "remaining_supply_pct"
                ),

            "fdv_premium_pct":
                token.get(
                    "fdv_premium_pct"
                ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# SAFE DIVISION
# ============================================================

def safe_divide(
    numerator,
    denominator,
):

    if pd.isna(numerator):
        return None

    if pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ============================================================
# MERGE DATA
# ============================================================

def merge_data(
    protocol_df,
    token_df,
):

    df = pd.merge(
        protocol_df,
        token_df,
        on="protocol",
        how="inner",
    )

    return df


# ============================================================
# CALCULATE VALUATION
# ============================================================

def calculate_valuation(df):

    df = df.copy()

    # --------------------------------------------------------
    # Market Cap / TVL
    # --------------------------------------------------------

    df["mcap_to_tvl"] = df.apply(
        lambda row:
            safe_divide(
                row["market_cap_usd"],
                row["tvl_usd"],
            ),
        axis=1,
    )

    df["fdv_to_tvl"] = df.apply(
        lambda row:
            safe_divide(
                row["fdv_usd"],
                row["tvl_usd"],
            ),
        axis=1,
    )

    # --------------------------------------------------------
    # Market Cap / annualized current fees
    # --------------------------------------------------------

    df[
        "mcap_to_annualized_fees"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["market_cap_usd"],
                row["annualized_fees_30d"],
            ),
        axis=1,
    )

    df[
        "fdv_to_annualized_fees"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["fdv_usd"],
                row["annualized_fees_30d"],
            ),
        axis=1,
    )

    # --------------------------------------------------------
    # Market Cap / trailing 1y fees
    # --------------------------------------------------------

    df[
        "mcap_to_fees_1y"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["market_cap_usd"],
                row["fees_1y"],
            ),
        axis=1,
    )

    df[
        "fdv_to_fees_1y"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["fdv_usd"],
                row["fees_1y"],
            ),
        axis=1,
    )

    # --------------------------------------------------------
    # Revenue valuation
    #
    # If revenue == 0, return N/A rather than infinity.
    # --------------------------------------------------------

    df[
        "mcap_to_annualized_revenue"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["market_cap_usd"],
                row["annualized_revenue_30d"],
            ),
        axis=1,
    )

    df[
        "fdv_to_annualized_revenue"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["fdv_usd"],
                row["annualized_revenue_30d"],
            ),
        axis=1,
    )

    df[
        "mcap_to_revenue_1y"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["market_cap_usd"],
                row["revenue_1y"],
            ),
        axis=1,
    )

    df[
        "fdv_to_revenue_1y"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["fdv_usd"],
                row["revenue_1y"],
            ),
        axis=1,
    )

    # --------------------------------------------------------
    # Implied yields
    # --------------------------------------------------------

    df[
        "annualized_fee_yield_pct"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["annualized_fees_30d"],
                row["market_cap_usd"],
            ),
        axis=1,
    )

    df[
        "annualized_revenue_yield_pct"
    ] = df.apply(
        lambda row:
            safe_divide(
                row["annualized_revenue_30d"],
                row["market_cap_usd"],
            ),
        axis=1,
    )

    df[
        "annualized_fee_yield_pct"
    ] *= 100

    df[
        "annualized_revenue_yield_pct"
    ] *= 100

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


def format_multiple(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}x"


def format_pct(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# PRINT MARKET VALUATION
# ============================================================

def print_market_valuation(df):

    print()
    print("==============================================")
    print("         LENDING PEER VALUATION")
    print("==============================================")

    print()
    print("=== MARKET VALUE ===")

    columns = [
        "protocol",
        "token",
        "market_cap_usd",
        "fdv_usd",
        "circulating_ratio_pct",
        "fdv_premium_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "market_cap_usd":
                    format_usd,

                "fdv_usd":
                    format_usd,

                "circulating_ratio_pct":
                    format_pct,

                "fdv_premium_pct":
                    format_pct,
            }
        )
    )


# ============================================================
# PRINT OPERATING VALUATION
# ============================================================

def print_operating_valuation(df):

    print()
    print("=== OPERATING VALUATION ===")

    columns = [
        "protocol",
        "mcap_to_tvl",
        "mcap_to_annualized_fees",
        "fdv_to_annualized_fees",
        "mcap_to_fees_1y",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "mcap_to_tvl":
                    format_multiple,

                "mcap_to_annualized_fees":
                    format_multiple,

                "fdv_to_annualized_fees":
                    format_multiple,

                "mcap_to_fees_1y":
                    format_multiple,
            }
        )
    )


# ============================================================
# PRINT REVENUE VALUATION
# ============================================================

def print_revenue_valuation(df):

    print()
    print("=== REVENUE VALUATION ===")

    columns = [
        "protocol",
        "mcap_to_annualized_revenue",
        "fdv_to_annualized_revenue",
        "mcap_to_revenue_1y",
        "fdv_to_revenue_1y",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "mcap_to_annualized_revenue":
                    format_multiple,

                "fdv_to_annualized_revenue":
                    format_multiple,

                "mcap_to_revenue_1y":
                    format_multiple,

                "fdv_to_revenue_1y":
                    format_multiple,
            }
        )
    )


# ============================================================
# PRINT IMPLIED YIELDS
# ============================================================

def print_yields(df):

    print()
    print("=== IMPLIED ECONOMIC YIELDS ===")

    columns = [
        "protocol",
        "annualized_fee_yield_pct",
        "annualized_revenue_yield_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={

                "annualized_fee_yield_pct":
                    format_pct,

                "annualized_revenue_yield_pct":
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
        "1. Market Cap / Fees measures token valuation "
        "relative to protocol economic activity."
    )

    print(
        "2. Fees are NOT tokenholder earnings."
    )

    print(
        "3. Revenue multiples are only meaningful when "
        "the protocol actively captures revenue."
    )

    print(
        "4. Morpho currently reports zero protocol "
        "revenue in the dataset, so revenue multiples "
        "are intentionally shown as N/A."
    )

    print(
        "5. Euler revenue metrics should be interpreted "
        "with caution because protocol monetization "
        "has changed over time."
    )

    print(
        "6. FDV-based multiples are especially important "
        "for tokens with significant future dilution."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading lending peer valuation data..."
    )

    protocol_df = (
        load_protocol_data()
    )

    token_df = (
        load_token_data()
    )

    df = merge_data(
        protocol_df,
        token_df,
    )

    df = calculate_valuation(
        df
    )

    df = (
        df
        .sort_values(
            "market_cap_usd",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    save_data(
        df
    )

    print_market_valuation(
        df
    )

    print_operating_valuation(
        df
    )

    print_revenue_valuation(
        df
    )

    print_yields(
        df
    )

    print_notes()

    print()
    print(
        "PEER VALUATION FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()