import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


FETCH_SCRIPTS = [
    "src/fetch_defillama.py",
    "src/fetch_aave.py",
    "src/fetch_defillama_fees.py",
    "src/fetch_defillama_revenue.py",
    "src/fetch_token_data.py",
    "src/fetch_competitors.py",
    "src/fetch_peer_tokens.py",
]


ANALYSIS_SCRIPTS = [
    "src/analyze_aave.py",
    "src/analyze_fees.py",
    "src/analyze_protocol_economics.py",
    "src/analyze_competitors.py",
    "src/analyze_valuation.py",
    "src/peer_valuation.py",
    "src/analyze_dao_financials.py",
    "src/scenario_valuation.py",
]


CHART_SCRIPTS = [
    "src/create_charts.py",
]


def run_script(script_path):

    full_path = PROJECT_ROOT / script_path

    print()
    print("=" * 60)
    print(f"RUNNING: {script_path}")
    print("=" * 60)
    print()

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        print()
        print("=" * 60)
        print(f"FAILED: {script_path}")
        print("=" * 60)

        sys.exit(result.returncode)

    print()
    print(f"COMPLETED: {script_path}")


def run_stage(stage_name, scripts):

    print()
    print()
    print("#" * 60)
    print(f"# {stage_name}")
    print("#" * 60)

    for script in scripts:
        run_script(script)


def main():

    print()
    print("=" * 60)
    print("AAVE FUNDAMENTAL ANALYSIS PIPELINE")
    print("=" * 60)

    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")

    run_stage(
        "STAGE 1 — FETCHING DATA",
        FETCH_SCRIPTS,
    )

    run_stage(
        "STAGE 2 — FUNDAMENTAL ANALYSIS",
        ANALYSIS_SCRIPTS,
    )

    run_stage(
        "STAGE 3 — GENERATING CHARTS",
        CHART_SCRIPTS,
    )

    print()
    print("=" * 60)
    print("PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 60)

    print()
    print("Outputs:")
    print("  Raw data:       data/raw/")
    print("  Processed data: data/processed/")
    print("  Charts:         charts/")
    print()


if __name__ == "__main__":
    main()