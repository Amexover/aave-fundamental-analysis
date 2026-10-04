import os

import pandas as pd
import requests


URL = "https://api.llama.fi/protocol/aave-v3"
OUTPUT_PATH = "data/raw/aave_tvl.csv"


def fetch_aave_tvl():

    response = requests.get(
        URL,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(
        data["tvl"]
    )

    df["date"] = pd.to_datetime(
        df["date"],
        unit="s",
    )

    df = df.rename(
        columns={
            "totalLiquidityUSD": "tvl_usd"
        }
    )

    return df[
        [
            "date",
            "tvl_usd",
        ]
    ]


def save_tvl_data(df):

    os.makedirs(
        "data/raw",
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


def main():

    print(
        "Fetching Aave V3 TVL data..."
    )

    df = fetch_aave_tvl()

    save_tvl_data(df)

    print()
    print(
        df.tail()
    )

    print()
    print(
        f"Rows: {len(df)}"
    )

    print(
        f"From: {df['date'].min()}"
    )

    print(
        f"To: {df['date'].max()}"
    )

    print()
    print(
        f"CSV saved to: {OUTPUT_PATH}"
    )

    print()
    print(
        "TVL DATA FETCH FINISHED SUCCESSFULLY"
    )


if __name__ == "__main__":
    main()