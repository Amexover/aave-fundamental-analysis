import os

import pandas as pd
import requests


URL = "https://api.v3.aave.com/graphql"
OUTPUT_PATH = "data/raw/aave_ethereum_reserves.csv"


QUERY = """
query EthereumMarket {
  market(
    request: {
      address: "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
      chainId: 1
    }
  ) {
    name
    totalMarketSize
    totalAvailableLiquidity

    reserves {
      underlyingToken {
        symbol
        name
      }

      supplyInfo {
        total {
          value
        }

        apy {
          value
        }
      }

      borrowInfo {
        total {
          amount {
            value
          }
          usd
        }

        availableLiquidity {
          amount {
            value
          }
          usd
        }

        apy {
          value
        }

        utilizationRate {
          value
        }

        reserveFactor {
          value
        }
      }
    }
  }
}
"""


def fetch_aave_ethereum():

    response = requests.post(
        URL,
        json={"query": QUERY},
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise RuntimeError(
            result["errors"]
        )

    return result["data"]["market"]


def reserves_to_dataframe(market):

    rows = []

    for reserve in market["reserves"]:

        token = reserve["underlyingToken"]
        supply = reserve["supplyInfo"]
        borrow = reserve["borrowInfo"]

        row = {
            "symbol":
                token["symbol"],

            "name":
                token["name"],

            "supplied_tokens":
                float(
                    supply["total"]["value"]
                ),

            "supply_apy":
                float(
                    supply["apy"]["value"]
                ) * 100,
        }

        if borrow is not None:

            borrowed_tokens = float(
                borrow["total"]["amount"]["value"]
            )

            borrowed_usd = float(
                borrow["total"]["usd"]
            )

            available_liquidity_usd = float(
                borrow[
                    "availableLiquidity"
                ]["usd"]
            )

            supplied_usd = (
                borrowed_usd
                + available_liquidity_usd
            )

            borrow_apy = float(
                borrow["apy"]["value"]
            ) * 100

            utilization = float(
                borrow[
                    "utilizationRate"
                ]["value"]
            ) * 100

            reserve_factor = float(
                borrow[
                    "reserveFactor"
                ]["value"]
            ) * 100

            row.update({
                "supplied_usd":
                    supplied_usd,

                "borrowed_tokens":
                    borrowed_tokens,

                "borrowed_usd":
                    borrowed_usd,

                "available_liquidity_usd":
                    available_liquidity_usd,

                "borrow_apy":
                    borrow_apy,

                "utilization":
                    utilization,

                "reserve_factor":
                    reserve_factor,
            })

        else:

            row.update({
                "supplied_usd":
                    None,

                "borrowed_tokens":
                    0.0,

                "borrowed_usd":
                    0.0,

                "available_liquidity_usd":
                    None,

                "borrow_apy":
                    None,

                "utilization":
                    0.0,

                "reserve_factor":
                    None,
            })

        rows.append(row)

    return pd.DataFrame(rows)


def calculate_reserve_metrics(df):

    df = df.copy()

    df[
        "estimated_annual_borrow_interest"
    ] = (
        df["borrowed_usd"]
        * df["borrow_apy"]
        / 100
    )

    df[
        "estimated_protocol_interest"
    ] = (
        df[
            "estimated_annual_borrow_interest"
        ]
        * df["reserve_factor"]
        / 100
    )

    return df


def calculate_market_metrics(df):

    lending_df = (
        df
        .dropna(
            subset=["supplied_usd"]
        )
        .copy()
    )

    total_supplied = (
        lending_df["supplied_usd"].sum()
    )

    total_borrowed = (
        lending_df["borrowed_usd"].sum()
    )

    total_available_liquidity = (
        lending_df[
            "available_liquidity_usd"
        ].sum()
    )

    if total_supplied > 0:

        aggregate_utilization = (
            total_borrowed
            / total_supplied
            * 100
        )

    else:

        aggregate_utilization = 0.0

    estimated_borrow_interest = (
        lending_df[
            "estimated_annual_borrow_interest"
        ].sum()
    )

    estimated_protocol_interest = (
        lending_df[
            "estimated_protocol_interest"
        ].sum()
    )

    top3_borrowed = (
        lending_df
        .nlargest(
            3,
            "borrowed_usd",
        )["borrowed_usd"]
        .sum()
    )

    if total_borrowed > 0:

        top3_borrow_share = (
            top3_borrowed
            / total_borrowed
            * 100
        )

    else:

        top3_borrow_share = 0.0

    return {
        "total_supplied":
            total_supplied,

        "total_borrowed":
            total_borrowed,

        "total_available_liquidity":
            total_available_liquidity,

        "aggregate_utilization":
            aggregate_utilization,

        "estimated_borrow_interest":
            estimated_borrow_interest,

        "estimated_protocol_interest":
            estimated_protocol_interest,

        "top3_borrow_share":
            top3_borrow_share,
    }


def save_dataframe(df):

    os.makedirs(
        os.path.dirname(
            OUTPUT_PATH
        ),
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


def print_results(
    market,
    df,
    metrics,
):

    market_size = float(
        market["totalMarketSize"]
    )

    api_available_liquidity = float(
        market["totalAvailableLiquidity"]
    )

    print()
    print(
        "=============================================="
    )
    print(
        "              AAVE V3 ETHEREUM"
    )
    print(
        "=============================================="
    )

    print(
        f"Market size (Aave API): "
        f"${market_size:,.0f}"
    )

    print(
        f"Available liquidity (Aave API): "
        f"${api_available_liquidity:,.0f}"
    )

    print(
        f"Number of reserves: {len(df)}"
    )

    print()
    print(
        "=== LENDING ECONOMICS ==="
    )

    print(
        f"Calculated supplied capital: "
        f"${metrics['total_supplied']:,.0f}"
    )

    print(
        f"Total borrowed: "
        f"${metrics['total_borrowed']:,.0f}"
    )

    print(
        f"Calculated available liquidity: "
        f"${metrics['total_available_liquidity']:,.0f}"
    )

    print(
        f"Aggregate utilization: "
        f"{metrics['aggregate_utilization']:.2f}%"
    )

    print(
        f"Estimated annual borrower interest: "
        f"${metrics['estimated_borrow_interest']:,.0f}"
    )

    print(
        f"Estimated annual protocol interest: "
        f"${metrics['estimated_protocol_interest']:,.0f}"
    )

    print(
        f"Top 3 assets share of total borrowing: "
        f"{metrics['top3_borrow_share']:.2f}%"
    )

    print()
    print(
        "=== TOP 10 RESERVES BY BORROWED USD ==="
    )

    top10 = (
        df
        .sort_values(
            "borrowed_usd",
            ascending=False,
        )
        .head(10)
        .copy()
    )

    columns = [
        "symbol",
        "supplied_usd",
        "borrowed_usd",
        "utilization",
        "supply_apy",
        "borrow_apy",
        "reserve_factor",
        "estimated_protocol_interest",
    ]

    formatters = {

        "supplied_usd":
            lambda x:
                f"${x:,.0f}"
                if pd.notna(x)
                else "N/A",

        "borrowed_usd":
            lambda x:
                f"${x:,.0f}",

        "utilization":
            lambda x:
                f"{x:.1f}%",

        "supply_apy":
            lambda x:
                f"{x:.2f}%",

        "borrow_apy":
            lambda x:
                f"{x:.2f}%"
                if pd.notna(x)
                else "N/A",

        "reserve_factor":
            lambda x:
                f"{x:.0f}%"
                if pd.notna(x)
                else "N/A",

        "estimated_protocol_interest":
            lambda x:
                f"${x:,.0f}"
                if pd.notna(x)
                else "N/A",
    }

    print(
        top10[
            columns
        ].to_string(
            index=False,
            formatters=formatters,
        )
    )

    print()

    print(
        "NOTE: Estimated protocol interest is a "
        "snapshot-based annualized estimate, not "
        "actual realized Aave revenue."
    )

    print()

    print(
        f"CSV saved to: {OUTPUT_PATH}"
    )

    print()

    print(
        "SCRIPT FINISHED SUCCESSFULLY"
    )


def main():

    print(
        "Fetching Aave V3 Ethereum data..."
    )

    market = fetch_aave_ethereum()

    print(
        "Data received."
    )

    df = reserves_to_dataframe(
        market
    )

    df = calculate_reserve_metrics(
        df
    )

    df = (
        df
        .sort_values(
            "borrowed_usd",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    metrics = calculate_market_metrics(
        df
    )

    save_dataframe(
        df
    )

    print_results(
        market,
        df,
        metrics,
    )


if __name__ == "__main__":
    main()