from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap


# ============================================================
# CONFIG
# ============================================================

TVL_PATH = "data/raw/aave_tvl.csv"
FEES_PATH = "data/raw/aave_fees_revenue.csv"
REVENUE_PATH = "data/raw/aave_revenue.csv"
RESERVES_PATH = "data/raw/aave_ethereum_reserves.csv"

PEERS_PATH = "data/processed/lending_peer_analysis.csv"
PEER_VALUATION_PATH = "data/processed/lending_peer_valuation.csv"

TOKEN_PATH = "data/raw/aave_token_data.json"

CHARTS_DIR = Path("charts")

plt.rcParams.update({
    "font.family": "DejaVu Sans Mono", "font.size": 10,
    "axes.axisbelow": True, "axes.labelcolor": "#777974",
    "xtick.color": "#8b8d89", "ytick.color": "#8b8d89",
    "text.color": "#222321",
    "axes.prop_cycle": plt.cycler(color=["#4256ae", "#8bcf9c"]),
})


def style_chart(fig, ax, subtitle):
    """Apply the shared research chart layout."""
    title = ax.get_title().lower()
    ax.set_title("")
    fig.set_facecolor("#f3f2ee")
    fig.add_artist(Rectangle((0.015, 0.02), 0.97, 0.96,
        transform=fig.transFigure, facecolor="#fbfbf9",
        edgecolor="#d2d2ce", linewidth=0.8, zorder=-10))
    ax.set_facecolor("none")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, pad=6)
    if not ax.images:
        for line in ax.get_xgridlines() + ax.get_ygridlines():
            line.set_color("#e2e3df")
            line.set_alpha(1)
    fig.text(0.045, 0.94, title, fontsize=15, weight="bold", va="top")
    fig.text(0.045, 0.89, subtitle, fontsize=9, color="#8b8d89", va="top")
    fig.text(0.045, 0.035, "source: project data snapshot  |  see README for methodology",
             fontsize=7.5, color="#92948f", va="bottom")
    fig.subplots_adjust(left=0.14, right=0.93, top=0.80, bottom=0.19)


# ============================================================
# SETUP
# ============================================================

def setup():
    CHARTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# CHART 1 — TVL HISTORY
# ============================================================

