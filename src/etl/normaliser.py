"""Normalise financial years and NSE ticker symbols."""

import re
from datetime import date, datetime

import pandas as pd


def normalize_year(value) -> str:
    """Convert source year values to YYYY-MM format."""

    if pd.isna(value):
        return "PARSE_ERROR"

    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.strftime("%Y-%m")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        year = int(value)
        if 1900 <= year <= 2100:
            return f"{year}-03"

    text = str(value).strip()

    # Already normalised: 2023-03
    if re.fullmatch(r"\d{4}-\d{2}", text):
        return text

    # Integer year stored as text: 2023
    if re.fullmatch(r"\d{4}", text):
        return f"{text}-03"

    # FY23 / FY24
    match = re.fullmatch(r"FY\s*(\d{2,4})", text, re.IGNORECASE)
    if match:
        year = int(match.group(1))
        if year < 100:
            year += 2000
        return f"{year}-03"

    cleaned = re.sub(r"\s+", "-", text)

    formats = (
        "%b-%y",       # Mar-23
        "%B-%Y",       # March-2023
        "%b-%Y",
        "%B-%y",
    )

    for fmt in formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.strftime("%Y-%m")
        except ValueError:
            continue

    return "PARSE_ERROR"


def normalize_ticker(value) -> str:
    """Strip whitespace and uppercase an NSE ticker."""

    if pd.isna(value):
        return "MISSING"

    ticker = str(value).strip().upper()

    if not ticker:
        return "MISSING"

    return ticker