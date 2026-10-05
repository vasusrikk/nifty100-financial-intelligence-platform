"""Generate sector-relative radar charts for companies without peer charts."""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


DATABASE_PATH = Path("nifty100.db")
OUTPUT_DIR = Path("reports/radar_charts")

RADAR_METRICS = [
    ("roe_pct", "ROE"),
    ("roce_pct", "ROCE"),
    ("revenue_cagr_5yr", "Revenue Growth"),
    ("pat_cagr_5yr", "PAT Growth"),
    ("cfo_margin_pct", "CFO Margin"),
    ("pe_ratio", "P/E Value"),
]


def valid_number(value):
    """Return True when value is a finite number."""
    if value is None:
        return False

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(value)


def safe_filename(value):
    """Convert a company ID into the same safe filename used by radar.py."""
    return "".join(
        character
        if character.isalnum() or character in "-_"
        else "_"
        for character in str(value)
    )


def latest_ratio_value(connection, company_id, metric):
    """Return latest available non-null financial-ratio value."""

    row = connection.execute(
        f"""
        SELECT {metric}
        FROM financial_ratios
        WHERE company_id = ?
          AND {metric} IS NOT NULL
        ORDER BY year DESC
        LIMIT 1
        """,
        (company_id,),
    ).fetchone()

    return row[0] if row else None


def latest_pe_value(connection, company_id):
    """Return latest available non-null P/E value."""

    row = connection.execute(
        """
        SELECT pe_ratio
        FROM market_cap
        WHERE company_id = ?
          AND pe_ratio IS NOT NULL
        ORDER BY year DESC
        LIMIT 1
        """,
        (company_id,),
    ).fetchone()

    return row[0] if row else None


def get_raw_value(connection, company_id, metric):
    """Return latest available source value for a radar metric."""

    if metric == "pe_ratio":
        return latest_pe_value(
            connection,
            company_id,
        )

    return latest_ratio_value(
        connection,
        company_id,
        metric,
    )


def percentile_rank(value, population, reverse=False):
    """
    Calculate a 0-100 percentile rank.

    Higher is better for operating/growth metrics.

    For P/E Value, lower positive P/E receives the
    stronger percentile because it represents a lower
    valuation multiple within the sector.
    """

    if not valid_number(value):
        return None

    values = [
        float(item)
        for item in population
        if valid_number(item)
    ]

    if not values:
        return None

    value = float(value)

    if reverse:
        values = [
            item
            for item in values
            if item > 0
        ]

        if value <= 0 or not values:
            return None

    if len(values) == 1:
        return 50.0

    if reverse:
        below = sum(
            item > value
            for item in values
        )
        equal = sum(
            item == value
            for item in values
        )
    else:
        below = sum(
            item < value
            for item in values
        )
        equal = sum(
            item == value
            for item in values
        )

    percentile = (
        below + 0.5 * equal
    ) / len(values) * 100.0

    return float(percentile)


def load_company_universe(connection):
    """Load all companies and their broad sectors."""

    rows = connection.execute(
        """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector
        FROM companies AS c
        LEFT JOIN sectors AS s
            ON s.company_id = c.id
        ORDER BY c.id
        """
    ).fetchall()

    return [
        {
            "company_id": row[0],
            "company_name": row[1] or row[0],
            "sector": row[2] or "Unclassified",
        }
        for row in rows
    ]


def existing_company_ids(companies):
    """Determine which companies already have radar PNG files."""

    existing = set()

    for company in companies:
        filename = (
            safe_filename(
                company["company_id"]
            )
            + ".png"
        )

        if (OUTPUT_DIR / filename).exists():
            existing.add(
                company["company_id"]
            )

    return existing


def build_sector_profiles(connection, companies):
    """Build raw metric profiles for all companies."""

    profiles = []

    for company in companies:

        metrics = {}

        for metric, _ in RADAR_METRICS:
            metrics[metric] = get_raw_value(
                connection,
                company["company_id"],
                metric,
            )

        profiles.append(
            {
                **company,
                "metrics": metrics,
            }
        )

    return profiles


def calculate_sector_percentiles(profiles):
    """Calculate sector-relative percentiles for all profiles."""

    for profile in profiles:

        sector = profile["sector"]

        sector_members = [
            member
            for member in profiles
            if member["sector"] == sector
        ]

        percentiles = {}

        for metric, _ in RADAR_METRICS:

            value = profile[
                "metrics"
            ].get(metric)

            population = [
                member["metrics"].get(metric)
                for member in sector_members
            ]

            percentiles[metric] = (
                percentile_rank(
                    value,
                    population,
                    reverse=(
                        metric == "pe_ratio"
                    ),
                )
            )

        profile["percentiles"] = percentiles

    return profiles


