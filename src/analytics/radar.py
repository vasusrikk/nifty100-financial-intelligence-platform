"""Sprint 3 - Day 19: Peer Percentile Radar Charts."""

from __future__ import annotations

import math
import sqlite3
from collections import defaultdict
from pathlib import Path

import matplotlib

# Headless backend for reliable PNG generation.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


DATABASE_PATH = Path("nifty100.db")
OUTPUT_DIR = Path("reports/radar_charts")


# Six dimensions keep the radar readable while covering
# profitability, efficiency, growth, cash flow and valuation.
RADAR_METRICS = [
    ("roe_pct", "ROE"),
    ("roce_pct", "ROCE"),
    ("revenue_cagr_5yr", "Revenue Growth"),
    ("pat_cagr_5yr", "PAT Growth"),
    ("cfo_margin_pct", "CFO Margin"),
    ("pe_ratio", "P/E Value"),
]


def valid_number(value):
    """Return True for finite numeric values."""

    if value is None:
        return False

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(value)


# ============================================================
# LOAD DAY 18 DATA
# ============================================================

def load_radar_data(
    database_path=DATABASE_PATH,
):
    """
    Load Day 18 percentile rows required by radar charts.
    """

    connection = sqlite3.connect(
        database_path
    )

    try:
        placeholders = ",".join(
            "?"
            for _ in RADAR_METRICS
        )

        metrics = [
            metric
            for metric, _ in RADAR_METRICS
        ]

        rows = connection.execute(
            f"""
            SELECT
                p.peer_group_name,
                p.company_id,
                p.is_benchmark,
                p.year,
                p.metric,
                p.raw_value,
                p.percentile,
                c.company_name
            FROM peer_percentiles AS p

            LEFT JOIN companies AS c
                ON c.id = p.company_id

            WHERE p.metric IN (
                {placeholders}
            )

            ORDER BY
                p.peer_group_name,
                p.company_id,
                p.metric
            """,
            metrics,
        ).fetchall()

    finally:
        connection.close()

    return rows


# ============================================================
# BUILD COMPANY PROFILES
# ============================================================

def build_company_profiles(rows):
    """
    Convert database rows into one radar profile per
    peer-group company.
    """

    profiles = {}

    for (
        peer_group,
        company_id,
        is_benchmark,
        year,
        metric,
        raw_value,
        percentile,
        company_name,
    ) in rows:

        key = (
            peer_group,
            company_id,
        )

        if key not in profiles:
            profiles[key] = {
                "peer_group_name":
                    peer_group,
                "company_id":
                    company_id,
                "company_name":
                    company_name
                    or company_id,
                "is_benchmark":
                    bool(is_benchmark),
                "year":
                    year,
                "metrics": {},
            }

        profiles[key][
            "metrics"
        ][metric] = {
            "raw_value": raw_value,
            "percentile": percentile,
        }

    return list(
        profiles.values()
    )


def get_profile_values(profile):
    """
    Return radar percentile values in RADAR_METRICS order.

    Missing percentile values remain None here.
    """

    values = []

    for metric, _ in RADAR_METRICS:

        data = profile[
            "metrics"
        ].get(metric, {})

        percentile = data.get(
            "percentile"
        )

        if valid_number(percentile):
            values.append(
                float(percentile)
            )
        else:
            values.append(None)

    return values


# ============================================================
# PEER MEDIAN
# ============================================================

def calculate_peer_medians(
    profiles,
):
    """
    Calculate median percentile for each radar dimension
    inside every peer group.
    """

    grouped = defaultdict(list)

    for profile in profiles:
        grouped[
            profile["peer_group_name"]
        ].append(profile)

    medians = {}

    for group_name, members in (
        grouped.items()
    ):

        group_values = []

        for index, (
            metric,
            _,
        ) in enumerate(
            RADAR_METRICS
        ):

            values = []

            for member in members:

                profile_values = (
                    get_profile_values(
                        member
                    )
                )

                value = (
                    profile_values[index]
                )

                if valid_number(value):
                    values.append(
                        float(value)
                    )

            if values:
                group_values.append(
                    float(
                        np.median(values)
                    )
                )
            else:
                group_values.append(
                    None
                )

        medians[
            group_name
        ] = group_values

    return medians


# ============================================================
# CHART HELPERS
# ============================================================

def safe_filename(value):
    """Convert company ID to a safe PNG filename."""

    value = str(value)

    return "".join(
        character
        if (
            character.isalnum()
            or character in "-_"
        )
        else "_"
        for character in value
    )


