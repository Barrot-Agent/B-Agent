.PHONY: install install-dev install-dev-core install-dev-full install-ml install-ui environment-check lint format test test-core test-full test-fast docker-build docker-dev clean

install:
	python -m pip install -r requirements.txt

install-dev: install-dev-full

install-dev-core:
	python -m pip install -r requirements-dev-codespaces.txt
	python -m pre_commit install

install-dev-full:
	python -m pip install -r requirements-dev.txt
	python -m pre_commit install

install-ml:
	python -m pip install -r requirements-ml.txt

install-ui:
	python -m pip install -r requirements-ui.txt

environment-check:
	bash .devcontainer/health-check.sh

lint:
	flake8 barrot_agent tests
	mypy barrot_agent

format:
	black barrot_agent tests
	isort barrot_agent tests

test: test-full

test-core:
	python -m pytest \
tests/test_cognitive_integrity.py \
		tests/test_evolution_engine.py \
		tests/test_claim_integrity.py \
		tests/test_corroboration.py \
		tests/test_evidence_corroboration.py \
		tests/test_source_independence.py \
		tests/test_source_independent_corroboration.py \
		tests/test_evidence_store.py \
		tests/test_evidence_normalization.py \
		tests/test_claim_events.py \
		tests/test_evidence_pipeline_integration.py \
		tests/test_reactive_observers.py \
		tests/test_intelligence_events.py \
		tests/test_evidence_quality.py \
		tests/test_claim_lifecycle.py \
		tests/test_confidence_calibration.py \
		tests/test_weighted_corroboration.py \
		tests/test_risk_manager.py \
		tests/test_coinbase_trader.py \
		tests/test_repository_repair.py \
		tests/test_devcontainer_contract.py \
		tests/test_v3_scripts.py \
		tests/test_barrot_agent_script.py \
		tests/test_external_deploys_require_confirmation.py \
		tests/test_deploy_databricks.py \
		tests/test_defensive_runtime.py \
		tests/test_scientific_discovery.py \
		tests/test_millennium_claim_registry.py \
		tests/test_formal_benchmark.py \
		tests/test_bundle_engineering.py \
		tests/test_bundle_schema_normalization.py \
		tests/test_bundle_lifecycle.py \
		tests/test_mesh_topology.py \
		tests/test_obj_mesh_loader.py \
		tests/test_polygon_triangulation.py \
		tests/test_mmi_adapter.py \
		tests/test_mmi_contract.py \
		tests/test_mmi_execution.py \
		tests/test_mmi_integration.py \
		tests/test_mmi_v1.py \
		tests/test_source_acquisition.py \
		tests/test_source_registry.py \
		tests/test_data_registry.py \
		tests/test_repository_causality.py \
		tests/test_bundle_delivery.py \
		tests/test_verified_bundle_delivery.py \
		tests/test_termux_self_drop.py \
		tests/test_autonomous_bundle_delivery.py \
		tests/test_autonomous_real_bundle.py \
		tests/test_deliver_bundle_action.py \
		tests/test_signal_summary.py \
		tests/test_xrp_research_artifact.py \
		tests/test_forecast_ledger.py \
		tests/test_point_in_time_features.py \
		tests/test_automation_containment.py \
		tests/test_external_action_gates.py -v --no-cov

test-full:
	python -m pytest tests -v --no-cov

test-fast:
	python -m pytest tests/test_config.py tests/test_models.py -v

docker-build:
	docker build -t b-agent:latest .

docker-dev:
	docker compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov coverage.xml dist build *.egg-info
