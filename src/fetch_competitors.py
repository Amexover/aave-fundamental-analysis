import json
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

PROTOCOLS = {
    "aave": {
        "tvl_slug": "aave-v3",
        "fees_slug": "aave",
    },

    "morpho": {
        "tvl_slug": "morpho",
        "fees_slug": "morpho",
    },

    "euler": {
        "tvl_slug": "euler",
        "fees_slug": "euler",
    },
}


OUTPUT_PATH = Path(
    "data/raw/competitor_protocol_data.json"
)


# ============================================================
# FETCH TVL DATA
# ============================================================

def fetch_tvl_data(slug):

    url = (
        f"https://api.llama.fi/protocol/{slug}"
    )

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# FETCH FEES / REVENUE
# ============================================================

def fetch_economics_data(
    slug,
    data_type=None,
):

    url = (
        f"https://api.llama.fi/summary/fees/{slug}"
    )

    params = {}

    if data_type is not None:
        params["dataType"] = data_type

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# EXTRACT CURRENT TVL
# ============================================================

def extract_current_tvl(data):

    tvl_history = data.get(
        "tvl",
        []
    )

    if not tvl_history:
        return None

    latest = tvl_history[-1]

    return float(
        latest["totalLiquidityUSD"]
    )


# ============================================================
# EXTRACT ECONOMICS
# ============================================================

def extract_economics(data):

    return {
        "24h": data.get(
            "total24h"
        ),

        "7d": data.get(
            "total7d"
        ),

        "30d": data.get(
            "total30d"
        ),

        "1y": data.get(
            "total1y"
        ),

        "all_time": data.get(
            "totalAllTime"
        ),
    }


# ============================================================
# FETCH ONE PROTOCOL
# ============================================================

def fetch_protocol(
    name,
    config,
):

    print()
    print(
        f"Fetching {name.upper()}..."
    )

    # --------------------------------------------------------
    # TVL
    # --------------------------------------------------------

    tvl_data = fetch_tvl_data(
        config["tvl_slug"]
    )

    current_tvl = extract_current_tvl(
        tvl_data
    )

    print(
        f"TVL received: "
        f"${current_tvl:,.0f}"
        if current_tvl is not None
        else "TVL unavailable"
    )

    # --------------------------------------------------------
    # FEES
    # --------------------------------------------------------

    fees_data = fetch_economics_data(
        config["fees_slug"]
    )

    fees = extract_economics(
        fees_data
    )

    print(
        f"30d fees: "
        f"${fees['30d']:,.0f}"
        if fees["30d"] is not None
        else "30d fees unavailable"
    )

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    revenue_data = fetch_economics_data(
        config["fees_slug"],
        data_type="dailyRevenue",
    )

    revenue = extract_economics(
        revenue_data
    )

    print(
        f"30d revenue: "
        f"${revenue['30d']:,.0f}"
        if revenue["30d"] is not None
        else "30d revenue unavailable"
    )

    return {
        "name": name,
        "tvl_usd": current_tvl,
        "fees": fees,
        "revenue": revenue,
    }


# ============================================================
# FETCH ALL PROTOCOLS
# ============================================================

def fetch_all_protocols():

    results = {}

    for name, config in PROTOCOLS.items():

        try:

            results[name] = fetch_protocol(
                name,
                config,
            )

        except Exception as error:

            print()
            print(
                f"ERROR fetching {name}: "
                f"{error}"
            )

            results[name] = {
                "name": name,
                "error": str(error),
            }

    return results


# ============================================================
# SAVE RAW DATA
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
# PRINT SUMMARY
# ============================================================

def print_summary(data):

    print()
    print("==============================================")
    print("             DEFI LENDING PEERS")
    print("==============================================")

    for name, protocol in data.items():

        print()
        print(
            f"--- {name.upper()} ---"
        )

        if "error" in protocol:

            print(
                f"ERROR: "
                f"{protocol['error']}"
            )

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

        print(
            f"TVL: "
            f"${tvl:,.0f}"
            if tvl is not None
            else "TVL: N/A"
        )

        print(
            f"30d Fees: "
            f"${fees_30d:,.0f}"
            if fees_30d is not None
            else "30d Fees: N/A"
        )

        print(
            f"1y Fees: "
            f"${fees_1y:,.0f}"
            if fees_1y is not None
            else "1y Fees: N/A"
        )

        print(
            f"30d Revenue: "
            f"${revenue_30d:,.0f}"
            if revenue_30d is not None
            else "30d Revenue: N/A"
        )

        print(
            f"1y Revenue: "
            f"${revenue_1y:,.0f}"
            if revenue_1y is not None
            else "1y Revenue: N/A"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Fetching DeFi lending competitors..."
    )

    data = fetch_all_protocols()

    save_data(
        data
    )

    print_summary(
        data
    )

    print()
    print(
        "COMPETITOR DATA FETCH FINISHED SUCCESSFULLY"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()