# Barrot V3 Autonomous Experimentation — first integrated slice

This implementation extends existing Barrot sandbox, Apex Lattice discovery and MCP validation components. It adds static repository discovery, deterministic bounded pairwise-oriented variations, a hash-chained append-only experiment ledger, Docker-only execution, a separate verification run, a bounded persistent discovery tick and an explicit integration assessment.

## Execution contract

- Docker and its daemon must already be available.
- The configured image must already exist locally. Automatic pulls are disabled.
- Experiments run with networking disabled, read-only container root, dropped Linux capabilities, no-new-privileges, CPU/memory/process limits, temporary filesystem and execution timeout.
- Repository content is copied into a temporary workspace. Git metadata, virtual environments, caches, dotenv files, symlinks and common key/certificate files are excluded.
- Commands are argument vectors; no shell is invoked. Verification runs in a second fresh container against the same isolated workspace.
- Ledger tampering blocks further appends and integration assessment.
- No production credentials are passed to containers. This module does not write production source, merge, deploy or create pull requests.

## API

Use SandboxDiscoveryEngine.discover for static candidate discovery; VariationGenerator.generate for bounded configurations; ExperimentOrchestrator.execute for execution and evidence persistence; ContinuousDiscoveryScheduler.run_once from an external scheduler; and integration_assessment to check whether verified evidence plus explicit approval permits preparing a reviewable change. The integration assessment never merges or deploys.

## Known limitations

This first slice is not the complete autonomous runtime. Model-backed hypothesis generation, multi-agent reviewer adapters, objective-specific statistical evaluation, persistent service supervision, host-level firewall enforcement, digital twins, production XRP ingestion, point-in-time feature storage, leakage-safe walk-forward evaluation and forecast calibration remain separate work. Do not describe those capabilities as implemented until independently verified.

The full-suite CI job automatically discovers tests/test_experimentation.py.
