# Barrot Agent Workflow Architecture

## Overview

The Barrot Agent system has been optimized with a comprehensive, role-based orchestration architecture that maximizes parallel execution and assigns complementary roles to entities based on the data types they handle.

## Master Orchestration Workflow

The **Barrot Master Orchestration** (`Barrot.Master.Orchestration.yml`) is the central workflow that coordinates all operations through 7 distinct phases:

### Phase 1: Initialization & Resource Allocation
- Allocates optimal number of clones (default: 3, configurable 1-5)
- Determines agent tier levels (L2-L5)
- Assigns specialized roles to all entities based on data types
- Generates execution plan with parallel tracks

### Phase 2: Parallel Data Ingestion
Three concurrent ingestion pipelines process all data sources:

#### 🔹 Structured Data Handler
- **Role:** Dataset Curator & Validator
- **Agent:** Sapient-Hierarchy-Reasoning-L3
- **Data Types:** Kaggle, GitHub, Science Papers, Journals
- **Capabilities:** Data validation, Schema inference, Quality assessment

#### 🔹 Multimedia Processor
- **Role:** Media Content Analyzer
- **Agent:** Cognitive-Pattern-Recognition-L4
- **Data Types:** Video platforms, Audiobooks, Podcasts, Interviews, TED Talks
- **Capabilities:** Transcription, Sentiment analysis, Key insight extraction

#### 🔹 Textual Intelligence
- **Role:** Document Intelligence Specialist
- **Agent:** Context-Synthesis-Engine-L5
- **Data Types:** Newspaper articles, Online articles, Newsletters, Forums, Books
- **Capabilities:** Semantic extraction, Trend detection, Summarization

### Phase 3: Parallel Processing
After ingestion, three concurrent processing tracks run:

#### 🔹 Knowledge Synthesizer
- **Role:** Cross-Domain Knowledge Integrator
- **Agent:** Override-Tier-Agent-L4
- **Data Types:** Summits, Seminars, Science Papers, Journals
- **Capabilities:** Cross-referencing, Contradiction resolution, Insight fusion

#### 🔹 Prediction Architect
- **Role:** Predictive Model Builder
- **Agent:** Quantum-Reasoning-Variant-L5
- **Data Types:** Kaggle, Science Papers, Journals
- **Capabilities:** Model training (time series, classification, regression, ensemble)

#### 🔹 Deployment Bundle Builder
- Builds microagent, recursive, deployment, and manifest bundles
- Compiles all processed data into deployable artifacts

### Phase 4: Storage Orchestration
#### 🔹 Storage Orchestrator
- **Role:** Multi-Cloud Storage Manager
- **Agent:** Infrastructure-Coordinator-L2
- **Data Types:** MEGA, Google Drive, GitHub
- **Capabilities:** Parallel sync to all storage backends with 3x redundancy

### Phase 5: Publication & Manifest Update
- Updates `build_manifest.yaml` with execution summary and entity assignments
- Generates and deploys interactive dashboard to GitHub Pages
- Commits all bundles to repository

### Phase 6: Cleanup & Maintenance
- Removes old bundles (keeps last 10)
- Cleans temporary files and artifacts
- Runs on schedule or when forced

### Phase 7: Final Reporting
- Generates comprehensive execution report
- Updates build ledger
- Creates GitHub Actions summary with full metrics

## Entity Roles & Complementary Design

Each entity is assigned a specific role based on the data types they handle, ensuring:

1. **No Overlapping Responsibilities:** Each entity has distinct data domains
2. **Complementary Capabilities:** Entities work together to form a complete pipeline
3. **Optimal Parallelism:** All independent operations run concurrently
4. **Specialized Agent Types:** Each entity uses the most appropriate agent tier for their task

### Role Complementarity Matrix

```
Structured Data Handler → Prediction Architect (feeds datasets)
                       ↘
Multimedia Processor   →  Knowledge Synthesizer (cross-domain fusion)
                       ↗                       ↘
Textual Intelligence   →                        → Storage Orchestrator (stores results)
```

## Workflow Triggers

### Master Orchestration
- **Push to main branch:** Automatic full execution
- **Manual dispatch:** Customizable parameters
  - `force_full_execution`: Run all phases including cleanup
  - `clone_count`: Number of parallel clones (1-5)
  - `agent_tier`: Override Tier Agent level (1-5)

