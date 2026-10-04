import json
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins"
)

TOKENS = {
    "AAVE": "aave",
    "MORPHO": "morpho",
    "EUL": "euler",
}

OUTPUT_PATH = Path(
    "data/raw/peer_token_data.json"
)


# ============================================================
# FETCH ONE TOKEN
# ============================================================

def fetch_token(
    symbol,
    coingecko_id,
):

    print()
    print(
        f"Fetching {symbol}..."
    )

    url = (
        f"{COINGECKO_URL}/{coingecko_id}"
    )

    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data


# ============================================================
# EXTRACT TOKEN DATA
# ============================================================

def extract_token_data(
    symbol,
    data,
):

    market = data[
        "market_data"
    ]

    price = market[
        "current_price"
    ].get("usd")

    market_cap = market[
        "market_cap"
    ].get("usd")

    fdv = market[
        "fully_diluted_valuation"
    ].get("usd")

    circulating_supply = market.get(
        "circulating_supply"
    )

    total_supply = market.get(
        "total_supply"
    )

    max_supply = market.get(
        "max_supply"
    )

    market_cap_rank = market.get(
        "market_cap_rank"
    )

    # --------------------------------------------------------
    # Circulating ratio
    # --------------------------------------------------------

    if (
        circulating_supply is not None
        and max_supply is not None
        and max_supply > 0
    ):

        circulating_ratio = (
            circulating_supply
            / max_supply
            * 100
        )

        remaining_supply = (
            max_supply
            - circulating_supply
        )

        remaining_supply_pct = (
            remaining_supply
            / max_supply
            * 100
        )

    else:

        circulating_ratio = None
        remaining_supply = None
        remaining_supply_pct = None

    # --------------------------------------------------------
    # FDV premium
    # --------------------------------------------------------

    if (
        market_cap is not None
        and fdv is not None
        and market_cap > 0
    ):

        fdv_premium = (
            fdv
            / market_cap
            - 1
        ) * 100

    else:

        fdv_premium = None

    # --------------------------------------------------------
    # Price performance
    # --------------------------------------------------------

    price_change_24h = market.get(
        "price_change_percentage_24h"
    )

    price_change_7d = market.get(
        "price_change_percentage_7d"
    )

    price_change_30d = market.get(
        "price_change_percentage_30d"
    )

    return {
        "symbol":
            symbol,

        "name":
            data.get("name"),

        "coingecko_id":
            data.get("id"),

        "price_usd":
            price,

        "market_cap_usd":
            market_cap,

        "fdv_usd":
            fdv,

        "market_cap_rank":
            market_cap_rank,

        "circulating_supply":
            circulating_supply,

        "total_supply":
            total_supply,

        "max_supply":
            max_supply,

        "circulating_ratio_pct":
            circulating_ratio,

        "remaining_supply":
            remaining_supply,

        "remaining_supply_pct":
            remaining_supply_pct,

        "fdv_premium_pct":
            fdv_premium,

        "price_change_24h_pct":
            price_change_24h,

        "price_change_7d_pct":
            price_change_7d,

        "price_change_30d_pct":
            price_change_30d,
    }


# ============================================================
# FETCH ALL TOKENS
# ============================================================

def fetch_all_tokens():

    results = {}

    for symbol, coingecko_id in TOKENS.items():

        try:

            raw_data = fetch_token(
                symbol,
                coingecko_id,
            )

            token_data = extract_token_data(
                symbol,
                raw_data,
            )

            results[symbol] = token_data

            print(
                f"{symbol} received successfully."
            )

        except Exception as error:

            print(
                f"ERROR fetching {symbol}: "
                f"{error}"
            )

            results[symbol] = {
                "symbol": symbol,
                "error": str(error),
            }

    return results


# ============================================================
# SAVE DATA
# ============================================================

def save_data(data):

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
            data,
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

    return f"${value:,.2f}"


def format_number(value):

    if value is None:
        return "N/A"

    return f"{value:,.0f}"


def format_pct(value):

    if value is None:
        return "N/A"

    return f"{value:.2f}%"


def format_signed_pct(value):

    if value is None:
        return "N/A"

    return f"{value:+.2f}%"


# ============================================================
# PRINT TOKEN
# ============================================================

def print_token(token):

    print()
    print(
        f"--- {token['symbol']} ---"
    )

    if "error" in token:

        print(
            f"ERROR: {token['error']}"
        )

        return

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
    print("Supply:")

    print(
        f"Circulating: "
        f"{format_number(token['circulating_supply'])}"
    )

    print(
        f"Total: "
        f"{format_number(token['total_supply'])}"
    )

    print(
        f"Max: "
        f"{format_number(token['max_supply'])}"
    )

    print(
        f"Circulating / Max: "
        f"{format_pct(token['circulating_ratio_pct'])}"
    )

    print(
        f"Remaining Supply: "
        f"{format_number(token['remaining_supply'])}"
    )

    print(
        f"Remaining Supply %: "
        f"{format_pct(token['remaining_supply_pct'])}"
    )

    print(
        f"FDV Premium: "
        f"{format_pct(token['fdv_premium_pct'])}"
    )

    print()
    print("Price Performance:")

    print(
        f"24h: "
        f"{format_signed_pct(token['price_change_24h_pct'])}"
    )

    print(
        f"7d: "
        f"{format_signed_pct(token['price_change_7d_pct'])}"
    )

    print(
        f"30d: "
        f"{format_signed_pct(token['price_change_30d_pct'])}"
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(data):

    print()
    print("==============================================")
    print("           LENDING PEER TOKENS")
    print("==============================================")

    for token in data.values():

        print_token(
            token
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Fetching lending peer token data..."
    )

    data = fetch_all_tokens()

    save_data(
        data
    )

    print_summary(
        data
    )

    print()
    print(
        "PEER TOKEN FETCH FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()