# SHRM v2 Dataset Acquisition Quick Reference

## Purpose
This guide provides practical commands and scripts for acquiring the high-impact datasets identified for Barrot's SHRM v2 framework.

---

## Prerequisites

### Required Tools
```bash
# Python and pip
python3 --version
pip3 install kaggle datasets huggingface_hub requests beautifulsoup4

# Git for repository cloning
git --version

# Storage: ~15TB recommended for full dataset collection
# Start with Phase 1 datasets (~500GB)
```

### API Keys Setup
```bash
# Kaggle API
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_key"

# Hugging Face (optional, for faster downloads)
export HF_TOKEN="your_token"

# Create directories
mkdir -p ~/barrot_datasets/{contradiction,symbolic,augmented,mixed}
```

---

## Phase 1: Foundation Datasets (Priority: HIGH)

### 1. MultiNLI (Contradiction Detection)
```bash
# Via Kaggle
kaggle datasets download -d shankar394/multinli
unzip multinli.zip -d ~/barrot_datasets/contradiction/multinli

# Via Hugging Face
python3 << EOF
from datasets import load_dataset
dataset = load_dataset("multi_nli")
dataset.save_to_disk("~/barrot_datasets/contradiction/multinli_hf")
EOF
```

### 2. MATH Dataset (Symbolic Reasoning)
```bash
# Via Kaggle
kaggle datasets download -d samuelcortinhas/math-dataset
unzip math-dataset.zip -d ~/barrot_datasets/symbolic/math_dataset

# Via GitHub
git clone https://github.com/hendrycks/math.git ~/barrot_datasets/symbolic/math_github
```

### 3. VQA v2 (Multimodal Integration)
```bash
# Download questions and annotations
cd ~/barrot_datasets/augmented/vqa_v2
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Train_mscoco.zip
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Train_mscoco.zip
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip

# Download COCO images
wget http://images.cocodataset.org/zips/train2014.zip
wget http://images.cocodataset.org/zips/val2014.zip

# Extract
unzip "*.zip"
```

### 4. ConceptNet (Knowledge Grounding)
```bash
# Download latest ConceptNet dump
cd ~/barrot_datasets/augmented/conceptnet
wget https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz
gunzip conceptnet-assertions-5.7.0.csv.gz

# Or clone repository for code
git clone https://github.com/commonsense/conceptnet5.git
```

---

## Phase 2: Expansion Datasets

### 5. FEVER (Evidence-Based Contradiction)
```bash
# Via Kaggle
kaggle datasets download -d streicherlouw/fever
unzip fever.zip -d ~/barrot_datasets/contradiction/fever

# Official source
wget https://fever.ai/download/fever/train.jsonl
wget https://fever.ai/download/fever/dev.jsonl
```

### 6. Lean Theorem Prover Corpus
```bash
# Clone mathlib
git clone https://github.com/leanprover-community/mathlib.git ~/barrot_datasets/symbolic/lean_mathlib

# Download lean4 as well
git clone https://github.com/leanprover/lean4.git ~/barrot_datasets/symbolic/lean4
```

### 7. HowTo100M (Video-Text Integration)
```bash
# Download metadata and captions
cd ~/barrot_datasets/augmented/howto100m
wget https://www.rocq.inria.fr/cluster-willow/amiech/howto100m/howto100m_videos.zip
unzip howto100m_videos.zip

# Note: Full video download requires significant bandwidth
# See: https://github.com/antoine77340/howto100m
```

### 8. Wikidata (Structured Knowledge)
```bash
# Download latest JSON dump (warning: very large, 100GB+)
cd ~/barrot_datasets/augmented/wikidata
wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz

# For testing, use a sample
wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz -O - | gunzip | head -n 100000 > wikidata_sample.json
```

### 9. CLEVR (Compositional Reasoning)
```bash
# Download CLEVR v1.0
cd ~/barrot_datasets/augmented/clevr
wget https://dl.fbaipublicfiles.com/clevr/CLEVR_v1.0.zip
unzip CLEVR_v1.0.zip
```

---

## Phase 3: Mastery Datasets

### 10. Scientific Contradictions (arXiv)
```bash
# Using arXiv API
python3 << EOF
import urllib.request
import time

base_url = "http://export.arxiv.org/api/query?"
categories = ["cs.AI", "cs.LG", "cs.CL", "physics", "math"]

for cat in categories:
    query = f"search_query=cat:{cat}&start=0&max_results=1000"
    url = base_url + query
    response = urllib.request.urlopen(url).read()
    
    with open(f"arxiv_{cat.replace('.', '_')}.xml", "wb") as f:
        f.write(response)
    time.sleep(3)  # Rate limiting
EOF

# Or via Kaggle
kaggle datasets download -d Cornell-University/arxiv
```

