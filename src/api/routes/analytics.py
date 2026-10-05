"""Sprint 6 - Day 40: Portfolio analytics API endpoints."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "nifty100.db"

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


def get_connection() -> sqlite3.Connection:
    """Create SQLite connection with dictionary-style rows."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def rows_to_dicts(rows):
    """Convert SQLite rows to JSON-serializable dictionaries."""

    return [dict(row) for row in rows]


# ============================================================
# 1. SECTOR SUMMARY
# ============================================================

@router.get("/sectors")
def sector_summary():
    """Return company count and index weight by broad sector."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                broad_sector,
                COUNT(DISTINCT company_id) AS company_count,
                ROUND(SUM(index_weight_pct), 4) AS total_index_weight_pct
            FROM sectors
            GROUP BY broad_sector
            ORDER BY company_count DESC, broad_sector
            """
        ).fetchall()

    return {
        "count": len(rows),
        "sectors": rows_to_dicts(rows),
    }


# ============================================================
# 2. SECTOR COMPANIES
# ============================================================

@router.get("/sectors/{sector_name}")
def sector_companies(sector_name: str):
    """Return companies belonging to a broad sector."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                c.id AS company_id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                s.index_weight_pct,
                s.market_cap_category
            FROM companies c
            JOIN sectors s
                ON c.id = s.company_id
            WHERE LOWER(s.broad_sector) = LOWER(?)
            ORDER BY s.index_weight_pct DESC, c.company_name
            """,
            (sector_name,),
        ).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Sector not found",
        )

    return {
        "sector": sector_name,
        "count": len(rows),
        "companies": rows_to_dicts(rows),
    }


# ============================================================
# 3. LATEST FINANCIAL RATIOS
# ============================================================

@router.get("/latest-ratios")
def latest_ratios():
    """Return latest meaningful annual ratio row per company."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT fr.*
            FROM financial_ratios fr
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM financial_ratios
                WHERE year <= '2024-03'
                GROUP BY company_id
            ) latest
                ON fr.company_id = latest.company_id
               AND fr.year = latest.latest_year
            ORDER BY fr.company_id
            """
        ).fetchall()

    return {
        "count": len(rows),
        "ratios": rows_to_dicts(rows),
    }


# ============================================================
# 4. VALUATION SUMMARY
# ============================================================

@router.get("/valuation")
def valuation_summary():
    """Return latest available valuation data per company."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT mc.*
            FROM market_cap mc
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM market_cap
                GROUP BY company_id
            ) latest
                ON mc.company_id = latest.company_id
               AND mc.year = latest.latest_year
            ORDER BY mc.company_id
            """
        ).fetchall()

    return {
        "count": len(rows),
        "valuation": rows_to_dicts(rows),
    }


# ============================================================
# 5. PRO / CON SIGNAL SUMMARY
# ============================================================

@router.get("/signals")
def signal_summary():
    """Return generated pro/con signal counts by company."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                company_id,
                SUM(
                    CASE
                        WHEN UPPER(signal_type) = 'PRO'
                        THEN 1
                        ELSE 0
                    END
                ) AS pro_count,
                SUM(
                    CASE
                        WHEN UPPER(signal_type) = 'CON'
                        THEN 1
                        ELSE 0
                    END
                ) AS con_count,
                COUNT(*) AS total_signals
            FROM generated_pros_cons
            GROUP BY company_id
            ORDER BY company_id
            """
        ).fetchall()

    return {
        "count": len(rows),
        "signals": rows_to_dicts(rows),
    }




# ============================================================
# 6. CLUSTER ANALYTICS
# ============================================================

@router.get("/clusters")
def cluster_analytics():
    """Return Day 36-37 company cluster labels and cluster profiles."""

    import csv

    output_dir = PROJECT_ROOT / "output"
    labels_path = output_dir / "cluster_labels.csv"
    profiles_path = output_dir / "cluster_profiles.csv"

    if not labels_path.exists() or not profiles_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Cluster analytics outputs are unavailable",
        )

    with labels_path.open("r", encoding="utf-8-sig", newline="") as file:
        labels = list(csv.DictReader(file))

    with profiles_path.open("r", encoding="utf-8-sig", newline="") as file:
        profiles = list(csv.DictReader(file))

    return {
        "company_count": len(labels),
        "cluster_count": len(profiles),
        "profiles": profiles,
        "companies": labels,
    }


# ============================================================
# 7. OUTLIER ANALYTICS
# ============================================================

@router.get("/outliers")
def outlier_analytics():
    """Return Day 37 statistical outlier report."""

    import csv

    report_path = PROJECT_ROOT / "output" / "outlier_report.csv"

    if not report_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Outlier report is unavailable",
        )

    with report_path.open("r", encoding="utf-8-sig", newline="") as file:
        outliers = list(csv.DictReader(file))

    return {
        "count": len(outliers),
        "outliers": outliers,
    }


# ============================================================
# 8. PORTFOLIO STATISTICS
# ============================================================

@router.get("/portfolio")
def portfolio_statistics():
    """Return Day 37 portfolio-level KPI statistics."""

    import csv

    stats_path = PROJECT_ROOT / "output" / "portfolio_stats.csv"

    if not stats_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Portfolio statistics are unavailable",
        )

    with stats_path.open("r", encoding="utf-8-sig", newline="") as file:
        statistics = list(csv.DictReader(file))

    return {
        "count": len(statistics),
        "statistics": statistics,
    }