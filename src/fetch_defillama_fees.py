import requests
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

URL = "https://api.llama.fi/summary/fees/aave"

OUTPUT_PATH = Path(
    "data/raw/aave_fees_revenue.csv"
)


# ============================================================
# FETCH DATA
# ============================================================

def fetch_aave_fees():
    """
    Fetch Aave historical fees and revenue
    from DefiLlama.
    """

    print("Fetching Aave fees data...")

    response = requests.get(
        URL,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    print("Data received.")

    return data


# ============================================================
# INSPECT API RESPONSE
# ============================================================

def inspect_response(data):
    """
    Print important fields returned by
    the DefiLlama API.
    """

    print()
    print("==============================================")
    print("          DEFILLAMA FEES RESPONSE")
    print("==============================================")

    print("Protocol:", data.get("name"))

    print(
        "Total 24h:",
        data.get("total24h")
    )

    print(
        "Total 7d:",
        data.get("total7d")
    )

    print(
        "Total 30d:",
        data.get("total30d")
    )

    print(
        "Total 1y:",
        data.get("total1y")
    )

    print()
    print("Available keys:")

    for key in data.keys():
        print("-", key)


# ============================================================
# EXTRACT DAILY FEES
# ============================================================

def extract_daily_fees(data):
    """
    Convert DefiLlama daily chart data
    into a pandas DataFrame.
    """

    chart = data.get(
        "totalDataChart",
        []
    )

    rows = []

    for item in chart:

        timestamp = item[0]
        value = item[1]

        rows.append({
            "date": pd.to_datetime(
                timestamp,
                unit="s"
            ),

            "fees_usd": float(value),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = (
            df
            .sort_values("date")
            .reset_index(drop=True)
        )

    return df


# ============================================================
# SAVE DATA
# ============================================================

def save_data(df):
    """
    Save historical fee data to CSV.
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print(
        f"CSV saved to: {OUTPUT_PATH}"
    )


# ============================================================
# PRINT DATASET SUMMARY
# ============================================================

def print_summary(df):

    print()
    print("==============================================")
    print("            HISTORICAL FEES DATA")
    print("==============================================")

    print(
        f"Rows: {len(df)}"
    )

    if df.empty:
        print("Dataset is empty.")
        return

    print(
        f"From: {df['date'].min()}"
    )

    print(
        f"To:   {df['date'].max()}"
    )

    print()
    print("Last 10 observations:")

    print(
        df.tail(10).to_string(
            index=False,
            formatters={
                "fees_usd":
                    lambda x: f"${x:,.0f}"
            }
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # 1. Fetch API response
    data = fetch_aave_fees()

    # 2. Inspect what DefiLlama returned
    inspect_response(data)

    # 3. Extract historical fees
    df = extract_daily_fees(data)

    # 4. Save raw dataset
    save_data(df)

    # 5. Print summary
    print_summary(df)

    print()
    print(
        "SCRIPT FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()