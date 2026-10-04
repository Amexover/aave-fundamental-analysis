import pandas as pd


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "data/raw/aave_ethereum_reserves.csv"


# ============================================================
# 1. LOAD DATA
# ============================================================

def load_data():
    """
    Load reserve-level Aave V3 Ethereum dataset
    created by fetch_aave.py.
    """

    df = pd.read_csv(DATA_PATH)

    return df


# ============================================================
# 2. PREPARE DATA
# ============================================================

def prepare_data(df):
    """
    Clean dataset and calculate additional
    analytical metrics.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Borrow share
    # --------------------------------------------------------
    #
    # Shows what percentage of all borrowing
    # comes from each reserve.

    total_borrowed = df["borrowed_usd"].sum()

    if total_borrowed > 0:
        df["borrow_share_pct"] = (
            df["borrowed_usd"]
            / total_borrowed
            * 100
        )
    else:
        df["borrow_share_pct"] = 0.0

    # --------------------------------------------------------
    # Supply share
    # --------------------------------------------------------
    #
    # Shows each reserve's share of supplied capital.
    #
    # Some supply-only assets have supplied_usd = NaN
    # in our current dataset, so they are excluded here.

    total_supplied = df["supplied_usd"].sum()

    if total_supplied > 0:
        df["supply_share_pct"] = (
            df["supplied_usd"]
            / total_supplied
            * 100
        )
    else:
        df["supply_share_pct"] = 0.0

    # --------------------------------------------------------
    # Protocol interest share
    # --------------------------------------------------------
    #
    # Shows which reserves contribute the most
    # to our estimated protocol interest.

    total_protocol_interest = (
        df["estimated_protocol_interest"].sum()
    )

    if total_protocol_interest > 0:
        df["protocol_interest_share_pct"] = (
            df["estimated_protocol_interest"]
            / total_protocol_interest
            * 100
        )
    else:
        df["protocol_interest_share_pct"] = 0.0

    return df


# ============================================================
# 3. CONCENTRATION ANALYSIS
# ============================================================

def concentration_analysis(df):
    """
    Measure concentration of borrowing activity.
    """

    sorted_df = df.sort_values(
        "borrowed_usd",
        ascending=False
    )

    total_borrowed = sorted_df[
        "borrowed_usd"
    ].sum()

    if total_borrowed == 0:
        return {
            "top1_share": 0,
            "top3_share": 0,
            "top5_share": 0,
            "top10_share": 0,
        }

    top1_share = (
        sorted_df.head(1)["borrowed_usd"].sum()
        / total_borrowed
        * 100
    )

    top3_share = (
        sorted_df.head(3)["borrowed_usd"].sum()
        / total_borrowed
        * 100
    )

    top5_share = (
        sorted_df.head(5)["borrowed_usd"].sum()
        / total_borrowed
        * 100
    )

    top10_share = (
        sorted_df.head(10)["borrowed_usd"].sum()
        / total_borrowed
        * 100
    )

    return {
        "top1_share": top1_share,
        "top3_share": top3_share,
        "top5_share": top5_share,
        "top10_share": top10_share,
    }


# ============================================================
# 4. CAPITAL EFFICIENCY ANALYSIS
# ============================================================

def capital_efficiency_analysis(df):
    """
    Compare supplied capital with actual borrowing activity.
    """

    # Ignore reserves where supplied USD
    # is currently unavailable.
    analysis_df = df.dropna(
        subset=["supplied_usd"]
    ).copy()

    # Ignore tiny reserves to prevent economically
    # irrelevant markets from dominating rankings.
    major_reserves = analysis_df[
        analysis_df["supplied_usd"] >= 10_000_000
    ].copy()

    most_utilized = (
        major_reserves
        .sort_values(
            "utilization",
            ascending=False
        )
        .head(10)
    )

    least_utilized = (
        major_reserves
        .sort_values(
            "utilization",
            ascending=True
        )
        .head(10)
    )

    return most_utilized, least_utilized


# ============================================================
# 5. PROTOCOL ECONOMICS ANALYSIS
# ============================================================

def protocol_economics_analysis(df):
    """
    Identify reserves that contribute most
    to estimated protocol interest.
    """

    economics_df = (
        df
        .dropna(
            subset=["estimated_protocol_interest"]
        )
        .sort_values(
            "estimated_protocol_interest",
            ascending=False
        )
        .head(10)
    )

    return economics_df


# ============================================================
# 6. PRINT BORROWING CONCENTRATION
# ============================================================

def print_concentration(concentration):

    print()
    print("==============================================")
    print("           BORROWING CONCENTRATION")
    print("==============================================")

    print(
        f"Top 1 reserve share: "
        f"{concentration['top1_share']:.2f}%"
    )

    print(
        f"Top 3 reserves share: "
        f"{concentration['top3_share']:.2f}%"
    )

    print(
        f"Top 5 reserves share: "
        f"{concentration['top5_share']:.2f}%"
    )

    print(
        f"Top 10 reserves share: "
        f"{concentration['top10_share']:.2f}%"
    )


# ============================================================
# 7. PRINT BORROWING COMPOSITION
# ============================================================

def print_borrow_composition(df):

    print()
    print("==============================================")
    print("             BORROW COMPOSITION")
    print("==============================================")

    top = (
        df
        .sort_values(
            "borrowed_usd",
            ascending=False
        )
        .head(10)
    )

    columns = [
        "symbol",
        "borrowed_usd",
        "borrow_share_pct",
    ]

    print(
        top[columns].to_string(
            index=False,
            formatters={
                "borrowed_usd":
                    lambda x: f"${x:,.0f}",

                "borrow_share_pct":
                    lambda x: f"{x:.2f}%",
            }
        )
    )


# ============================================================
# 8. PRINT MOST UTILIZED MARKETS
# ============================================================

def print_most_utilized(df):

    print()
    print("==============================================")
    print("          MOST UTILIZED MARKETS")
    print("      Supply >= $10M only")
    print("==============================================")

    columns = [
        "symbol",
        "supplied_usd",
        "borrowed_usd",
        "utilization",
        "borrow_apy",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={
                "supplied_usd":
                    lambda x: f"${x:,.0f}",

                "borrowed_usd":
                    lambda x: f"${x:,.0f}",

                "utilization":
                    lambda x: f"{x:.2f}%",

                "borrow_apy":
                    lambda x: (
                        f"{x:.2f}%"
                        if pd.notna(x)
                        else "N/A"
                    ),
            }
        )
    )


# ============================================================
# 9. PRINT LEAST UTILIZED MARKETS
# ============================================================

def print_least_utilized(df):

    print()
    print("==============================================")
    print("          LEAST UTILIZED MARKETS")
    print("      Supply >= $10M only")
    print("==============================================")

    columns = [
        "symbol",
        "supplied_usd",
        "borrowed_usd",
        "utilization",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={
                "supplied_usd":
                    lambda x: f"${x:,.0f}",

                "borrowed_usd":
                    lambda x: f"${x:,.0f}",

                "utilization":
                    lambda x: f"{x:.2f}%",
            }
        )
    )


# ============================================================
# 10. PRINT PROTOCOL ECONOMICS
# ============================================================

def print_protocol_economics(df):

    print()
    print("==============================================")
    print("      ESTIMATED PROTOCOL INTEREST")
    print("==============================================")

    columns = [
        "symbol",
        "borrowed_usd",
        "borrow_apy",
        "reserve_factor",
        "estimated_protocol_interest",
        "protocol_interest_share_pct",
    ]

    print(
        df[columns].to_string(
            index=False,
            formatters={
                "borrowed_usd":
                    lambda x: f"${x:,.0f}",

                "borrow_apy":
                    lambda x: (
                        f"{x:.2f}%"
                        if pd.notna(x)
                        else "N/A"
                    ),

                "reserve_factor":
                    lambda x: (
                        f"{x:.0f}%"
                        if pd.notna(x)
                        else "N/A"
                    ),

                "estimated_protocol_interest":
                    lambda x: f"${x:,.0f}",

                "protocol_interest_share_pct":
                    lambda x: f"{x:.2f}%",
            }
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading Aave dataset...")

    # 1. Load CSV
    df = load_data()

    print(
        f"Loaded {len(df)} reserves."
    )

    # 2. Calculate additional analytical metrics
    df = prepare_data(df)

    # 3. Borrow concentration
    concentration = concentration_analysis(df)

    # 4. Capital efficiency
    most_utilized, least_utilized = (
        capital_efficiency_analysis(df)
    )

    # 5. Protocol economics
    protocol_economics = (
        protocol_economics_analysis(df)
    )

    # 6. Print analysis
    print_concentration(
        concentration
    )

    print_borrow_composition(
        df
    )

    print_most_utilized(
        most_utilized
    )

    print_least_utilized(
        least_utilized
    )

    print_protocol_economics(
        protocol_economics
    )

    print()
    print("ANALYSIS FINISHED SUCCESSFULLY")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()