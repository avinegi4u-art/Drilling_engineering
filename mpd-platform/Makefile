PYTHON ?= python3
ENGINE_DIR := engine

.PHONY: help install-engine test-engine lint-engine typecheck-engine

help:
	@echo "MPD Platform (Phase 1)"
	@echo "  install-engine    Install the calculation engine with test extras"
	@echo "  test-engine       Run engine unit tests"
	@echo "  lint-engine       Run Ruff on the engine package"
	@echo "  typecheck-engine  Run mypy on the engine package"

install-engine:
	$(PYTHON) -m pip install -e "$(ENGINE_DIR)[dev]"

test-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m pytest tests -v

lint-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m ruff check mpd_engine tests

typecheck-engine:
	cd $(ENGINE_DIR) && $(PYTHON) -m mypy mpd_engine
