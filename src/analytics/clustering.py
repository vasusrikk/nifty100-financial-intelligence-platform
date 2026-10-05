"""Sprint 6 - Day 36: KMeans Company Clustering.

Implements:
- 5-feature clustering matrix
- sector-median missing-value imputation
- z-score standardisation
- KMeans with 5 clusters
- deterministic random_state=42 equivalent
- elbow analysis for k=2..10
- centroid-distance calculation
- cluster_labels.csv
- elbow_plot.png

Environment note:
The local Windows Enterprise Code Integrity policy blocks
scikit-learn compiled extensions. Therefore the mathematical
StandardScaler and KMeans operations are implemented directly
with NumPy rather than weakening system security.

Data limitation:
Genuine FCF CAGR cannot be calculated because the source database
contains no genuine FCF values due to unavailable explicit CapEx.
The required fcf_cagr_5yr feature is retained with a neutral value
for every company, giving it zero discriminatory effect.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = Path("nifty100.db")

OUTPUT_PATH = Path(
    "output/cluster_labels.csv"
)

ELBOW_PATH = Path(
    "reports/elbow_plot.png"
)

N_CLUSTERS = 5
RANDOM_STATE = 42
MAX_ITER = 300
N_INIT = 10

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# DATA LOADING
# ============================================================

def load_company_features() -> pd.DataFrame:
    """Load comparable 2024-03 clustering inputs for all companies.

    2024-03 is used as the common analytical period because it
    provides near-complete coverage across the required financial
    features. The later 2024-09 rows are predominantly sparse and
    are therefore not suitable as the clustering reference period.
    """

    clustering_year = "2024-03"

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            fr.year,
            fr.roe_pct
                AS return_on_equity_pct,
            fr.de_ratio
                AS debt_to_equity,
            fr.revenue_cagr_5yr,
            fr.opm_pct
                AS operating_profit_margin_pct
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
            AND fr.year = ?
        ORDER BY c.id
    """

    with sqlite3.connect(DB_PATH) as connection:
        df = pd.read_sql_query(
            query,
            connection,
            params=(clustering_year,),
        )

    # Genuine FCF CAGR is unavailable because genuine FCF
    # cannot be calculated without an explicit CapEx source.
    #
    # Keep the Sprint 6 feature in the clustering schema but
    # assign it missing here. The imputation stage will apply
    # the documented neutral constant fallback. Because every
    # company receives the same value, this feature contributes
    # zero discriminatory information to KMeans.
    df["fcf_cagr_5yr"] = np.nan

    return df





# ============================================================
# IMPUTATION
# ============================================================

def impute_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Apply sector-median then global-median imputation."""

    result = df.copy()

    report = {}

    for feature in FEATURES:

        missing_before = int(
            result[feature].isna().sum()
        )

        # Required first-stage imputation:
        # sector median.
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

        missing_after_sector = int(
            result[feature].isna().sum()
        )

        # Global fallback for sectors where the metric
        # is completely unavailable.
        global_median = (
            result[feature].median()
        )

        if pd.notna(global_median):

            result[feature] = (
                result[feature]
                .fillna(global_median)
            )

            method = (
                "SECTOR_MEDIAN_WITH_GLOBAL_FALLBACK"
            )

        else:

            # Entire feature unavailable.
            #
            # Giving every company the same zero value means
            # its standardized value is also zero and it has
            # no influence on cluster assignment.
            result[feature] = (
                result[feature]
                .fillna(0.0)
            )

            method = (
                "SOURCE_UNAVAILABLE_NEUTRAL_ZERO"
            )

        missing_final = int(
            result[feature].isna().sum()
        )

        report[feature] = {
            "missing_before": missing_before,
            "missing_after_sector":
                missing_after_sector,
            "missing_final": missing_final,
            "method": method,
        }

    return result, report


# ============================================================
# STANDARD SCALER EQUIVALENT
# ============================================================

def standardize(
    df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform z-score standardisation.

    Equivalent mathematical transformation:

        z = (x - mean) / population_standard_deviation

    Constant features receive a scale of 1 so their
    standardized value becomes zero.
    """

    matrix = (
        df[FEATURES]
        .astype(float)
        .to_numpy()
    )

    means = np.mean(
        matrix,
        axis=0,
    )

    scales = np.std(
        matrix,
        axis=0,
        ddof=0,
    )

    scales = np.where(
        scales == 0,
        1.0,
        scales,
    )

    scaled = (
        matrix - means
    ) / scales

    return (
        scaled,
        means,
        scales,
    )


# ============================================================
# KMEANS IMPLEMENTATION
# ============================================================

