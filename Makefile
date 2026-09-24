.PHONY: load ratios test report dashboard api clean

# Load and validate the financial datasets
load:
	python -m src.etl.loader
	python -m src.etl.validator

# Build financial ratios
ratios:
	python -m src.analytics.populate_ratios

# Run automated tests
test:
	python -m pytest -v

# Reporting entry point
report:
	@echo "Report module will be implemented in the reporting sprint."

# Dashboard entry point
dashboard:
	@echo "Dashboard module will be implemented in the dashboard sprint."

# API entry point
api:
	@echo "API module will be implemented in the API sprint."

# Remove Python cache and pytest cache files
clean:
	python -c "import pathlib,shutil; [shutil.rmtree(p,ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache',ignore_errors=True)"