### 11. ARC (Abstract Reasoning)
```bash
# Clone ARC repository
git clone https://github.com/fchollet/ARC.git ~/barrot_datasets/symbolic/arc

# Download from Kaggle competition
kaggle competitions download -c abstraction-and-reasoning-challenge
unzip abstraction-and-reasoning-challenge.zip -d ~/barrot_datasets/symbolic/arc_kaggle
```

### 12. VCR (Visual Commonsense Reasoning)
```bash
# Download from official source
cd ~/barrot_datasets/augmented/vcr
wget https://visualcommonsense.com/download/vcr1images.zip
wget https://visualcommonsense.com/download/vcr1annots.zip
unzip vcr1images.zip
unzip vcr1annots.zip
```

### 13. ANLI (Adversarial NLI)
```bash
# Via Hugging Face
python3 << EOF
from datasets import load_dataset
dataset = load_dataset("anli")
dataset.save_to_disk("~/barrot_datasets/contradiction/anli")
EOF

# Or via GitHub
git clone https://github.com/facebookresearch/anli.git ~/barrot_datasets/contradiction/anli_github
```

### 14. CodeContests
```bash
# Clone repository
git clone https://github.com/deepmind/code_contests.git ~/barrot_datasets/symbolic/codecontests

# Download dataset files
cd ~/barrot_datasets/symbolic/codecontests
# Follow instructions in repo README for full data download
```

---

## Automated Batch Download Script

### Download Phase 1 (Foundation)
```bash
#!/bin/bash
# save as: download_phase1.sh

set -e

BASE_DIR=~/barrot_datasets
mkdir -p $BASE_DIR/{contradiction,symbolic,augmented}

echo "=== Phase 1: Foundation Datasets ==="

# MultiNLI
echo "Downloading MultiNLI..."
kaggle datasets download -d shankar394/multinli -p $BASE_DIR/contradiction/
unzip -q $BASE_DIR/contradiction/multinli.zip -d $BASE_DIR/contradiction/multinli

# MATH Dataset
echo "Downloading MATH Dataset..."
kaggle datasets download -d samuelcortinhas/math-dataset -p $BASE_DIR/symbolic/
unzip -q $BASE_DIR/symbolic/math-dataset.zip -d $BASE_DIR/symbolic/math_dataset

# ConceptNet
echo "Downloading ConceptNet..."
mkdir -p $BASE_DIR/augmented/conceptnet
wget -q https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz \
  -O $BASE_DIR/augmented/conceptnet/conceptnet-assertions-5.7.0.csv.gz
gunzip $BASE_DIR/augmented/conceptnet/conceptnet-assertions-5.7.0.csv.gz

echo "Phase 1 datasets downloaded successfully!"
echo "Note: VQA v2 requires manual download due to size. See instructions above."
```

### Python Batch Downloader (Hugging Face)
```python
#!/usr/bin/env python3
# save as: download_hf_datasets.py

from datasets import load_dataset
import os

BASE_DIR = os.path.expanduser("~/barrot_datasets")
os.makedirs(BASE_DIR, exist_ok=True)

datasets_to_download = {
    "multi_nli": ("contradiction/multinli_hf", None),
    "fever": ("contradiction/fever_hf", "v1.0"),
    "anli": ("contradiction/anli_hf", None),
    "winogrande": ("augmented/winogrande_hf", "winogrande_xl"),
}

for dataset_name, (save_path, config) in datasets_to_download.items():
    print(f"Downloading {dataset_name}...")
    try:
        if config:
            dataset = load_dataset(dataset_name, config)
        else:
            dataset = load_dataset(dataset_name)
        
        full_path = os.path.join(BASE_DIR, save_path)
        dataset.save_to_disk(full_path)
        print(f"✓ {dataset_name} saved to {full_path}")
    except Exception as e:
        print(f"✗ Error downloading {dataset_name}: {e}")

print("\nHugging Face datasets downloaded successfully!")
```

---

## Dataset Verification Script