def squared_distances(
    matrix: np.ndarray,
    centroids: np.ndarray,
) -> np.ndarray:
    """Return squared Euclidean distances."""

    return np.sum(
        (
            matrix[:, None, :]
            - centroids[None, :, :]
        ) ** 2,
        axis=2,
    )


def initialize_centroids(
    matrix: np.ndarray,
    k: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Initialise centroids using k-means++."""

    n_rows = matrix.shape[0]

    centroids = [
        matrix[
            rng.integers(
                0,
                n_rows,
            )
        ].copy()
    ]

    while len(centroids) < k:

        existing = np.array(
            centroids
        )

        distances = squared_distances(
            matrix,
            existing,
        )

        nearest = np.min(
            distances,
            axis=1,
        )

        total = nearest.sum()

        if total <= 0:
            index = int(
                rng.integers(
                    0,
                    n_rows,
                )
            )
        else:
            probabilities = (
                nearest / total
            )

            index = int(
                rng.choice(
                    n_rows,
                    p=probabilities,
                )
            )

        centroids.append(
            matrix[index].copy()
        )

    return np.array(
        centroids,
        dtype=float,
    )


def single_kmeans(
    matrix: np.ndarray,
    k: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Run one deterministic KMeans initialisation."""

    rng = np.random.default_rng(
        seed
    )

    centroids = initialize_centroids(
        matrix,
        k,
        rng,
    )

    labels = np.zeros(
        matrix.shape[0],
        dtype=int,
    )

    for _ in range(MAX_ITER):

        distances = squared_distances(
            matrix,
            centroids,
        )

        new_labels = np.argmin(
            distances,
            axis=1,
        )

        new_centroids = (
            centroids.copy()
        )

        for cluster_id in range(k):

            members = matrix[
                new_labels
                == cluster_id
            ]

            if len(members) == 0:

                # Re-seed an empty cluster using the
                # observation furthest from its nearest
                # existing centroid.
                nearest_distance = np.min(
                    distances,
                    axis=1,
                )

                replacement = int(
                    np.argmax(
                        nearest_distance
                    )
                )

                new_centroids[
                    cluster_id
                ] = matrix[
                    replacement
                ]

            else:

                new_centroids[
                    cluster_id
                ] = np.mean(
                    members,
                    axis=0,
                )

        if np.allclose(
            centroids,
            new_centroids,
            rtol=1e-8,
            atol=1e-10,
        ):
            labels = new_labels
            centroids = new_centroids
            break

        labels = new_labels
        centroids = new_centroids

    final_distances = (
        squared_distances(
            matrix,
            centroids,
        )
    )

    labels = np.argmin(
        final_distances,
        axis=1,
    )

    inertia = float(
        np.sum(
            final_distances[
                np.arange(
                    matrix.shape[0]
                ),
                labels,
            ]
        )
    )

    return (
        labels,
        centroids,
        inertia,
    )


def kmeans(
    matrix: np.ndarray,
    k: int,
    random_state: int = RANDOM_STATE,
    n_init: int = N_INIT,
):
    """Run multiple KMeans initialisations and retain the best."""

    best = None

    for run in range(n_init):

        seed = (
            random_state
            + run
        )

        result = single_kmeans(
            matrix,
            k,
            seed,
        )

        if (
            best is None
            or result[2] < best[2]
        ):
            best = result

    return best


# ============================================================
# ELBOW ANALYSIS
# ============================================================

def build_elbow(
    scaled: np.ndarray,
) -> pd.DataFrame:
    """Calculate inertia for k=2 through k=10."""

    records = []

    for k in range(2, 11):

        _, _, inertia = kmeans(
            scaled,
            k,
        )

        records.append(
            {
                "k": k,
                "inertia": inertia,
            }
        )

    return pd.DataFrame(
        records
    )


def save_elbow_plot(
    elbow: pd.DataFrame,
) -> None:
    """Save elbow curve as PNG."""

    ELBOW_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(
        figsize=(8, 5)
    )

    plt.plot(
        elbow["k"],
        elbow["inertia"],
        marker="o",
    )

    plt.axvline(
        N_CLUSTERS,
        linestyle="--",
    )

    plt.title(
        "KMeans Elbow Curve"
    )

    plt.xlabel(
        "Number of Clusters (k)"
    )

    plt.ylabel(
        "Inertia"
    )

    plt.xticks(
        range(2, 11)
    )

    plt.tight_layout()

    plt.savefig(
        ELBOW_PATH,
        dpi=150,
    )

    plt.close()


# ============================================================
# FINAL CLUSTER MODEL
# ============================================================

def build_final_clusters(
    df: pd.DataFrame,
    scaled: np.ndarray,
) -> pd.DataFrame:
    """Run the required five-cluster model."""

    (
        labels,
        centroids,
        _inertia,
    ) = kmeans(
        scaled,
        N_CLUSTERS,
    )

    distances = np.sqrt(
        squared_distances(
            scaled,
            centroids,
        )
    )

    assigned_distance = (
        distances[
            np.arange(
                len(labels)
            ),
            labels,
        ]
    )

    result = df.copy()

    result[
        "cluster_id"
    ] = labels.astype(int)

    result[
        "cluster_name"
    ] = result[
        "cluster_id"
    ].apply(
        lambda value:
        f"Cluster {value}"
    )

    result[
        "distance_from_centroid"
    ] = assigned_distance

    return result


# ============================================================
# EXPORT
# ============================================================

def export_labels(
    clustered: pd.DataFrame,
) -> pd.DataFrame:
    """Export required Day 36 cluster labels."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = clustered[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    output.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return output


# ============================================================
# QA
# ============================================================

def validate_day36(
    output: pd.DataFrame,
) -> None:
    """Enforce Day 36 acceptance checks."""

    assert len(output) == 92, (
        f"Expected 92 rows, got {len(output)}"
    )

    assert (
        output["company_id"].nunique()
        == 92
    ), "Expected 92 unique companies"

    assert (
        output["cluster_id"]
        .isna()
        .sum()
        == 0
    ), "Missing cluster IDs detected"

    assert (
        output[
            "distance_from_centroid"
        ]
        .isna()
        .sum()
        == 0
    ), "Missing centroid distances detected"

    valid_ids = set(
        output["cluster_id"]
        .astype(int)
        .unique()
    )

    assert valid_ids == {
        0, 1, 2, 3, 4
    }, (
        "Expected cluster IDs 0-4; "
        f"got {sorted(valid_ids)}"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    """Execute Sprint 6 Day 36."""

    raw = load_company_features()

    imputed, report = (
        impute_features(
            raw
        )
    )

    (
        scaled,
        means,
        scales,
    ) = standardize(
        imputed
    )

    elbow = build_elbow(
        scaled
    )

    save_elbow_plot(
        elbow
    )

    clustered = (
        build_final_clusters(
            imputed,
            scaled,
        )
    )

    output = export_labels(
        clustered
    )

    validate_day36(
        output
    )

    print(
        "\nDAY 36 KMEANS CLUSTERING COMPLETE"
    )

    print(
        "=" * 55
    )

    print(
        "COMPANIES:",
        len(output),
    )

    print(
        "UNIQUE COMPANIES:",
        output[
            "company_id"
        ].nunique(),
    )

    print(
        "CLUSTERS:",
        output[
            "cluster_id"
        ].nunique(),
    )

    print(
        "\nCLUSTER DISTRIBUTION:"
    )

    print(
        output[
            "cluster_id"
        ]
        .value_counts()
        .sort_index()
    )

    print(
        "\nFEATURE IMPUTATION:"
    )

    for feature in FEATURES:

        info = report[
            feature
        ]

        print(
            feature,
            "->",
            info["method"],
            "| before:",
            info["missing_before"],
            "| after sector:",
            info[
                "missing_after_sector"
            ],
            "| final:",
            info["missing_final"],
        )

    print(
        "\nFCF CAGR STATUS:"
    )

    print(
        "SOURCE UNAVAILABLE - "
        "neutral constant feature; "
        "zero clustering influence"
    )

    print(
        "\nSTANDARDISATION:"
    )

    for index, feature in enumerate(
        FEATURES
    ):
        print(
            feature,
            "| mean:",
            round(
                float(
                    means[index]
                ),
                6,
            ),
            "| scale:",
            round(
                float(
                    scales[index]
                ),
                6,
            ),
        )

    print(
        "\nELBOW INERTIA:"
    )

    print(
        elbow.to_string(
            index=False
        )
    )

    print(
        "\nCLUSTER ID RANGE:",
        output[
            "cluster_id"
        ].min(),
        "to",
        output[
            "cluster_id"
        ].max(),
    )

    print(
        "MISSING CLUSTERS:",
        output[
            "cluster_id"
        ].isna().sum(),
    )

    print(
        "MISSING DISTANCES:",
        output[
            "distance_from_centroid"
        ].isna().sum(),
    )

    print(
        "\nOUTPUT:",
        OUTPUT_PATH.resolve(),
    )

    print(
        "ELBOW PLOT:",
        ELBOW_PATH.resolve(),
    )

    print(
        "\nDAY 36 STATUS: PASS"
    )


if __name__ == "__main__":
    main()