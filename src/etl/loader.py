"""Load and normalise Nifty 100 Excel source datasets."""

import logging
from pathlib import Path

import pandas as pd

from src.etl.normaliser import normalize_ticker, normalize_year

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
SUPPORTING_DIR = Path("data/supporting")


def find_file(directory: Path, name: str) -> Path:
    """Find a source file even when its downloaded name has a prefix."""

    matches = list(directory.glob(f"*{name}"))

    if not matches:
        raise FileNotFoundError(f"{name} not found in {directory}")

    return matches[0]


def load_excel(path: Path, header: int = 0) -> pd.DataFrame:
    """Load an Excel workbook into a DataFrame."""

    try:
        df = pd.read_excel(path, header=header)
        logger.info("Loaded %s: %d rows", path.name, len(df))
        return df
    except Exception as exc:
        logger.error("Failed to load %s: %s", path, exc)
        raise


def normalise_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise ticker and financial-year columns."""

    df = df.copy()

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)

    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    if "Year" in df.columns:
        df["Year"] = df["Year"].apply(normalize_year)

    return df


def load_raw_file(name: str) -> pd.DataFrame:
    """Load one core Excel source file."""

    path = find_file(RAW_DIR, name)

    # Core files contain a title row before their actual headers.
    df = load_excel(path, header=1)

    return normalise_dataframe(df)


def load_supporting_file(name: str) -> pd.DataFrame:
    """Load one supplementary Excel source file."""

    path = find_file(SUPPORTING_DIR, name)

    # Supporting files already begin with their real header row.
    df = load_excel(path, header=0)

    return normalise_dataframe(df)


def load_all_sources() -> dict[str, pd.DataFrame]:
    """Load all 12 project datasets."""

    datasets = {
        "companies": load_raw_file("companies.xlsx"),
        "profitandloss": load_raw_file("profitandloss.xlsx"),
        "balancesheet": load_raw_file("balancesheet.xlsx"),
        "cashflow": load_raw_file("cashflow.xlsx"),
        "analysis": load_raw_file("analysis.xlsx"),
        "documents": load_raw_file("documents.xlsx"),
        "prosandcons": load_raw_file("prosandcons.xlsx"),
        "sectors": load_supporting_file("sectors.xlsx"),
        "stock_prices": load_supporting_file("stock_prices.xlsx"),
        "market_cap": load_supporting_file("market_cap.xlsx"),
        "financial_ratios": load_supporting_file("financial_ratios.xlsx"),
        "peer_groups": load_supporting_file("peer_groups.xlsx"),
    }

    return datasets


def main() -> None:
    """Load all datasets and display their row counts."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    datasets = load_all_sources()

    for name, df in datasets.items():
        logger.info("%-20s %d rows", name, len(df))


if __name__ == "__main__":
    main()