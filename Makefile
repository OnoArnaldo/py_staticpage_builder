PYTHON=python3.12
VENV=.venv

PIP=$(VENV)/bin/pip
COMPILE=$(VENV)/bin/pip-compile
PY=$(VENV)/bin/python

REQ_DEV_IN=requirements/dev.in
REQ_PROD_IN=requirements/prod.in
REQ_DEV=requirements/dev.txt
REQ_PROD=requirements/prod.txt

RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m  # No Color

.PHONY: help dev build compile test clear install-dev install-prod check format

help:
	@echo "Usage:"
	@echo "  make [help | prod | dev | build | compile | test | clear | check | format]"

compile:$(REQ_DEV_IN)
	@echo "$(GREEN)[INFO] Compile $(REQ_DEV_IN)$(NC)"
	[ -f "$(REQ_DEV_IN)" ] \
		&& $(COMPILE) $(REQ_DEV_IN) \
		|| echo "$(RED)[WARNING] File not found: $(REQ_DEV_IN)$(NC)"

	@echo "$(GREEN)[INFO] Compile $(REQ_PROD_IN)$(NC)"
	[ -f "$(REQ_PROD_IN)" ] \
		&& $(COMPILE) $(REQ_PROD_IN) \
		|| echo "$(RED)[WARNING] File not found: $(REQ_PROD_IN)$(NC)"

dev:$(PY) install-dev
	@echo "$(GREEN)[INFO] Dev Created!$(NC)"

prod:$(PY) install-prod
	@echo "$(GREEN)[INFO] Prod Created!$(NC)"

$(PY):
	@echo "$(GREEN)[INFO] Create venv$(NC)"
	$(PYTHON) -m venv .venv
	$(PIP) install -U pip
	$(PIP) install --quiet pip-tools

install-dev:
	@echo "$(GREEN)[INFO] Install dev requirements$(NC)"
	[ -f "$(REQ_DEV)" ] \
		&& $(PIP) install --quiet -r $(REQ_DEV) \
		|| echo "$(RED)[WARNING] File not found: $(REQ_DEV)$(NC)"

install-prod:
	@echo "$(GREEN)[INFO] Install dev requirements$(NC)"
	[ -f "$(REQ_PROD)" ] \
		&& $(PIP) install --quiet -r $(REQ_PROD) \
		|| echo "$(RED)[WARNING] File not found: $(REQ_PROD)$(NC)"

clear:
	@echo "$(GREEN)[INFO] Clear installation$(NC)"
	rm -r -f $(VENV)

check:
	@echo "$(GREEN)[INFO] Check code$(NC)"
	ruff check ./src
	ruff check ./tests

format:
	@echo "$(GREEN)[INFO] Format code$(NC)"
	ruff format ./src
	ruff format ./tests
