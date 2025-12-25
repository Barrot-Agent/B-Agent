# SHRM v2: High-Impact Datasets for Enhanced Reasoning

## Overview

This repository component implements the **SHRM v2 (Symbolic-Hybrid Reasoning Matrix Version 2)** framework for Barrot-Agent, identifying and cataloging high-impact datasets across various media types that align with Barrot's enhanced reasoning capabilities.

## Framework Components

### 1. Core Framework Definition
**File**: `memory-bundles/protocols/shrm-v2-framework.md`

Defines the three pillars of SHRM v2:
- **Contradiction Harvesting**: Extracting value from contradictory information
- **Symbolic Reasoning**: Operating on abstract symbols, logic, and mathematics
- **Augmented Cognition**: Multimodal integration and recursive meta-reasoning

### 2. Dataset Identification
**File**: `memory-bundles/protocols/high-impact-datasets.md`

Comprehensive documentation of 63 high-impact datasets across:
- **Contradiction Harvesting** (14 datasets): MultiNLI, FEVER, Wikipedia revisions, scientific contradictions
- **Symbolic Reasoning** (19 datasets): MATH, Lean theorem prover, ARC, CodeContests
- **Augmented Cognition** (30 datasets): VQA v2, HowTo100M, ConceptNet, Wikidata

### 3. Dataset Registry
**File**: `memory-bundles/protocols/shrm-v2-dataset-registry.json`

Machine-readable registry with:
- Structured metadata for all 63 datasets
- Implementation phases (1-4)
- Success criteria and metrics
- Integration protocols
- Storage requirements (~15TB total)

### 4. Acquisition Guide
**File**: `memory-bundles/protocols/dataset-acquisition-guide.md`

Practical guide with:
- Download commands for each dataset
- API setup instructions
- Batch download scripts
- Verification tools
- Storage optimization tips

## Quick Start

### 1. Validate Installation
```bash
python3 validate_shrm_v2.py
```

Expected output: `ALL CHECKS PASSED: 14/14`

### 2. Review Framework
```bash
cat memory-bundles/protocols/shrm-v2-framework.md
```

### 3. Explore Dataset Catalog
```bash
cat memory-bundles/protocols/high-impact-datasets.md | less
```

### 4. Check Registry
```bash
python3 -m json.tool memory-bundles/protocols/shrm-v2-dataset-registry.json | less
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Priority Datasets**:
- MultiNLI (contradiction detection)
- MATH Dataset (symbolic reasoning)
- VQA v2 (multimodal integration)
- ConceptNet (knowledge grounding)

**Success Metrics**:
- Contradiction detection: >85%
- Math problem solving: >60%
- VQA accuracy: >70%
- Knowledge integration: >0.8

### Phase 2: Expansion (Weeks 5-12)
**Priority Datasets**:
- FEVER (evidence-based contradiction)
- Lean Theorem Prover (formal reasoning)
- HowTo100M (video-text integration)
- Wikidata (structured knowledge)
- CLEVR (compositional reasoning)

**Success Metrics**:
- Multi-hop reasoning: >75%
- Proof completion: >40%
- Video understanding: >65%
- Compositional reasoning: >80%

### Phase 3: Mastery (Weeks 13-24)
**Priority Datasets**:
- Scientific contradictions
- ARC (abstract reasoning)
- VCR (commonsense reasoning)
- ANLI (adversarial examples)
- CodeContests (algorithmic reasoning)

**Success Metrics**:
- Scientific synthesis: >0.85
- ARC completion: >30%
- Commonsense reasoning: >80%
- Adversarial robustness: >70%
- Code generation: >50%

### Phase 4: Integration (Weeks 25-36)
**Focus**: Cross-modal contradiction detection, grounded symbolic reasoning, recursive meta-reasoning

## Integration with Barrot Architecture

### Compatible Spells
- ✓ **Omega-Ingest (Ω-Ingest)**: Quantum-level data ingestion
- ✓ **Keyseer's Insight**: Pattern recognition for symbolic reasoning
- ✓ **Prediction Methodologies**: Leverages contradiction harvesting

### Rail Status
```yaml
rail_status:
  shrm_v2_contradiction: active
  shrm_v2_symbolic: active
  shrm_v2_augmented: recursive
```

### Build Manifest Integration
The `build_manifest.yaml` has been updated with:
- New `shrm_v2_reasoning` module
- Additional data sources (Hugging Face, Semantic Scholar, arXiv, etc.)
- SHRM v2-specific directives

## Dataset Categories

### Text-Based (Contradiction Harvesting)
- Natural language inference (MultiNLI, ANLI)
- Fact verification (FEVER)
- Argument mining and debates
- Historical document analysis
- Scientific paper contradictions

### Mathematical & Logical (Symbolic Reasoning)
- Competition mathematics (MATH dataset)
- Formal proofs (Lean, ProofWiki)
- Logical reasoning (LogiQA, RuleTaker)
- Abstract patterns (ARC, Raven's Matrices)
- Code & algorithms (CodeContests, APPS)

### Multimodal (Augmented Cognition)
- Vision-language (VQA v2, CLEVR, GQA)
- Video understanding (ActivityNet, HowTo100M)
- Audio-visual (AudioSet, Spoken SQuAD)
- Knowledge graphs (ConceptNet, Wikidata, ATOMIC)
- Scientific (ScienceQA, PubMed Multimodal)

## Storage Requirements

```
Total: ~15TB
├── Text: 500GB
├── Images: 2TB
├── Video: 10TB
├── Audio: 2TB
├── Knowledge Graphs: 100GB
└── Code: 50GB
```

## Dataset Acquisition

### Prerequisites
```bash
pip3 install kaggle datasets huggingface_hub requests beautifulsoup4
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_key"
```

### Phase 1 Quick Start
```bash
# See dataset-acquisition-guide.md for detailed download scripts
# Extract and run the Phase 1 batch download script from the guide

