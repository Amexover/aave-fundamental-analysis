import json
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/aave"
)

OUTPUT_PATH = Path(
    "data/raw/aave_token_data.json"
)


# ============================================================
# FETCH TOKEN DATA
# ============================================================

def fetch_token_data():

    print("Fetching AAVE token data from CoinGecko...")

    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }

    response = requests.get(
        COINGECKO_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    print("Data received.")

    return data


# ============================================================
# EXTRACT MARKET DATA
# ============================================================

def extract_market_data(data):

    market = data["market_data"]

    token_data = {
        "id": data["id"],
        "symbol": data["symbol"].upper(),
        "name": data["name"],

        "price_usd":
            market["current_price"]["usd"],

        "market_cap_usd":
            market["market_cap"]["usd"],

        "fdv_usd":
            market["fully_diluted_valuation"]["usd"],

        "circulating_supply":
            market["circulating_supply"],

        "total_supply":
            market["total_supply"],

        "max_supply":
            market["max_supply"],

        "market_cap_rank":
            market["market_cap_rank"],

        "price_change_24h_pct":
            market[
                "price_change_percentage_24h"
            ],

        "price_change_7d_pct":
            market[
                "price_change_percentage_7d"
            ],

        "price_change_30d_pct":
            market[
                "price_change_percentage_30d"
            ],

        "ath_usd":
            market["ath"]["usd"],

        "ath_change_pct":
            market["ath_change_percentage"]["usd"],

        "ath_date":
            market["ath_date"]["usd"],
    }

    return token_data


# ============================================================
# SAVE DATA
# ============================================================

def save_data(token_data):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            token_data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print()
    print(
        f"JSON saved to: {OUTPUT_PATH}"
    )


# ============================================================
# FORMAT HELPERS
# ============================================================

def format_usd(value):

    if value is None:
        return "N/A"

    return f"${value:,.0f}"


def format_number(value):

    if value is None:
        return "N/A"

    return f"{value:,.0f}"


def format_percentage(value):

    if value is None:
        return "N/A"

    return f"{value:+.2f}%"


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(token):

    print()
    print("==============================================")
    print("              AAVE TOKEN DATA")
    print("==============================================")

    print(
        f"Token: "
        f"{token['name']} ({token['symbol']})"
    )

    print(
        f"Price: "
        f"{format_usd(token['price_usd'])}"
    )

    print(
        f"Market Cap: "
        f"{format_usd(token['market_cap_usd'])}"
    )

    print(
        f"FDV: "
        f"{format_usd(token['fdv_usd'])}"
    )

    print(
        f"Market Cap Rank: "
        f"{token['market_cap_rank']}"
    )

    print()
    print("=== SUPPLY ===")

    print(
        f"Circulating Supply: "
        f"{format_number(token['circulating_supply'])} AAVE"
    )

    print(
        f"Total Supply: "
        f"{format_number(token['total_supply'])} AAVE"
    )

    print(
        f"Max Supply: "
        f"{format_number(token['max_supply'])} AAVE"
    )

    print()
    print("=== PRICE PERFORMANCE ===")

    print(
        f"24h: "
        f"{format_percentage(token['price_change_24h_pct'])}"
    )

    print(
        f"7d: "
        f"{format_percentage(token['price_change_7d_pct'])}"
    )

    print(
        f"30d: "
        f"{format_percentage(token['price_change_30d_pct'])}"
    )

    print()
    print("=== ALL-TIME HIGH ===")

    print(
        f"ATH: "
        f"{format_usd(token['ath_usd'])}"
    )

    print(
        f"From ATH: "
        f"{format_percentage(token['ath_change_pct'])}"
    )

    print(
        f"ATH Date: "
        f"{token['ath_date']}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    data = fetch_token_data()

    token_data = extract_market_data(
        data
    )

    save_data(
        token_data
    )

    print_results(
        token_data
    )

    print()
    print(
        "SCRIPT FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()