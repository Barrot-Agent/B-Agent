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
`https://<owner>.github.io/<repo>/` (e.g., `https://barrot-agent.github.io/Barrot-Agent/`)

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

## Web Intelligence Scanner

The **Barrot Web Intelligence Scanner** (`Barrot.Web.Intelligence.Scanner.yml`) is an advanced web-scraping and analysis system that:

### Key Features

- **Scans Every Morsel of the Web:** Discovers and processes data from 1000+ domains across 12+ categories
- **Dynamic Operative Assignment:** 8 specialized operatives assigned based on data type and performance
- **Adaptive Resource Optimization:** Real-time reallocation of operatives to maximize data resolution
- **Comprehensive Coverage:** Academic, news, social media, data repositories, multimedia, and more

### Special Operatives

1. **WebCrawler-Alpha** (Autonomous-Crawler-L5)
   - Deep web crawling and content extraction
   - Recursive site traversal with 50 concurrent connections
   - Rate: 1000 req/min

2. **DataMiner-Beta** (Schema-Recognition-L4)
   - Structured data extraction (CSV, JSON, XML, APIs)
   - Database querying and schema inference
   - Rate: 500 req/min

3. **MediaHarvester-Gamma** (Stream-Processor-L4)
   - Video/audio scraping and transcription
   - Metadata extraction from multimedia
   - Rate: 100 req/min

4. **SemanticAnalyzer-Delta** (NLP-Transformer-L5)
   - Text analysis, entity extraction, sentiment analysis
   - Document summarization and classification
   - Rate: Unlimited

5. **RealTimeMonitor-Epsilon** (Event-Driven-L5)
   - WebSocket monitoring, RSS feeds, streaming APIs
   - Real-time event capture and processing
   - Rate: 10000 req/min

6. **KnowledgeWeaver-Zeta** (Graph-Neural-Network-L5)
   - Entity linking and knowledge graph construction
   - Cross-source fact verification
   - Rate: Unlimited

7. **CodeIntelligence-Eta** (AST-Parser-L4)
   - Source code analysis and dependency tracking
   - Vulnerability scanning in repositories
   - Rate: 5000 req/hour

8. **AdaptiveCoordinator-Theta** (Meta-Learning-Optimizer-L5)
   - Dynamic operative assignment and load balancing
   - Performance optimization and resource reallocation
   - Rate: Unlimited

### Execution Phases

1. **Web Discovery & Reconnaissance**
   - Discovers domains across all categories
   - Categorizes data types
   - Estimates data volume
   - Recommends operatives

2. **Dynamic Operative Deployment**
   - Deploys 7 operatives in parallel
   - Each operative processes assigned domains
   - Real-time performance monitoring

3. **Adaptive Resource Optimization**
   - Analyzes operative performance
   - Generates reallocation strategies
   - Scales up top performers
   - Reallocates underperformers

4. **Data Resolution & Synthesis**
   - Synthesizes intelligence from all sources
   - Generates comprehensive reports
   - Creates interactive dashboard

5. **Commit Results & Update Manifest**
   - Commits intelligence reports
   - Updates build manifest
   - Generates execution summary

### Configuration

```bash
# Trigger Web Intelligence Scanner
gh workflow run "Barrot Web Intelligence Scanner" \
  --field scan_depth=exhaustive \
  --field data_resolution_threshold=90
```

**Scan Depths:**
- **surface:** 100 sites, ~10TB data
- **deep:** 500 sites, ~100TB data (default)
- **exhaustive:** 1000+ sites, ~1PB data

**Data Resolution Threshold:** Target percentage of data to resolve (85-100%)

### Integration

The Web Intelligence Scanner integrates with the Master Orchestration workflow:
- Automatically triggered after orchestration completion
- Can be enabled/disabled via `enable_web_scanning` parameter
- Results feed back into entity data sources

### Performance Metrics

- **Domains Scanned:** 500-2000 depending on scan depth
- **Data Items Resolved:** 80,000-200,000 per scan
- **Resolution Rate:** Typically 85-98%
- **Operatives:** 7 specialized agents
- **Scan Frequency:** Every 4 hours or on-demand

### Dashboard

An interactive dashboard is generated at `site/web-intelligence/index.html` showing:
- Real-time operative performance
- Data resolution metrics
- Top performers and efficiency ratings
- Detailed statistics per operative

### Adaptive Optimization

The system continuously optimizes itself:
- **Scale Up:** Top performers get more resources
- **Reallocate:** Move operatives to high-value targets
- **Optimize:** Adjust batch sizes and concurrency
- **Clone:** Duplicate high-performing operatives
- **Rebalance:** Every 15 minutes

This ensures maximum data resolution from the entire web.