def create_tvl_chart():

    df = pd.read_csv(
        TVL_PATH,
        parse_dates=["date"],
    )

    df = df.sort_values("date")

    df["tvl_b"] = (
        df["tvl_usd"]
        / 1_000_000_000
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.plot(
        df["date"],
        df["tvl_b"],
        linewidth=2,
    )

    ax.set_title(
        "Aave V3 TVL History",
        fontsize=16,
        pad=15,
    )

    ax.set_ylabel(
        "TVL ($B)"
    )

    ax.set_xlabel("")

    ax.grid(
        alpha=0.2
    )

    fig.tight_layout()

    style_chart(fig, ax, 'historical total value locked  |  usd billions')

    output = (
        CHARTS_DIR
        / "aave_tvl_history.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# CHART 2 — MONTHLY FEES & REVENUE
# ============================================================

def create_monthly_economics_chart():

    fees = pd.read_csv(
        FEES_PATH,
        parse_dates=["date"],
    )

    revenue = pd.read_csv(
        REVENUE_PATH,
        parse_dates=["date"],
    )

    fees["month"] = (
        fees["date"]
        .dt.to_period("M")
    )

    revenue["month"] = (
        revenue["date"]
        .dt.to_period("M")
    )

    monthly_fees = (
        fees
        .groupby("month")[
            "fees_usd"
        ]
        .sum()
    )

    monthly_revenue = (
        revenue
        .groupby("month")[
            "revenue_usd"
        ]
        .sum()
    )

    monthly = pd.concat(
        [
            monthly_fees,
            monthly_revenue,
        ],
        axis=1,
    ).dropna()

    latest_date = max(
        fees["date"].max(),
        revenue["date"].max(),
    )

    current_month = (
        latest_date.to_period("M")
    )

    # Remove incomplete current month
    monthly = monthly[
        monthly.index
        < current_month
    ]

    # Recent 18 complete months
    monthly = (
        monthly
        .tail(18)
        .copy()
    )

    monthly["fees_m"] = (
        monthly["fees_usd"]
        / 1_000_000
    )

    monthly["revenue_m"] = (
        monthly["revenue_usd"]
        / 1_000_000
    )

    labels = [
        str(month)
        for month in monthly.index
    ]

    x = list(
        range(len(monthly))
    )

    fig, ax = plt.subplots(
        figsize=(13, 6)
    )

    width = 0.38

    ax.bar(
        [
            i - width / 2
            for i in x
        ],
        monthly["fees_m"],
        width=width,
        label="Fees",
    )

    ax.bar(
        [
            i + width / 2
            for i in x
        ],
        monthly["revenue_m"],
        width=width,
        label="Protocol Revenue",
    )

    ax.set_title(
        "Aave Monthly Fees & Protocol Revenue",
        fontsize=16,
        pad=15,
    )

    ax.set_ylabel(
        "$M"
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        labels,
        rotation=45,
        ha="right",
    )

    ax.legend(frameon=False, loc="upper left", ncol=2)

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    fig.tight_layout()

    style_chart(fig, ax, 'fees and protocol revenue  |  complete months  |  usd millions')

    output = (
        CHARTS_DIR
        / "aave_monthly_fees_revenue.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# CHART 3 — BORROW COMPOSITION
# ============================================================

def create_borrow_composition_chart():

    df = pd.read_csv(
        RESERVES_PATH
    )

    df = (
        df
        .sort_values(
            "borrowed_usd",
            ascending=False,
        )
        .copy()
    )

    total_borrowed = (
        df["borrowed_usd"]
        .sum()
    )

    top = (
        df
        .head(7)
        .copy()
    )

    top["borrow_share_pct"] = (
        top["borrowed_usd"]
        / total_borrowed
        * 100
    )

    other_share = (
        100
        - top[
            "borrow_share_pct"
        ].sum()
    )

    chart_df = pd.DataFrame({
        "asset":
            list(
                top["symbol"]
            )
            + ["Other"],

        "share":
            list(
                top[
                    "borrow_share_pct"
                ]
            )
            + [other_share],
    })

    chart_df = (
        chart_df
        .sort_values(
            "share",
            ascending=True,
        )
    )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    bars = ax.barh(
        chart_df["asset"],
        chart_df["share"],
    )

    ax.set_title(
        "Aave Ethereum Borrow Composition",
        fontsize=16,
        pad=15,
    )

    ax.set_xlabel(
        "Share of Total Borrowing (%)"
    )

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    for bar in bars:

        width = (
            bar.get_width()
        )

        ax.text(
            width + 0.5,
            bar.get_y()
            + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center",
        )

    fig.tight_layout()

    style_chart(fig, ax, 'ethereum v3 reserves  |  share of borrowed assets')

    output = (
        CHARTS_DIR
        / "aave_borrow_composition.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# CHART 4 — PEER FEE PRODUCTIVITY
# ============================================================

def create_peer_productivity_chart():

    df = pd.read_csv(
        PEERS_PATH
    )

    df = (
        df
        .sort_values(
            "annualized_fee_tvl_pct",
            ascending=False,
        )
        .copy()
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    bars = ax.bar(
        df["protocol"],
        df[
            "annualized_fee_tvl_pct"
        ],
    )

    ax.set_title(
        "DeFi Lending Fee Productivity",
        fontsize=16,
        pad=15,
    )

    ax.set_ylabel(
        "Annualized 30d Fees / Current TVL (%)"
    )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    for bar in bars:

        height = (
            bar.get_height()
        )

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            height + 0.1,
            f"{height:.2f}%",
            ha="center",
        )

    fig.tight_layout()

    style_chart(fig, ax, 'annualized 30-day fees / current tvl  |  percent')

    output = (
        CHARTS_DIR
        / "lending_fee_productivity.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# CHART 5 — PEER VALUATION
# ============================================================

def create_peer_valuation_chart():

    df = pd.read_csv(
        PEER_VALUATION_PATH
    )

    df = (
        df
        .dropna(
            subset=[
                "fdv_to_annualized_fees"
            ]
        )
        .sort_values(
            "fdv_to_annualized_fees",
            ascending=True,
        )
        .copy()
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    bars = ax.barh(
        df["protocol"],
        df[
            "fdv_to_annualized_fees"
        ],
    )

    ax.set_title(
        "DeFi Lending Peer Valuation",
        fontsize=16,
        pad=15,
    )

    ax.set_xlabel(
        "FDV / Annualized 30d Fees"
    )

    ax.grid(
        axis="x",
        alpha=0.2,
    )

    for bar in bars:

        width = (
            bar.get_width()
        )

        ax.text(
            width + 0.15,
            bar.get_y()
            + bar.get_height() / 2,
            f"{width:.2f}x",
            va="center",
        )

    fig.tight_layout()

    style_chart(fig, ax, 'fully diluted valuation / annualized 30-day fees')

    output = (
        CHARTS_DIR
        / "lending_peer_valuation.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# CHART 6 — AAVE VALUATION SENSITIVITY
# ============================================================

def create_valuation_sensitivity_chart():

    with open(
        TOKEN_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        token = json.load(file)

    circulating_supply = (
        token["circulating_supply"]
    )

    current_price = (
        token["price_usd"]
    )

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

    sensitivity = []

    for revenue in revenue_levels:

        row = []

        for multiple in multiples:

            implied_market_cap = (
                revenue
                * multiple
            )

            implied_price = (
                implied_market_cap
                / circulating_supply
            )

            row.append(
                implied_price
            )

        sensitivity.append(
            row
        )

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )

    image = ax.imshow(
        sensitivity,
        aspect="auto",
        cmap=LinearSegmentedColormap.from_list("research", ["#e4eee8", "#8bcf9c", "#4256ae"]),
    )

    ax.set_title(
        "AAVE Implied Price Sensitivity",
        fontsize=16,
        pad=15,
    )

    ax.set_xlabel(
        "Revenue Multiple"
    )

    ax.set_ylabel(
        "Normalized Annual Protocol Revenue"
    )

    ax.set_xticks(
        range(len(multiples))
    )

    ax.set_xticklabels(
        [
            f"{multiple}x"
            for multiple in multiples
        ]
    )

    ax.set_yticks(
        range(
            len(revenue_levels)
        )
    )

    ax.set_yticklabels(
        [
            f"${revenue / 1_000_000:.0f}M"
            for revenue
            in revenue_levels
        ]
    )

    # --------------------------------------------------------
    # Cell labels
    # --------------------------------------------------------

    for i in range(
        len(revenue_levels)
    ):

        for j in range(
            len(multiples)
        ):

            price = (
                sensitivity[i][j]
            )

            ax.text(
                j,
                i,
                f"${price:.0f}",
                ha="center",
                va="center",
                fontsize=9,
                color="white" if price > max(map(max, sensitivity)) * 0.62 else "#202622",
            )

    # --------------------------------------------------------
    # Color scale
    # --------------------------------------------------------

    colorbar = fig.colorbar(
        image,
        ax=ax,
    )

    colorbar.set_label(
        "Implied AAVE Price ($)"
    )

    # --------------------------------------------------------
    # Current price note
    # --------------------------------------------------------

    fig.text(
        0.5,
        0.075,
        (
            f"Snapshot AAVE price: "
            f"${current_price:.2f}"
        ),
        ha="center",
        fontsize=10,
    )

    fig.tight_layout(
        rect=[
            0,
            0.04,
            1,
            1,
        ]
    )

    style_chart(fig, ax, 'scenario model  |  annual revenue and revenue multiple')

    output = (
        CHARTS_DIR
        / "aave_valuation_sensitivity.png"
    )

    fig.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Created: {output}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "Creating final research charts..."
    )

    print()

    setup()

    create_tvl_chart()

    create_monthly_economics_chart()

    create_borrow_composition_chart()

    create_peer_productivity_chart()

    create_peer_valuation_chart()

    create_valuation_sensitivity_chart()

    print()

    print(
        "ALL 6 CHARTS CREATED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
