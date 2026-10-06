.PHONY: load ratios test report portfolio sectors acceptance dashboard api final-qa clean

# Load and validate source datasets
load:
	python -m src.etl.loader
	python -m src.etl.validator

# Build financial ratios
ratios:
	python -m src.analytics.populate_ratios

# Run complete automated test suite and generate HTML report
test:
	python -m pytest tests -q --html=reports/pytest_report.html --self-contained-html

# Generate all required reports:
# 92 company tearsheets + 11 sector reports + portfolio summary
report:
	python -m src.reports.batch_generate 

	python -m src.reports.sector_reports

	python -m src.reports.portfolio_summary

# Generate portfolio summary PDF
portfolio:
	python -m src.reports.portfolio_summary

# Generate all 11 sector reports
sectors:
	python -m src.reports.sector_reports

# Generate final Sprint 1-6 acceptance checklist
acceptance:
	python -m src.reports.acceptance_checklist

# Launch Streamlit dashboard
dashboard:
	python -m streamlit run src/dashboard/app.py

# Launch FastAPI development server
api:
	python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# Final automated QA
final-qa:
	python -m pytest tests -q --html=reports/pytest_report.html --self-contained-html
	python -m src.reports.batch_generate
	python -m src.reports.sector_reports
	python -m src.reports.portfolio_summary
	python -m src.reports.acceptance_checklist

# Remove Python/pytest caches
clean:
	python -c "import pathlib,shutil; [shutil.rmtree(p,ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache',ignore_errors=True)"