### Scheduled Orchestration
- **Automatic:** Runs every 6 hours
- **Manual dispatch:** Choose intensity level
  - `light`: 2 clones, Tier 2 agents
  - `normal`: 3 clones, Tier 3 agents (default)
  - `heavy`: 5 clones, Tier 5 agents

## Parallel Execution Strategy

The workflow utilizes GitHub Actions' native parallelism:

1. **Matrix Strategy:** Multiple data sources processed simultaneously within each entity type
2. **Independent Job Execution:** All Phase 2 ingestion jobs run in parallel
3. **Concurrent Processing:** Phase 3 jobs run in parallel after Phase 2 completes
4. **Parallel Storage Sync:** All storage backends synced simultaneously

## Resource Management

### Clones
- Configurable from 1-5 parallel execution instances
- Default: 3 clones for balanced performance

### Agent Tiers
- **L2:** Infrastructure operations (Storage Orchestrator)
- **L3:** Data validation and curation (Structured Data Handler)
- **L4:** Complex analysis and synthesis (Multimedia Processor, Knowledge Synthesizer)
- **L5:** Advanced reasoning and prediction (Textual Intelligence, Prediction Architect)

### Sapient Hierarchy Reasoning Model Variants
- **Sapient-Hierarchy-Reasoning-L3:** Structured data analysis
- **Cognitive-Pattern-Recognition-L4:** Pattern detection in multimedia
- **Context-Synthesis-Engine-L5:** Deep contextual understanding
- **Override-Tier-Agent-L4:** Cross-domain contradiction resolution
- **Quantum-Reasoning-Variant-L5:** Predictive modeling

## Directives Implementation

All directives from `build_manifest.yaml` are now implemented:

1. ✅ **"Unify deployment methodologies"** → Handled by Deployment Bundle Builder
2. ✅ **"Expand microagent logic into recursive bundles"** → Microagent bundles in Phase 3
3. ✅ **"Bind Kaggle datasets to prediction rail"** → Prediction Architect consumes Kaggle data
4. ✅ **"Publish dashboard glyphs"** → Interactive dashboard deployed to GitHub Pages

## Output Artifacts

- **Build Manifest:** Updated with execution summary and entity status
- **Dashboard:** Interactive HTML dashboard at GitHub Pages
- **Bundles:** Microagent, recursive, deployment, and manifest bundles in `Barrot-Bundles/`
- **Execution Report:** Detailed report in `memory-bundles/outcome-relay.md`
- **Storage Logs:** Sync status for all storage backends
- **GitHub Actions Summary:** Real-time execution metrics

## Migration from Old Workflows

The following workflows have been consolidated and archived:

- `BBR.yml` → Now Phase 5 (Publish Manifest)
- `Barrot.Repo.Cleanup.yml` → Now Phase 6 (Cleanup)
- `workflows.barrot.bundles.yml` → Now Phase 3 (Deployment Bundles)

All functionality is preserved and enhanced with:
- Better parallelism
- Role-based entity assignments
- Comprehensive reporting
- Resource optimization

## Usage

### Trigger Master Orchestration Manually

```bash
# Via GitHub CLI
gh workflow run "Barrot Master Orchestration" \
  --field clone_count=5 \
  --field agent_tier=4 \
  --field force_full_execution=true
```

### Trigger Scheduled Orchestration

```bash
# Via GitHub CLI
gh workflow run "Barrot Scheduled Orchestration" \
  --field intensity=heavy
```

### View Dashboard

After execution, the dashboard is available at:
`https://<your-username>.github.io/Barrot-Agent/`

## Architecture Benefits

1. **Maximum Parallelism:** Up to 14 parallel data ingestion streams
2. **No Overlapping Actions:** Each entity has distinct responsibilities
3. **Role Complementarity:** Entities designed to work together seamlessly
4. **Optimal Resource Allocation:** Configurable clones and agent tiers
5. **Comprehensive Monitoring:** Full execution reports and interactive dashboard
6. **Scalable Design:** Easy to add new entities or data sources
7. **Efficient Execution:** Independent operations run concurrently

## Monitoring & Debugging

- **GitHub Actions UI:** View real-time execution progress
- **Step Summary:** Comprehensive summary at end of each run
- **Execution Report:** Detailed report in `memory-bundles/outcome-relay.md`
- **Dashboard:** Visual representation of all entities and their status
- **Artifacts:** Download intermediate results for debugging