def calculate_sector_median(profile, profiles):
    """Return median sector percentile for each radar dimension."""

    sector_members = [
        member
        for member in profiles
        if member["sector"] == profile["sector"]
    ]

    result = []

    for metric, _ in RADAR_METRICS:

        values = [
            member["percentiles"].get(metric)
            for member in sector_members
            if valid_number(
                member["percentiles"].get(metric)
            )
        ]

        if values:
            result.append(
                float(np.median(values))
            )
        else:
            result.append(None)

    return result


def plot_values(values):
    """Convert missing percentiles to zero only for visualization."""

    return [
        float(value)
        if valid_number(value)
        else 0.0
        for value in values
    ]


def generate_sector_radar(profile, profiles):
    """Generate one sector-relative radar PNG."""

    labels = [
        label
        for _, label in RADAR_METRICS
    ]

    company_values = [
        profile["percentiles"].get(metric)
        for metric, _ in RADAR_METRICS
    ]

    sector_median = calculate_sector_median(
        profile,
        profiles,
    )

    company_plot = plot_values(
        company_values
    )

    sector_plot = plot_values(
        sector_median
    )

    dimension_count = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        dimension_count,
        endpoint=False,
    ).tolist()

    plot_angles = angles + angles[:1]

    company_plot = (
        company_plot + company_plot[:1]
    )

    sector_plot = (
        sector_plot + sector_plot[:1]
    )

    figure = plt.figure(
        figsize=(8, 8)
    )

    axis = figure.add_subplot(
        111,
        polar=True,
    )

    axis.set_theta_offset(
        np.pi / 2
    )

    axis.set_theta_direction(-1)

    axis.set_xticks(angles)

    axis.set_xticklabels(
        labels,
        fontsize=10,
    )

    axis.set_ylim(
        0,
        100,
    )

    axis.set_yticks(
        [20, 40, 60, 80, 100]
    )

    axis.set_yticklabels(
        ["20", "40", "60", "80", "100"],
        fontsize=8,
    )

    axis.plot(
        plot_angles,
        company_plot,
        linewidth=2,
        label=profile["company_id"],
    )

    axis.fill(
        plot_angles,
        company_plot,
        alpha=0.15,
    )

    axis.plot(
        plot_angles,
        sector_plot,
        linewidth=2,
        linestyle="--",
        label="Sector Median",
    )

    title = (
        f"{profile['company_id']} - "
        f"{profile['company_name']}\n"
        f"Sector: {profile['sector']}"
    )

    axis.set_title(
        title,
        pad=25,
        fontsize=12,
        fontweight="bold",
    )

    axis.legend(
        loc="upper right",
        bbox_to_anchor=(1.28, 1.12),
    )

    figure.tight_layout()

    output_path = (
        OUTPUT_DIR
        / (
            safe_filename(
                profile["company_id"]
            )
            + ".png"
        )
    )

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_path


def main():
    """Generate only radar charts missing from the original peer output."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:
        companies = load_company_universe(
            connection
        )

        existing = existing_company_ids(
            companies
        )

        profiles = build_sector_profiles(
            connection,
            companies,
        )

        profiles = calculate_sector_percentiles(
            profiles
        )

        missing_profiles = [
            profile
            for profile in profiles
            if profile["company_id"]
            not in existing
        ]

        generated = []

        missing_source_values = 0

        for profile in missing_profiles:

            for metric, _ in RADAR_METRICS:
                if not valid_number(
                    profile["metrics"].get(metric)
                ):
                    missing_source_values += 1

            output_path = generate_sector_radar(
                profile,
                profiles,
            )

            generated.append(
                output_path
            )

            print(
                "GENERATED:",
                profile["company_id"],
                "|",
                profile["sector"],
            )

    finally:
        connection.close()

    png_files = list(
        OUTPUT_DIR.glob("*.png")
    )

    print()
    print(
        "=== SECTOR RADAR EXTENSION QA ==="
    )
    print(
        "Total companies:",
        len(companies),
    )
    print(
        "Original existing charts:",
        len(existing),
    )
    print(
        "Missing before extension:",
        len(missing_profiles),
    )
    print(
        "New charts generated:",
        len(generated),
    )
    print(
        "Total radar PNG files:",
        len(png_files),
    )
    print(
        "Missing source metric values:",
        missing_source_values,
    )

    final_existing = (
        existing_company_ids(
            companies
        )
    )

    final_missing = [
        company["company_id"]
        for company in companies
        if company["company_id"]
        not in final_existing
    ]

    print(
        "Matched company charts:",
        len(final_existing),
    )
    print(
        "Missing company charts:",
        len(final_missing),
    )

    status = (
        len(companies) == 92
        and len(final_existing) == 92
        and len(final_missing) == 0
    )

    print(
        "D-10 RADAR CHART STATUS:",
        "PASS" if status else "FAIL",
    )

    if final_missing:
        print(
            "Still missing:",
            ", ".join(final_missing),
        )


if __name__ == "__main__":
    main()