"""Sprint 6 - Day 37: Cluster Profiling and Portfolio Statistics.

Creates:
- financial profiles for the five Day 36 clusters
- descriptive cluster archetype names
- Pearson correlation heatmap for 10 core KPIs
- broad-sector Z-score outlier report
- portfolio percentile/statistics report

The common analytical period is 2024-03 because it provides
near-complete KPI coverage across the 92-company universe.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DB_PATH = Path("nifty100.db")

CLUSTER_PATH = Path(
    "output/cluster_labels.csv"
)

PROFILE_PATH = Path(
    "output/cluster_profiles.csv"
)

OUTLIER_PATH = Path(
    "output/outlier_report.csv"
)

PORTFOLIO_STATS_PATH = Path(
    "output/portfolio_stats.csv"
)

HEATMAP_PATH = Path(
    "reports/correlation_heatmap.png"
)

ANALYTICAL_YEAR = "2024-03"


CLUSTER_FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


KPI_COLUMNS = [
    "npm_pct",
    "opm_pct",
    "roe_pct",
    "roce_pct",
    "roa_pct",
    "de_ratio",
    "icr",
    "asset_turnover",
    "revenue_cagr_5yr",
    "cfo_margin_pct",
]


KPI_LABELS = {
    "npm_pct": "NPM %",
    "opm_pct": "OPM %",
    "roe_pct": "ROE %",
    "roce_pct": "ROCE %",
    "roa_pct": "ROA %",
    "de_ratio": "Debt/Equity",
    "icr": "ICR",
    "asset_turnover": "Asset Turnover",
    "revenue_cagr_5yr": "Revenue CAGR 5Y %",
    "cfo_margin_pct": "CFO Margin %",
}


def load_day37_data() -> pd.DataFrame:
    """Load the common-period financial dataset."""

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            fr.npm_pct,
            fr.opm_pct,
            fr.roe_pct,
            fr.roce_pct,
            fr.roa_pct,
            fr.de_ratio,
            fr.icr,
            fr.asset_turnover,
            fr.revenue_cagr_5yr,
            fr.cfo_margin_pct
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
            AND fr.year = ?
        ORDER BY c.id
    """

    with sqlite3.connect(DB_PATH) as connection:
        data = pd.read_sql_query(
            query,
            connection,
            params=(ANALYTICAL_YEAR,),
        )

    return data


def load_cluster_data() -> pd.DataFrame:
    """Load Day 36 cluster assignments."""

    if not CLUSTER_PATH.exists():
        raise FileNotFoundError(
            f"Missing Day 36 output: {CLUSTER_PATH}"
        )

    clusters = pd.read_csv(
        CLUSTER_PATH
    )

    required = {
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid",
    }

    missing = (
        required
        - set(clusters.columns)
    )

    if missing:
        raise ValueError(
            "cluster_labels.csv missing columns: "
            + ", ".join(sorted(missing))
        )

    return clusters


