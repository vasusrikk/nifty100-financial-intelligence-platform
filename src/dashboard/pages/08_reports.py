"""Sprint 4 - Reports and Export Center."""

from pathlib import Path
import sqlite3

import pandas as pd
import requests
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

REPORTS_DIR = PROJECT_ROOT / "reports"

RADAR_DIR = REPORTS_DIR / "radar_charts"

DATABASE_PATH = PROJECT_ROOT / "nifty100.db"


# ============================================================
# HELPERS
# ============================================================

def format_size(size_bytes):
    """Return a readable file size."""

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"

    return f"{size_bytes / (1024 ** 2):.2f} MB"


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


@st.cache_data(
    ttl=600,
    show_spinner=False,
)
def check_report_url(url):
    """
    Check whether an annual-report URL is reachable.

    Returns:
        (available, status_code, message)
    """

    if not url:
        return (
            False,
            None,
            "No annual-report URL is available.",
        )

    url = str(url).strip()

    if not url.lower().startswith(
        ("http://", "https://")
    ):
        return (
            False,
            None,
            "The stored annual-report URL is invalid.",
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=8,
            headers=headers,
        )

        status_code = response.status_code

        # Some servers do not support HEAD correctly.
        if status_code in {
            400,
            403,
            405,
        }:
            response = requests.get(
                url,
                allow_redirects=True,
                timeout=8,
                headers=headers,
                stream=True,
            )

            status_code = response.status_code

            response.close()

        if 200 <= status_code < 400:
            return (
                True,
                status_code,
                "Annual report is available.",
            )

        if status_code == 404:
            return (
                False,
                status_code,
                "Annual Report Unavailable - "
                "the source returned HTTP 404.",
            )

        return (
            False,
            status_code,
            "Annual Report Unavailable - "
            f"the source returned HTTP {status_code}.",
        )

    except requests.Timeout:
        return (
            False,
            None,
            "Annual Report Unavailable - "
            "the source did not respond within the timeout.",
        )

    except requests.RequestException as exc:
        return (
            False,
            None,
            "Annual Report Unavailable - "
            f"the source could not be reached: {exc}",
        )


# ============================================================
# HEADER
# ============================================================

st.title("Reports & Export Center")