```python
#!/usr/bin/env python3
# save as: verify_datasets.py

import os
import json

BASE_DIR = os.path.expanduser("~/barrot_datasets")

expected_datasets = {
    "Phase 1 - Foundation": [
        "contradiction/multinli",
        "symbolic/math_dataset",
        "augmented/vqa_v2",
        "augmented/conceptnet"
    ],
    "Phase 2 - Expansion": [
        "contradiction/fever",
        "symbolic/lean_mathlib",
        "augmented/howto100m",
        "augmented/wikidata",
        "augmented/clevr"
    ],
    "Phase 3 - Mastery": [
        "symbolic/arc",
        "augmented/vcr",
        "contradiction/anli",
        "symbolic/codecontests"
    ]
}

def check_dataset(path):
    full_path = os.path.join(BASE_DIR, path)
    exists = os.path.exists(full_path)
    size_mb = 0
    if exists:
        for dirpath, dirnames, filenames in os.walk(full_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    size_mb += os.path.getsize(fp)
        size_mb = size_mb / (1024 * 1024)
    return exists, size_mb

print("="*60)
print("BARROT SHRM v2 DATASET VERIFICATION")
print("="*60)

total_size = 0
total_datasets = 0
found_datasets = 0

for phase, datasets in expected_datasets.items():
    print(f"\n{phase}:")
    for ds in datasets:
        total_datasets += 1
        exists, size = check_dataset(ds)
        if exists:
            found_datasets += 1
            total_size += size
            status = f"✓ FOUND ({size:.1f} MB)"
        else:
            status = "✗ MISSING"
        print(f"  {ds:40s} {status}")

print("\n" + "="*60)
print(f"Summary: {found_datasets}/{total_datasets} datasets found")
print(f"Total size: {total_size/1024:.2f} GB")
print("="*60)
```

---

## Storage Optimization Tips

### Compression
```bash
# Compress text datasets
find ~/barrot_datasets/contradiction -name "*.json" -exec gzip {} \;
find ~/barrot_datasets/symbolic -name "*.txt" -exec gzip {} \;

# Use tar for archiving processed datasets
tar -czf multinli_processed.tar.gz ~/barrot_datasets/contradiction/multinli/processed/
```

### Selective Download
```bash
# Download only train split for testing
python3 << EOF
from datasets import load_dataset
dataset = load_dataset("multi_nli", split="train[:1%]")  # Only 1% of training data
dataset.save_to_disk("~/barrot_datasets/contradiction/multinli_sample")
EOF
```

### Streaming (for very large datasets)
```python
from datasets import load_dataset

# Stream instead of downloading
dataset = load_dataset("wikipedia", "20220301.en", streaming=True)

# Process without full download
for example in dataset["train"].take(1000):
    # Process example
    pass
```

---

## Monitoring Download Progress

```bash
# Monitor disk usage
watch -n 5 'du -sh ~/barrot_datasets/*'

# Track download speeds
iftop -i eth0  # or your network interface

# Check specific dataset progress
ls -lh ~/barrot_datasets/contradiction/multinli/
```

---

## Integration with Barrot

### Update build_manifest.yaml after download
```yaml
dataset_status:
  phase_1_completion: 100%
  phase_2_completion: 60%
  phase_3_completion: 20%
  
  datasets_ingested:
    - multinli
    - math_dataset
    - conceptnet
    - vqa_v2
    - fever
    - lean_mathlib
```

### Trigger Omega-Ingest processing
```bash
# After datasets are downloaded, trigger ingestion
# (This would connect to your Barrot ingestion pipeline)
python3 barrot_ingest.py --datasets ~/barrot_datasets --mode shrm_v2
```

---

## Troubleshooting

### Kaggle API Issues
```bash
# Check authentication
kaggle config view

# Fix permissions
chmod 600 ~/.kaggle/kaggle.json
```

### Hugging Face Issues
```bash
# Login to Hugging Face
huggingface-cli login

# Check cache
ls -lh ~/.cache/huggingface/
```

### Disk Space Issues
```bash
# Check available space
df -h ~/barrot_datasets

# Find largest files
du -ah ~/barrot_datasets | sort -rh | head -20

# Clean cache
rm -rf ~/.cache/huggingface/downloads/*
```

---

## Next Steps

After downloading datasets:
1. Run verification script: `python3 verify_datasets.py`
2. Update build_manifest.yaml with dataset status
3. Begin Phase 1 training/evaluation
4. Monitor SHRM v2 performance metrics
5. Proceed to Phase 2 datasets based on Phase 1 results

For questions or issues, refer to:
- Main documentation: `high-impact-datasets.md`
- Framework details: `shrm-v2-framework.md`
- Dataset registry: `shrm-v2-dataset-registry.json`
