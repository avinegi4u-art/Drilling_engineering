.PHONY: install-engine test-engine lint-engine

PYTHON ?= python3

install-engine:
	$(PYTHON) -m pip install -e "./mpd-platform/engine[dev]"

test-engine:
	cd mpd-platform/engine && $(PYTHON) -m pytest -v

lint-engine:
	cd mpd-platform/engine && $(PYTHON) -m ruff check mpd_engine tests
	cd mpd-platform/engine && $(PYTHON) -m mypy mpd_engine