st.caption(
    "Access generated screener reports, peer-comparison "
    "workbooks, valuation analysis, custom-screen exports "
    "and company radar charts."
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

valuation_report = existing_file(
    "valuation_summary.xlsx"
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
                valuation_report,
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
                valuation_report,
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


# ------------------------------------------------------------
# PEER COMPARISON
# ------------------------------------------------------------

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


st.divider()


# ------------------------------------------------------------
# SCREENER OUTPUT
# ------------------------------------------------------------

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


st.divider()


# ------------------------------------------------------------
# VALUATION SUMMARY
# ------------------------------------------------------------

st.markdown(
    "### Valuation Summary Workbook"
)

st.write(
    "Sector-relative valuation analysis for all 92 companies "
    "using P/E, P/B and EV/EBITDA, with transparent valuation "
    "flags and FCF-yield source-availability status."
)

if valuation_report is not None:
    st.caption(
        f"File: {valuation_report.name} | "
        f"Size: {format_size(valuation_report.stat().st_size)}"
    )

download_report(
    valuation_report,
    "Download Valuation Summary Excel",
    (
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    ),
    "valuation_excel",
)


# ============================================================
# ANNUAL REPORTS
# ============================================================

st.subheader("Annual Reports")

st.write(
    "Browse company annual reports by financial year. "
    "Available reports open directly from the BSE source."
)

with sqlite3.connect(
    DATABASE_PATH
) as connection:

    companies_df = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY company_name
        """,
        connection,
    )


company_options = {
    (
        f"{row.company_name} "
        f"({row.company_id})"
    ): row.company_id
    for row in companies_df.itertuples()
}


selected_company_label = st.selectbox(
    "Select company",
    options=list(
        company_options.keys()
    ),
    key="annual_report_company",
)

selected_company = company_options[
    selected_company_label
]


with sqlite3.connect(
    DATABASE_PATH
) as connection:

    reports_df = pd.read_sql_query(
        """
        SELECT
            Year AS year,
            Annual_Report AS annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY Year DESC
        """,
        connection,
        params=(selected_company,),
    )


if reports_df.empty:

    st.error(
        "Annual Report Unavailable - "
        "no annual-report records are available "
        "for this company."
    )

else:

    reports_df = reports_df.dropna(
        subset=["year"]
    )

    available_years = (
        reports_df["year"]
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    if not available_years:

        st.error(
            "Annual Report Unavailable - "
            "no financial-year information "
            "is available for this company."
        )

    else:

        selected_year = st.selectbox(
            "Select financial year",
            options=available_years,
            key="annual_report_year",
        )

        selected_rows = reports_df[
            reports_df[
                "year"
            ].astype(str)
            == selected_year
        ]

        valid_links = (
            selected_rows[
                "annual_report"
            ]
            .dropna()
            .astype(str)
            .str.strip()
        )

        valid_links = valid_links[
            valid_links != ""
        ]

        if valid_links.empty:

            st.error(
                "Annual Report Unavailable - "
                "no PDF link is available "
                "for the selected year."
            )

        else:

            report_url = (
                valid_links.iloc[0]
            )

            with st.spinner(
                "Checking annual-report availability..."
            ):

                (
                    report_available,
                    report_status,
                    report_message,
                ) = check_report_url(
                    report_url
                )

            if report_available:

                st.success(
                    f"Available - annual report "
                    f"for {selected_year}."
                )

                if report_status is not None:
                    st.caption(
                        "Source status: "
                        f"HTTP {report_status}"
                    )

                st.link_button(
                    "Open Annual Report PDF",
                    report_url,
                    use_container_width=True,
                )

            else:

                st.error(
                    report_message
                )

                if report_status is not None:
                    st.caption(
                        "Source status: "
                        f"HTTP {report_status}"
                    )


# ============================================================
# CUSTOM SCREEN EXPORTS
# ============================================================

st.subheader(
    "Custom Screen Exports"
)

e1, e2 = st.columns(2)


with e1:

    st.markdown(
        "### CSV Export"
    )

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
                "CSV preview unavailable: "
                f"{exc}"
            )

    download_report(
        custom_csv,
        "Download Custom Screen CSV",
        "text/csv",
        "custom_csv",
    )


with e2:

    st.markdown(
        "### JSON Export"
    )

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

st.subheader(
    "Company Radar Charts"
)

if radar_files:

    radar_lookup = {
        path.stem: path
        for path in radar_files
    }

    radar_tickers = sorted(
        radar_lookup.keys()
    )

    selected_ticker = st.selectbox(
        "Select company radar chart",
        options=radar_tickers,
        index=(
            radar_tickers.index(
                "TCS"
            )
            if "TCS" in radar_tickers
            else 0
        ),
    )

    selected_radar = (
        radar_lookup[
            selected_ticker
        ]
    )

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

        radar_bytes = (
            file.read()
        )

    st.download_button(
        label=(
            f"Download "
            f"{selected_ticker} "
            "Radar PNG"
        ),
        data=radar_bytes,
        file_name=(
            selected_radar.name
        ),
        mime="image/png",
        use_container_width=True,
    )

    st.caption(
        f"{len(radar_files)} "
        "company radar charts "
        "are currently available."
    )

else:

    st.warning(
        "No radar-chart files "
        "were found."
    )


# ============================================================
# FILE INVENTORY TABLE
# ============================================================

st.subheader(
    "Generated File Inventory"
)

inventory = []

for path in [
    peer_report,
    screener_report,
    valuation_report,
    custom_csv,
    custom_json,
]:

    if path is not None:

        inventory.append(
            {
                "File":
                    path.name,

                "Type":
                    (
                        path.suffix
                        .upper()
                        .replace(
                            ".",
                            "",
                        )
                    ),

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

            "Type":
                "PNG",

            "Size":
                format_size(
                    total_radar_size
                ),
        }
    )


st.dataframe(
    pd.DataFrame(
        inventory
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# VALUATION DATA NOTE
# ============================================================

st.info(
    "FCF Yield is unavailable in the current valuation "
    "workbook because the source dataset contains no populated "
    "FCF values for 2024-03. The platform does not fabricate "
    "FCF or FCF Yield from incomplete source data."
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