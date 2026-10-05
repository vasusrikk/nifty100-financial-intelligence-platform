from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


# ============================================================
# ROOT AND HEALTH
# ============================================================

def test_root():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


# ============================================================
# COMPANY ENDPOINTS
# ============================================================

def test_list_companies():
    response = client.get("/api/companies?limit=3")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3
    assert len(data["companies"]) == 3


def test_company_detail():
    response = client.get("/api/companies/TCS")
    assert response.status_code == 200

    data = response.json()
    assert data["company_id"] == "TCS"
    assert data["company_name"] == "Tata Consultancy Services Ltd"


def test_company_not_found():
    response = client.get("/api/companies/NOTREAL")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"


def test_company_ratios():
    response = client.get(
        "/api/companies/TCS/ratios",
        params={"year": "2024-03"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["company_id"] == "TCS"
    assert data["year"] == "2024-03"
    assert "roe_pct" in data
    assert "de_ratio" in data


def test_company_valuation():
    response = client.get(
        "/api/companies/TCS/valuation",
        params={"year": "2024-03"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["company_id"] == "TCS"
    assert data["year"] == "2024-03"
    assert "pe_ratio" in data
    assert "pb_ratio" in data


def test_company_prices():
    response = client.get(
        "/api/companies/TCS/prices",
        params={"limit": 3},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["company_id"] == "TCS"
    assert data["count"] == 3
    assert len(data["prices"]) == 3


def test_company_signals():
    response = client.get("/api/companies/TCS/signals")
    assert response.status_code == 200

    data = response.json()
    assert data["company_id"] == "TCS"
    assert data["count"] == 16
    assert len(data["signals"]) == 16


# ============================================================
# ANALYTICS ENDPOINTS
# ============================================================

def test_sector_summary():
    response = client.get("/api/analytics/sectors")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 10
    assert len(data["sectors"]) == 10


def test_sector_companies():
    response = client.get(
        "/api/analytics/sectors/Information%20Technology"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["sector"] == "Information Technology"
    assert data["count"] == 5


def test_latest_ratios():
    response = client.get("/api/analytics/latest-ratios")
    assert response.status_code == 200
    assert "count" in response.json()


def test_valuation_summary():
    response = client.get("/api/analytics/valuation")
    assert response.status_code == 200
    assert "count" in response.json()


def test_signal_summary():
    response = client.get("/api/analytics/signals")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 5
    assert len(data["signals"]) == 5


def test_cluster_analytics():
    response = client.get("/api/analytics/clusters")
    assert response.status_code == 200

    data = response.json()
    assert data["company_count"] == 92
    assert data["cluster_count"] == 5
    assert len(data["profiles"]) == 5


def test_outlier_analytics():
    response = client.get("/api/analytics/outliers")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 11
    assert len(data["outliers"]) == 11


def test_portfolio_statistics():
    response = client.get("/api/analytics/portfolio")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 10
    assert len(data["statistics"]) == 10


# ============================================================
# OPENAPI
# ============================================================

def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert data["openapi"].startswith("3.")
    assert len(data["paths"]) == 16



# ============================================================
# DAY 42 - VALIDATION AND EDGE CASES
# ============================================================

def test_company_limit_zero_rejected():
    response = client.get("/api/companies?limit=0")
    assert response.status_code == 422


def test_company_negative_limit_rejected():
    response = client.get("/api/companies?limit=-1")
    assert response.status_code == 422


def test_company_limit_above_max_rejected():
    response = client.get("/api/companies?limit=9999")
    assert response.status_code == 422


def test_unknown_company_ratios_not_found():
    response = client.get(
        "/api/companies/NOTREAL/ratios",
        params={"year": "2024-03"},
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Financial ratios not found for requested company/year"
    )


def test_unknown_ratio_year_not_found():
    response = client.get(
        "/api/companies/TCS/ratios",
        params={"year": "1900-01"},
    )
    assert response.status_code == 404


def test_price_limit_zero_rejected():
    response = client.get(
        "/api/companies/TCS/prices",
        params={"limit": 0},
    )
    assert response.status_code == 422


def test_unknown_sector_not_found():
    response = client.get("/api/analytics/sectors/NOTREAL")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sector not found"