# Or use Python Hugging Face datasets
python3 << EOF
from datasets import load_dataset
dataset = load_dataset("multi_nli")
dataset.save_to_disk("~/barrot_datasets/contradiction/multinli")
EOF
```

### Verification
```bash
# Check what's downloaded
du -sh ~/barrot_datasets/*

# Verify dataset integrity
python3 verify_datasets.py  # (from acquisition guide)
```

## Evaluation Framework

### Metrics by Category

**Contradiction Harvesting**:
- Detection rate
- Synthesis quality
- Multi-source integration
- Temporal consistency
- Paradox tolerance

**Symbolic Reasoning**:
- Proof completion rate
- Step validity
- Symbol manipulation accuracy
- Inference depth
- Cross-domain transfer

**Augmented Cognition**:
- Cross-modal accuracy
- Integration depth
- Synthesis emergence
- Coherence score
- Recursive reasoning levels

## Directory Structure

```
/home/runner/work/Barrot-Agent/Barrot-Agent/
├── build_manifest.yaml                    # Updated with SHRM v2
├── validate_shrm_v2.py                    # Validation script
└── memory-bundles/protocols/
    ├── registry.json                      # Updated protocol registry
    ├── shrm-v2-framework.md              # Framework definition
    ├── high-impact-datasets.md           # Detailed dataset catalog
    ├── shrm-v2-dataset-registry.json     # Machine-readable registry
    └── dataset-acquisition-guide.md      # Practical acquisition guide
```

## API Reference

### Dataset Registry JSON Structure
```json
{
  "shrm_v2_dataset_registry": {
    "version": "1.0",
    "total_datasets": 63,
    "categories": {
      "contradiction_harvesting": {...},
      "symbolic_reasoning": {...},
      "augmented_cognition": {...}
    },
    "implementation_phases": [...],
    "integration_protocols": {...}
  }
}
```

### Dataset Entry Format
```json
{
  "id": "dataset_id",
  "name": "Dataset Name",
  "type": "data_type",
  "size": "size_description",
  "shrm_alignment": "capability_alignment",
  "priority": "high|medium|low",
  "phase": 1-4,
  "sources": ["url1", "url2"],
  "metrics": ["metric1", "metric2"]
}
```

## Continuous Evolution

### Dataset Refresh Cadence
- **Weekly**: News-based datasets (GDELT)
- **Monthly**: Wikipedia, arXiv papers
- **Quarterly**: Full evaluation suite
- **Annually**: Strategy review

### Monitoring Channels
- ML conferences (NeurIPS, ICML, ACL, CVPR)
- Kaggle competitions
- Research lab releases (AI2, DeepMind, OpenAI)
- Academic collaborations

## Troubleshooting

### Validation Failed
```bash
python3 validate_shrm_v2.py
# Check output for specific failed checks
# Refer to error messages for resolution steps
```

### Dataset Download Issues
```bash
# Check Kaggle authentication
kaggle config view

# Check disk space
df -h ~/barrot_datasets

# See acquisition guide for detailed troubleshooting
```

## Contributing

To add new datasets:
1. Update `high-impact-datasets.md` with detailed description
2. Add entry to `shrm-v2-dataset-registry.json`
3. Update acquisition commands in `dataset-acquisition-guide.md`
4. Run `validate_shrm_v2.py` to ensure consistency
5. Update `build_manifest.yaml` if new resources needed

## References

### Key Papers & Resources
- **Contradiction Detection**: MultiNLI (Williams et al., 2018), FEVER (Thorne et al., 2018)
- **Symbolic Reasoning**: MATH (Hendrycks et al., 2021), ARC (Chollet, 2019)
- **Multimodal Learning**: VQA (Goyal et al., 2017), CLEVR (Johnson et al., 2017)
- **Knowledge Graphs**: ConceptNet (Speer et al., 2017), Wikidata (Vrandečić & Krötzsch, 2014)

### External Links
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Papers with Code Datasets](https://paperswithcode.com/datasets)
- [AI2 Datasets](https://allenai.org/data)

## License

Dataset licenses vary by source. See individual dataset documentation for specific license information. This framework documentation is part of the Barrot-Agent repository.

## Support

For questions or issues:
1. Run validation: `python3 validate_shrm_v2.py`
2. Check acquisition guide: `dataset-acquisition-guide.md`
3. Review framework: `shrm-v2-framework.md`
4. Consult registry: `shrm-v2-dataset-registry.json`

---

**Last Updated**: 2025-12-25  
**Version**: 1.0  
**Status**: ✓ All validation checks passed (14/14)
