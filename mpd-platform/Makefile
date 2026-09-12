PYTHON ?= python3
ENGINE_DIR := engine
BACKEND_DIR := backend
DASHBOARD_DIR := dashboard

.PHONY: help install-engine install-backend test-engine test-backend lint-engine typecheck-engine api dashboard

help:
	@echo "MPD Platform"
	@echo "  install-engine    Install the calculation engine with test extras"
	@echo "  install-backend   Install FastAPI service (expects engine already installed)"
	@echo "  test-engine       Run engine unit tests"
	@echo "  test-backend      Run API tests"
	@echo "  lint-engine       Run Ruff on the engine package"
	@echo "  typecheck-engine  Run mypy on the engine package"
	@echo "  api               Run uvicorn on :8000"
	@echo "  dashboard         Run Streamlit on :8501"

install-engine:
	$(PYTHON) -m pip install -e "$(ENGINE_DIR)[dev]"

install-backend:
	$(PYTHON) -m pip install -e "$(ENGINE_DIR)"
	$(PYTHON) -m pip install -e "$(BACKEND_DIR)[dev]"

test-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m pytest tests -v

test-backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests -v

lint-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m ruff check mpd_engine tests

typecheck-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m mypy mpd_engine

api:
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	cd $(DASHBOARD_DIR) && $(PYTHON) -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