def prepare_plot_values(values):
    """
    Matplotlib cannot draw None on a filled radar polygon.

    Missing values are plotted as 0 only for visualization;
    the source percentile remains NULL in the database.
    """

    return [
        float(value)
        if valid_number(value)
        else 0.0
        for value in values
    ]


# ============================================================
# RADAR PNG
# ============================================================

def generate_radar_chart(
    profile,
    peer_median,
    output_dir=OUTPUT_DIR,
):
    """
    Generate one company-vs-peer-median radar PNG.
    """

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    labels = [
        label
        for _, label in RADAR_METRICS
    ]

    company_values = (
        prepare_plot_values(
            get_profile_values(
                profile
            )
        )
    )

    peer_values = (
        prepare_plot_values(
            peer_median
        )
    )

    dimension_count = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        dimension_count,
        endpoint=False,
    ).tolist()

    # Close polygons.
    plot_angles = (
        angles + angles[:1]
    )

    company_plot = (
        company_values
        + company_values[:1]
    )

    peer_plot = (
        peer_values
        + peer_values[:1]
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

    # Company percentile profile.
    axis.plot(
        plot_angles,
        company_plot,
        linewidth=2,
        label=profile[
            "company_id"
        ],
    )

    axis.fill(
        plot_angles,
        company_plot,
        alpha=0.15,
    )

    # Peer-group median.
    axis.plot(
        plot_angles,
        peer_plot,
        linewidth=2,
        linestyle="--",
        label="Peer Median",
    )

    title = (
        f"{profile['company_id']} - "
        f"{profile['company_name']}\n"
        f"Peer Group: "
        f"{profile['peer_group_name']}"
    )

    if profile["is_benchmark"]:
        title += " | Benchmark"

    axis.set_title(
        title,
        pad=25,
        fontsize=12,
        fontweight="bold",
    )

    axis.legend(
        loc="upper right",
        bbox_to_anchor=(
            1.28,
            1.12,
        ),
    )

    figure.tight_layout()

    filename = (
        safe_filename(
            profile["company_id"]
        )
        + ".png"
    )

    output_path = (
        output_dir / filename
    )

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_path


# ============================================================
# COMPLETE DAY 19 PIPELINE
# ============================================================

def generate_all_radar_charts(
    database_path=DATABASE_PATH,
    output_dir=OUTPUT_DIR,
):
    """
    Generate radar charts for every company explicitly
    assigned to one of the supplied 11 peer groups.
    """

    rows = load_radar_data(
        database_path
    )

    profiles = (
        build_company_profiles(
            rows
        )
    )

    medians = (
        calculate_peer_medians(
            profiles
        )
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated = []

    for profile in profiles:

        group_name = profile[
            "peer_group_name"
        ]

        output_path = (
            generate_radar_chart(
                profile,
                medians[group_name],
                output_dir,
            )
        )

        generated.append(
            output_path
        )

    return {
        "profiles": profiles,
        "peer_groups": len(
            medians
        ),
        "company_count": len(
            profiles
        ),
        "chart_count": len(
            generated
        ),
        "charts": generated,
        "output_dir": output_dir,
    }


# ============================================================
# DAY 19 QA
# ============================================================

def main():

    result = (
        generate_all_radar_charts()
    )

    print(
        "\n=== ORIGINAL SPRINT 3 - "
        "DAY 19 RADAR CHART QA ==="
    )

    print(
        "Peer groups:",
        result["peer_groups"],
    )

    print(
        "Peer-group companies:",
        result["company_count"],
    )

    print(
        "Radar metrics:",
        len(RADAR_METRICS),
    )

    print(
        "PNG charts generated:",
        result["chart_count"],
    )

    print(
        "Output directory:",
        result["output_dir"],
    )

    existing = [
        path
        for path in result["charts"]
        if path.exists()
    ]

    print(
        "PNG files verified:",
        len(existing),
    )

    if existing:

        sizes = [
            path.stat().st_size
            for path in existing
        ]

        print(
            "Smallest PNG:",
            min(sizes),
            "bytes",
        )

        print(
            "Largest PNG:",
            max(sizes),
            "bytes",
        )

    missing_percentiles = 0

    for profile in (
        result["profiles"]
    ):
        missing_percentiles += sum(
            value is None
            for value in get_profile_values(
                profile
            )
        )

    print(
        "Missing radar percentile values:",
        missing_percentiles,
    )


if __name__ == "__main__":
    main()