def add_cluster_features(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Map source KPIs to the five clustering feature names."""

    result = data.copy()

    result[
        "return_on_equity_pct"
    ] = result["roe_pct"]

    result[
        "debt_to_equity"
    ] = result["de_ratio"]

    result[
        "operating_profit_margin_pct"
    ] = result["opm_pct"]

    # FCF CAGR is unavailable in the source database.
    # The Day 36 clustering model used a neutral constant.
    result[
        "fcf_cagr_5yr"
    ] = 0.0

    return result


def impute_cluster_features(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Apply the same sector-median imputation as Day 36."""

    result = data.copy()

    for feature in CLUSTER_FEATURES:

        sector_median = (
            result.groupby(
                "broad_sector"
            )[feature]
            .transform("median")
        )

        result[feature] = (
            result[feature]
            .fillna(sector_median)
        )

        global_median = (
            result[feature].median()
        )

        if pd.notna(global_median):

            result[feature] = (
                result[feature]
                .fillna(global_median)
            )

        else:

            result[feature] = (
                result[feature]
                .fillna(0.0)
            )

    return result


def build_cluster_profiles(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Compute mean and median of all five features by cluster."""

    records = []

    for cluster_id in sorted(
        data["cluster_id"].unique()
    ):

        subset = data[
            data["cluster_id"]
            == cluster_id
        ]

        record = {
            "cluster_id": int(cluster_id),
            "company_count": len(subset),
        }

        for feature in CLUSTER_FEATURES:

            record[
                f"{feature}_mean"
            ] = subset[
                feature
            ].mean()

            record[
                f"{feature}_median"
            ] = subset[
                feature
            ].median()

        records.append(record)

    return pd.DataFrame(records)

def assign_cluster_names(
    profiles: pd.DataFrame,
) -> dict[int, str]:
    """Assign reviewed names based on observed cluster profiles.

    Names describe the statistical characteristics of the
    current dataset and do not imply investment quality.
    """

    names = {
        0: "Low-Leverage Core",
        1: "High-Margin Low-Leverage",
        2: "Growth and Moderate Leverage",
        3: "High-Leverage Growth",
        4: "Extreme-ROE Outlier Cluster",
    }

    actual_clusters = set(
        profiles["cluster_id"]
        .astype(int)
        .tolist()
    )

    if actual_clusters != set(names):
        raise ValueError(
            "Unexpected cluster IDs: "
            f"{sorted(actual_clusters)}"
        )

    return names


def export_cluster_profiles(
    profiles: pd.DataFrame,
    names: dict[int, str],
) -> pd.DataFrame:
    """Export cluster statistics and descriptive names."""

    output = profiles.copy()

    output[
        "cluster_name"
    ] = output[
        "cluster_id"
    ].map(names)

    columns = [
        "cluster_id",
        "cluster_name",
        "company_count",
    ]

    columns += [
        column
        for column in output.columns
        if column not in columns
    ]

    output = output[
        columns
    ]

    PROFILE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        PROFILE_PATH,
        index=False,
    )

    return output


def update_cluster_labels(
    names: dict[int, str],
) -> pd.DataFrame:
    """Replace generic Day 36 labels with reviewed archetype names."""

    clusters = pd.read_csv(
        CLUSTER_PATH
    )

    clusters[
        "cluster_name"
    ] = clusters[
        "cluster_id"
    ].map(names)

    clusters.to_csv(
        CLUSTER_PATH,
        index=False,
    )

    return clusters


def save_correlation_heatmap(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Generate the Pearson correlation heatmap for ten KPIs."""

    correlation = (
        data[KPI_COLUMNS]
        .corr(
            method="pearson"
        )
    )

    HEATMAP_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(
        figsize=(13, 10)
    )

    image = ax.imshow(
        correlation.to_numpy(),
        aspect="auto",
        vmin=-1,
        vmax=1,
    )

    labels = [
        KPI_LABELS[column]
        for column in KPI_COLUMNS
    ]

    ax.set_xticks(
        range(len(labels))
    )

    ax.set_yticks(
        range(len(labels))
    )

    ax.set_xticklabels(
        labels,
        rotation=45,
        ha="right",
    )

    ax.set_yticklabels(
        labels
    )

    # Required annotated heatmap.
    for row in range(
        len(labels)
    ):
        for column in range(
            len(labels)
        ):

            value = correlation.iloc[
                row,
                column,
            ]

            if pd.notna(value):

                ax.text(
                    column,
                    row,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                )

    ax.set_title(
        "Pearson Correlation Matrix - "
        "10 Core KPIs (2024-03)"
    )

    fig.colorbar(
        image,
        ax=ax,
        label="Pearson Correlation",
    )

    fig.tight_layout()

    fig.savefig(
        HEATMAP_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    return correlation


def build_outlier_report(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Flag broad-sector observations with absolute Z-score > 3."""

    records = []

    for sector, sector_data in data.groupby(
        "broad_sector",
        dropna=False,
    ):

        for metric in KPI_COLUMNS:

            values = pd.to_numeric(
                sector_data[metric],
                errors="coerce",
            )

            mean = values.mean()

            std = values.std(
                ddof=0
            )

            if (
                pd.isna(std)
                or std == 0
            ):
                continue

            z_scores = (
                values - mean
            ) / std

            mask = (
                z_scores.abs()
                > 3
            )

            flagged = sector_data.loc[
                mask
            ]

            for index, row in (
                flagged.iterrows()
            ):

                records.append(
                    {
                        "company_id":
                            row["company_id"],
                        "company_name":
                            row["company_name"],
                        "broad_sector":
                            sector,
                        "metric":
                            metric,
                        "value":
                            row[metric],
                        "sector_mean":
                            mean,
                        "sector_std":
                            std,
                        "z_score":
                            z_scores.loc[
                                index
                            ],
                    }
                )

    columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "metric",
        "value",
        "sector_mean",
        "sector_std",
        "z_score",
    ]

    report = pd.DataFrame(
        records,
        columns=columns,
    )

    OUTLIER_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report.to_csv(
        OUTLIER_PATH,
        index=False,
    )

    return report


def build_portfolio_stats(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate P10-P90 and summary statistics for ten KPIs."""

    records = []

    for metric in KPI_COLUMNS:

        values = pd.to_numeric(
            data[metric],
            errors="coerce",
        ).dropna()

        records.append(
            {
                "kpi": metric,
                "count": len(values),
                "p10": values.quantile(
                    0.10
                ),
                "p25": values.quantile(
                    0.25
                ),
                "p50": values.quantile(
                    0.50
                ),
                "p75": values.quantile(
                    0.75
                ),
                "p90": values.quantile(
                    0.90
                ),
                "mean": values.mean(),
                "std": values.std(
                    ddof=1
                ),
            }
        )

    stats = pd.DataFrame(
        records
    )

    PORTFOLIO_STATS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    stats.to_csv(
        PORTFOLIO_STATS_PATH,
        index=False,
    )

    return stats


def print_cluster_review(
    data: pd.DataFrame,
    names: dict[int, str],
) -> None:
    """Print companies in each cluster for manual name review."""

    print(
        "\nCLUSTER COMPANY REVIEW"
    )

    print(
        "=" * 70
    )

    for cluster_id in sorted(
        names
    ):

        subset = data[
            data["cluster_id"]
            == cluster_id
        ].sort_values(
            "company_name"
        )

        print(
            f"\nCLUSTER {cluster_id}: "
            f"{names[cluster_id]}"
        )

        print(
            "COMPANIES:",
            len(subset),
        )

        company_list = (
            subset["company_name"]
            .astype(str)
            .tolist()
        )

        print(
            ", ".join(company_list)
        )


def validate_day37(
    data: pd.DataFrame,
    profiles: pd.DataFrame,
    names: dict[int, str],
    correlation: pd.DataFrame,
    portfolio_stats: pd.DataFrame,
) -> None:
    """Validate all Day 37 outputs."""

    assert len(data) == 92, (
        f"Expected 92 companies, got {len(data)}"
    )

    assert (
        data["company_id"].nunique()
        == 92
    ), "Expected 92 unique companies"

    assert len(profiles) == 5, (
        "Expected exactly 5 cluster profiles"
    )

    assert len(names) == 5, (
        "Expected 5 cluster names"
    )

    assert all(
        names.values()
    ), "Every cluster requires a name"

    assert correlation.shape == (
        10,
        10,
    ), (
        "Correlation matrix must be 10 x 10"
    )

    assert len(
        portfolio_stats
    ) == 10, (
        "Portfolio statistics must cover 10 KPIs"
    )

    required_files = [
        CLUSTER_PATH,
        PROFILE_PATH,
        OUTLIER_PATH,
        PORTFOLIO_STATS_PATH,
        HEATMAP_PATH,
    ]

    for path in required_files:

        assert path.exists(), (
            f"Missing output: {path}"
        )


def main():
    """Execute Sprint 6 Day 37."""

    financials = (
        load_day37_data()
    )

    clusters = (
        load_cluster_data()
    )

    data = financials.merge(
        clusters[
            [
                "company_id",
                "cluster_id",
                "distance_from_centroid",
            ]
        ],
        on="company_id",
        how="left",
        validate="one_to_one",
    )

    data = add_cluster_features(
        data
    )

    data = impute_cluster_features(
        data
    )

    profiles = (
        build_cluster_profiles(
            data
        )
    )

    names = (
        assign_cluster_names(
            profiles
        )
    )

    profiles = (
        export_cluster_profiles(
            profiles,
            names,
        )
    )

    update_cluster_labels(
        names
    )

    correlation = (
        save_correlation_heatmap(
            data
        )
    )

    outliers = (
        build_outlier_report(
            data
        )
    )

    portfolio_stats = (
        build_portfolio_stats(
            data
        )
    )

    validate_day37(
        data,
        profiles,
        names,
        correlation,
        portfolio_stats,
    )

    print(
        "\nDAY 37 - CLUSTER PROFILING "
        "AND STATISTICS"
    )

    print(
        "=" * 70
    )

    print(
        "COMPANIES:",
        len(data),
    )

    print(
        "CLUSTERS PROFILED:",
        len(profiles),
    )

    print(
        "\nCLUSTER PROFILES:"
    )

    display_columns = [
        "cluster_id",
        "cluster_name",
        "company_count",
        "return_on_equity_pct_median",
        "debt_to_equity_median",
        "revenue_cagr_5yr_median",
        "operating_profit_margin_pct_median",
    ]

    print(
        profiles[
            display_columns
        ].to_string(
            index=False
        )
    )

    print_cluster_review(
        data,
        names,
    )

    print(
        "\nCORRELATION MATRIX:",
        correlation.shape,
    )

    print(
        "OUTLIER FLAGS:",
        len(outliers),
    )

    print(
        "PORTFOLIO KPIS:",
        len(portfolio_stats),
    )

    print(
        "\nOUTPUT FILES:"
    )

    print(
        "CLUSTER PROFILES:",
        PROFILE_PATH
    )

    print(
        "CLUSTER LABELS:",
        CLUSTER_PATH
    )

    print(
        "CORRELATION HEATMAP:",
        HEATMAP_PATH
    )

    print(
        "OUTLIER REPORT:",
        OUTLIER_PATH
    )

    print(
        "PORTFOLIO STATS:",
        PORTFOLIO_STATS_PATH
    )

    print(
        "\nDAY 37 STATUS: PASS"
    )


if __name__ == "__main__":
    main()