"""Sprint 4 - Reports and Export Center."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

REPORTS_DIR = PROJECT_ROOT / "reports"

RADAR_DIR = REPORTS_DIR / "radar_charts"


# ============================================================
# HELPERS
# ============================================================

def format_size(size_bytes):
    """Return a readable file size."""

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"

    return (
        f"{size_bytes / (1024 ** 2):.2f} MB"
    )


def existing_file(filename):
    """Return report path when it exists."""

    path = REPORTS_DIR / filename

    return path if path.exists() else None


def download_report(
    path,
    label,
    mime,
    key,
):
    """Render download button for an existing report."""

    if path is None:
        st.warning(
            "Report file is currently unavailable."
        )
        return

    with path.open("rb") as file:
        data = file.read()

    st.download_button(
        label=label,
        data=data,
        file_name=path.name,
        mime=mime,
        key=key,
        use_container_width=True,
    )


# ============================================================
# HEADER
# ============================================================

st.title("Reports & Export Center")

st.caption(
    "Access generated screener reports, peer-comparison "
    "workbooks, custom-screen exports and company radar charts."
)


# ============================================================
# REPORT INVENTORY
# ============================================================

peer_report = existing_file(
    "peer_comparison.xlsx"
)

screener_report = existing_file(
    "screener_output.xlsx"
)

custom_csv = existing_file(
    "day20_custom_screen.csv"
)

custom_json = existing_file(
    "day20_custom_screen.json"
)

radar_files = (
    sorted(RADAR_DIR.glob("*.png"))
    if RADAR_DIR.exists()
    else []
)


st.subheader("Report Inventory")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Excel Reports",
        sum(
            path is not None
            for path in [
                peer_report,
                screener_report,
            ]
        ),
    )

with c2:
    st.metric(
        "Custom Exports",
        sum(
            path is not None
            for path in [
                custom_csv,
                custom_json,
            ]
        ),
    )

with c3:
    st.metric(
        "Radar Charts",
        len(radar_files),
    )

with c4:
    total_files = (
        sum(
            path is not None
            for path in [
                peer_report,
                screener_report,
                custom_csv,
                custom_json,
            ]
        )
        + len(radar_files)
    )

    st.metric(
        "Total Report Files",
        total_files,
    )


# ============================================================
# EXCEL REPORTS
# ============================================================

st.subheader("Excel Reports")

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        "### Peer Comparison Workbook"
    )

    st.write(
        "Peer-group comparison workbook containing "
        "the validated peer analytics."
    )

    if peer_report is not None:

        st.caption(
            f"File: {peer_report.name} | "
            f"Size: {format_size(peer_report.stat().st_size)}"
        )

    download_report(
        peer_report,
        "Download Peer Comparison Excel",
        (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        "peer_excel",
    )


with col2:

    st.markdown(
        "### Screener Output Workbook"
    )

    st.write(
        "Generated screener workbook containing "
        "company screening results."
    )

    if screener_report is not None:

        st.caption(
            f"File: {screener_report.name} | "
            f"Size: {format_size(screener_report.stat().st_size)}"
        )

    download_report(
        screener_report,
        "Download Screener Excel",
        (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        "screener_excel",
    )


# ============================================================
# CUSTOM SCREEN EXPORTS
# ============================================================

st.subheader("Custom Screen Exports")

e1, e2 = st.columns(2)

with e1:

    st.markdown("### CSV Export")

    if custom_csv is not None:

        st.caption(
            f"{custom_csv.name} | "
            f"{format_size(custom_csv.stat().st_size)}"
        )

        try:
            preview = pd.read_csv(
                custom_csv
            )

            st.write(
                f"Rows: {len(preview)}"
            )

            st.dataframe(
                preview.head(10),
                use_container_width=True,
                hide_index=True,
            )

        except Exception as exc:
            st.info(
                f"CSV preview unavailable: {exc}"
            )

    download_report(
        custom_csv,
        "Download Custom Screen CSV",
        "text/csv",
        "custom_csv",
    )


with e2:

    st.markdown("### JSON Export")

    if custom_json is not None:

        st.caption(
            f"{custom_json.name} | "
            f"{format_size(custom_json.stat().st_size)}"
        )

    download_report(
        custom_json,
        "Download Custom Screen JSON",
        "application/json",
        "custom_json",
    )


# ============================================================
# RADAR CHART LIBRARY
# ============================================================

st.subheader("Company Radar Charts")

if radar_files:

    radar_lookup = {
        path.stem: path
        for path in radar_files
    }

    selected_ticker = st.selectbox(
        "Select company radar chart",
        options=sorted(
            radar_lookup.keys()
        ),
        index=(
            sorted(
                radar_lookup.keys()
            ).index("TCS")
            if "TCS"
            in radar_lookup
            else 0
        ),
    )

    selected_radar = radar_lookup[
        selected_ticker
    ]

    st.image(
        str(selected_radar),
        caption=(
            f"{selected_ticker} "
            "Peer Percentile Radar"
        ),
        use_container_width=True,
    )

    with selected_radar.open(
        "rb"
    ) as file:
        radar_bytes = file.read()

    st.download_button(
        label=(
            f"Download {selected_ticker} Radar PNG"
        ),
        data=radar_bytes,
        file_name=selected_radar.name,
        mime="image/png",
        use_container_width=True,
    )

    st.caption(
        f"{len(radar_files)} company radar charts "
        "are currently available."
    )

else:
    st.warning(
        "No radar-chart files were found."
    )


# ============================================================
# FILE INVENTORY TABLE
# ============================================================

st.subheader("Generated File Inventory")

inventory = []

for path in [
    peer_report,
    screener_report,
    custom_csv,
    custom_json,
]:

    if path is not None:

        inventory.append(
            {
                "File": path.name,
                "Type":
                    path.suffix.upper()
                    .replace(".", ""),
                "Size":
                    format_size(
                        path.stat().st_size
                    ),
            }
        )


if radar_files:

    total_radar_size = sum(
        path.stat().st_size
        for path in radar_files
    )

    inventory.append(
        {
            "File":
                "radar_charts/*.png",
            "Type": "PNG",
            "Size":
                format_size(
                    total_radar_size
                ),
        }
    )


st.dataframe(
    pd.DataFrame(inventory),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# NOTE
# ============================================================

st.caption(
    "The Reports page exposes artifacts already generated "
    "by the project's analytics pipeline. Downloads use the "
    "actual files in the reports directory; missing reports "
    "are not represented as available."
)