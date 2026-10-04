import requests
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

URL = (
    "https://api.llama.fi/summary/fees/aave"
    "?dataType=dailyRevenue"
)

OUTPUT_PATH = Path(
    "data/raw/aave_revenue.csv"
)


# ============================================================
# FETCH DATA
# ============================================================

def fetch_aave_revenue():

    print("Fetching Aave revenue data...")

    response = requests.get(
        URL,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    print("Data received.")

    return data


# ============================================================
# EXTRACT DAILY REVENUE
# ============================================================

def extract_daily_revenue(data):

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

            "revenue_usd": float(value),
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
# PRINT API SUMMARY
# ============================================================

def print_api_summary(data):

    print()
    print("==============================================")
    print("          AAVE REVENUE — DEFILLAMA")
    print("==============================================")

    print(
        f"Protocol: {data.get('name')}"
    )

    print(
        f"24h revenue: "
        f"${data.get('total24h', 0):,.0f}"
    )

    print(
        f"7d revenue: "
        f"${data.get('total7d', 0):,.0f}"
    )

    print(
        f"30d revenue: "
        f"${data.get('total30d', 0):,.0f}"
    )

    print(
        f"1y revenue: "
        f"${data.get('total1y', 0):,.0f}"
    )

    print(
        f"All-time revenue: "
        f"${data.get('totalAllTime', 0):,.0f}"
    )


# ============================================================
# PRINT DATASET SUMMARY
# ============================================================

def print_dataset_summary(df):

    print()
    print("==============================================")
    print("          HISTORICAL REVENUE DATA")
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
                "revenue_usd":
                    lambda x: f"${x:,.0f}"
            }
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    data = fetch_aave_revenue()

    print_api_summary(data)

    df = extract_daily_revenue(data)

    save_data(df)

    print_dataset_summary(df)

    print()
    print(
        "SCRIPT FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()