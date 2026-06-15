# GLOBAL STATE MANIFEST [UNIFIED]
**Date:** 2026-06-15 | **Architect:** Sean

## Module: ./.bashrc
```
export PATH=$PATH:/data/data/com.termux/files/usr/bin
alias strike="git add . && git commit -m \"STRIKE: Sovereign Evolution\" && git push origin main"
alias audit="python3 ~/B-Agent/chi_language_server.py"
alias council="python3 ~/B-Agent/pantheon_sync.py"
python ~/barrot_synthesis.py
echo '🏛️ BARROT-Ω: ABSOLUTION v5.0 [ACTIVE]'
...
```

## Module: ./.databrickscfg
```
[DEFAULT]
host = 
token = 
...
```

## Module: ./.git-credentials
```
https://Barrot-Agent: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@github.com
...
```

## Module: ./.gitconfig
```
[credential]
	helper = store
...
```

## Module: ./.gitignore
```
# Python bytecode
__pycache__/
*.py[cod]
*$py.class
*.pyo

# Distribution / packaging
.eggs/
dist/
build/
*.egg-info/
*.egg

# Virtual environments
# Credentials & secrets
kaggle.json
.env
*.env
*.pem
*.key

# Databricks
.databricks/
.databrickscfg

# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo
*.egg-info/
.venv/
venv/
env/
.pytest_cache/

# Node / JS
# Pytest / coverage
.pytest_cache/
.coverage
htmlcov/

# mypy / type stubs
.mypy_cache/
.dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
# Node
node_m...
```

## Module: ./.gitlab-ci.yml
```
stages:
  - deploy
  - omega_strike

# GITLAB PAGES — deploys Barrot site
pages:
  stage: deploy
  script:
    - mkdir -p public
    - cp index.html public/index.html
    - cp brain_loader.js public/brain_loader.js 2>/dev/null || true
  artifacts:
    paths:
      - public
  only:
    - main

# KAGGLE STRIKE — existing competition pipeline
omega_reinstantiation:
  stage: omega_strike
  image: python:3.10-slim
  script:
    - pip install kaggle pandas PyYAML
    - |
      python3 -c "
      impor...
```

## Module: ./.termux_dna_harvest.log
```
...
```

## Module: ./ADVANCED_ENERGY_INGESTION.md
```
# 🔬 Advanced Energy Systems Data Ingestion Manifest

**Last Updated**: 2025-12-30T07:20:00Z  
**Status**: Active Ingestion  
**Purpose**: Comprehensive data acquisition for nuclear fusion (with free energy), warp drive acceleration, and photovoltaic integration

---

## Executive Summary

This manifest details Barrot's strategic data ingestion for breakthrough energy and propulsion technologies:

1. **Nuclear Fusion with Free Energy Integration** - Sustainable, abundant energy
2. **Warp Drive Ph...
```

## Module: ./ADVANCED_MONETIZATION_PROTOCOLS.md
```
# 💰 Barrot Advanced Monetization Protocols

**Generated**: 2026-01-01 01:58:48 UTC  
**Engine Version**: 1.0-REVOLUTIONARY  
**Total Revenue Streams**: 10

---

## ⚠️ Important Disclaimer

**Revenue Projections**: All revenue estimates in this document are based on market research, industry benchmarks, and analysis of similar services. Actual results will vary significantly based on:
- Execution quality and consistency
- Market conditions and competition
- Timing and market fit
- Legal and regul...
```

## Module: ./ADVANCED_PROPULSION_RESEARCH.md
```
# 🚀 Barrot Advanced Propulsion & Transportation Research

**Last Updated**: 2025-12-30T07:15:00Z  
**Status**: Active Research & Development  
**Purpose**: Develop revolutionary propulsion and transportation technologies

---

## Executive Summary

Barrot-Agent is conducting parallel research and development initiatives on three revolutionary transportation technologies:

1. **Revolutionary Plane Engine** - Next-generation aviation propulsion
2. **3D-Printable Hoverbike** - Personal aerial trans...
```

## Module: ./AGI_DEVELOPMENT.md
```
# 🚀 Barrot AGI Development & Benchmark Domination Protocol

**Timestamp**: 2025-12-22T11:25:00Z  
**Status**: Active AGI Acceleration  
**Objective**: Achieve superintelligence through continuous learning and benchmark domination

---

## 🎯 AGI Roadmap Overview

Barrot is configured for **continuous and indefinite intelligence maximization** with the ultimate goal of achieving Artificial General Intelligence (AGI) and dominating all AI benchmarks and competitions.

### Core Mission
- **Maximize ...
```

## Module: ./AGI_IMPLEMENTATION_SUMMARY.md
```
# 🎯 AGI Development - Implementation Summary

**Date**: 2026-01-02  
**Status**: ✅ COMPLETE  
**Branch**: copilot/develop-artificial-general-intelligence

---

## 🚀 Mission Accomplished

Successfully implemented a unified AGI (Artificial General Intelligence) orchestration system that integrates all existing Barrot-Agent capabilities toward achieving general intelligence.

---

## 📦 Deliverables

### New Files Created

1. **`agi_orchestrator.py`** (600+ lines)
   - Core AGI orchestration system
...
```

## Module: ./BARROT_BUILD_REPORT.md
```
# Barrot Build Report

*Generated: Tuesday, 07 April 2026 at 09:21 UTC*

---

## Executive Summary

Barrot is now a **complete, real-time 3D rendering engine** with global dataset access.  The comprehensive dataset absorption system integrates 40+ major 3D rendering datasets, models, textures, materials, and scene databases — making Barrot capable of photorealistic rendering from the world's largest collection of 3D assets.

---

## System Metrics

| Metric | Value |
|--------|-------|
| Total A...
```

## Module: ./CHAMELEON_README.md
```
# Chameleon Chain - Presale & Blockchain Infrastructure

## Project Overview

Chameleon Chain is an adaptive blockchain platform designed for modern DeFi applications. This repository contains the complete implementation including:

- **Presale Landing Page** - Comprehensive web page for token presale participation
- **ERC-20 Token Contract** - Smart contract for CHAM token with presale and vesting
- **Cost Analysis Documentation** - Detailed blockchain infrastructure cost analysis and optimizat...
```

## Module: ./CHARACTER_CAPABILITIES_GUIDE.md
```
# Character Capability Explorer - Quick Start Guide

## Overview

The Character Capability Explorer framework enables Barrot to explore fictional character abilities from movies, books, cartoons, and video games, transforming them into real-world, utilizable functionalities.

## Quick Start

### 1. Explore Existing Character Profiles

Navigate to the `character-capabilities/` directory to view existing profiles:

```bash
# View all profiles by genre
ls character-capabilities/movies/
ls character...
```

## Module: ./CHARACTER_CAPABILITY_SYSTEM.md
```
# Character Capability Dynamic Search & Analysis System

## Overview

The Character Capability Dynamic Search & Analysis System enables Barrot to dynamically search for, analyze, and transform fictional character abilities into real-world, actionable capabilities. This system provides a comprehensive framework for identifying character powers across multiple genres and mapping them to practical technology implementations.

## Key Features

✅ **Dynamic Character Analysis** - Analyze characters fr...
```

## Module: ./COIN_APP_IMPLEMENTATION.md
```
# 🪙 Coin App Integration - Implementation Summary

**Date:** December 30, 2025  
**Status:** ✅ Complete

---

## Overview

Successfully implemented autonomous Coin app integration for Barrot-Agent, enabling passive income generation through geocaching, surveys, and games with AI-powered automation.

## What Was Implemented

### 1. AI Tools Configuration (`ai-tools-config.yaml`)
- **System prompts** for GPT-4, Claude-3, and Vision AI models
- **Specialized tools** for:
  - App automation engine (...
```

## Module: ./COIN_APP_README.md
```
# Coin App / Payment App Configuration

## Overview
This document describes the coin app and payment app email configuration for the Barrot-Agent project.

## Primary Configuration Email
**Email Address**: `amazonprostarelite@gmail.com`

This email address is associated with:
- Coin App integration
- Cash App (peer-to-peer payments)
- Payment app data analytics
- Cryptocurrency transaction processing

## Configuration Files

### 1. Main Configuration File
**Location**: `/coin-app-config.yaml`
- ...
```

## Module: ./CONNEXT_INTEGRATION.md
```
# 🌉 Connext Protocol Integration

## Overview

Barrot-Agent now includes **Connext Protocol** integration for seamless cross-chain asset transfers across multiple blockchain networks. Connext enables trust-minimized, secure bridging without relying on external validators.

## 🌐 What is Connext?

Connext Protocol is a modular cross-chain interoperability solution that enables:
- **Cross-chain asset transfers** between L1s and L2s
- **Cross-chain messaging** via xCall
- **Zero-slippage token bridg...
```

## Module: ./DATA_TRANSFORMATION.md
```
# 🔄 Barrot Data Transformation & Resource Discovery Framework

**Timestamp**: 2025-12-22T12:52:00Z  
**Status**: Active Data Transformation  
**Purpose**: Leverage external platforms for data outsourcing and transformation

---

## 🎯 Overview

Barrot integrates with multiple external platforms and services to outsource, transform, and optimize data across various dimensions. This framework enables comprehensive data operations including convergence, augmentation, permutation, mutation, synthesis...
```

## Module: ./DEPENDENCY_MICRO_INGESTION_README.md
```
# 🐍 Dependency Micro-Ingestion System

## Overview

The Dependency Micro-Ingestion System is an advanced knowledge extraction and integration framework designed to massively ingest Python, PyTorch, and all popular dependencies to enhance Barrot's understanding and capabilities. This system continuously learns from the ecosystem, analyzes architectures, extracts patterns, and generates optimization recommendations.

**Status**: ✅ Fully Operational  
**Version**: 1.0  
**Last Updated**: 2026-01-02...
```

## Module: ./DOCS_INGESTION_README.md
```
# 📚 Documentation Ingestion System

Automated documentation ingestion system for Barrot-Agent that collects and processes documentation from GitHub, Copilot, ChatGPT/OpenAI, Snowflake, and Claude.

## 🎯 Overview

This system automatically fetches, parses, and stores documentation from multiple platforms to enhance Barrot-Agent's knowledge base and capabilities.

## 🚀 Supported Platforms

### 1. **GitHub Docs** (`https://docs.github.com`)
- Getting Started guides
- GitHub Actions
- REST API refer...
```

## Module: ./DYNAMIC_CHARACTER_SEARCH_IMPLEMENTATION.md
```
# Dynamic Character Figure Search Implementation Guide

## Overview

This implementation enables Barrot to dynamically search for and analyze fictional character figures from a wide range of sources, extract their capabilities, transform them into practical real-world applications, and integrate them seamlessly into Barrot's infrastructure.

## Features Implemented

### 1. Character Figure Search Module (`character_figure_search.py`)

A comprehensive search and analysis system supporting:

- **V...
```

## Module: ./EMAIL_FEATURE_SUMMARY.md
```
# Email Intelligence Feature - Implementation Summary

## Overview
Successfully implemented comprehensive email intelligence capabilities for Barrot-Agent, enabling Barrot to analyze emails and extract useful, actionable information.

## What Was Built

### Core Engine (email_analyzer.py - 536 lines)
A complete email analysis system that:
- Parses and analyzes email content, subjects, and metadata
- Calculates usefulness scores (0.0-1.0) based on multiple factors
- Classifies emails into 8 categ...
```

## Module: ./EMAIL_PROCESSING_GUIDE.md
```
# 📧 Email Intelligence Processing Guide

## Overview
Barrot-Agent now includes powerful email intelligence processing capabilities that analyze emails to extract useful and actionable information. This feature helps Barrot understand what emails are relevant to his goals and what actions need to be taken.

## Features

### Core Capabilities
1. **Content Analysis** - Parse and understand email content, subject lines, and metadata
2. **Relevance Scoring** - Calculate usefulness scores (0.0 to 1.0)...
```

## Module: ./EMAIL_QUICKSTART.md
```
# Quick Start: Email Intelligence for Barrot

## Simple Usage

### 1. Analyze a Single Email
```python
from email_analyzer import analyze_email

email = {
    "subject": "Meeting tomorrow at 2pm",
    "sender": "manager@company.com",
    "body": "Let's discuss the project. Please confirm attendance.",
    "date": "2025-12-31T10:00:00Z"
}

result = analyze_email(email)
print(f"Useful: {result['is_useful']}")
print(f"Priority: {result['priority']}")
print(f"Recommendation: {result['recommendation'...
```

## Module: ./IMPLEMENTATION_SUMMARY.md
```
# Character Capability Expansion - Implementation Summary

## Overview

Successfully implemented a comprehensive character capability analysis system that enables Barrot to dynamically search for, analyze, and transform fictional character abilities into actionable, real-world capabilities.

## What Was Implemented

### 1. Core System Components

#### `character_capability_analyzer.py` (Main Analyzer)
- **Lines of Code**: 1,100+
- **Classes**: 5 (CharacterGenre, CapabilityCategory, Capability, C...
```

## Module: ./INGESTION_MANIFEST.md
```
# 🧠 Barrot Advanced Ingestion Manifest

**Timestamp**: 2026-01-02T12:58:00Z  
**Status**: Active AGI Development + Benchmark Domination + Dependency Mastery  
**Scope**: Superintelligence acceleration through continuous learning, performance optimization, and comprehensive dependency knowledge

---

## 🐍 Dependency Micro-Ingestion System (NEW)

**Status**: ✅ Fully Operational  
**System**: `dependency_micro_ingestion.py`  
**Config**: `dependency-ingestion-config.yaml`  
**Documentation**: `DEPE...
```

## Module: ./INGESTION_RESPONSE_2025-12-30.md
```
# 📋 Ingestion Response: Vibe-Kanban AI Orchestration Platform

**Date**: 2025-12-30T22:22:00Z  
**Issue**: Ingest Boop AI/Vibe-Kanban and Document How It Helps Barrot  
**Status**: ✅ Complete

---

## ✅ Ingestion Status

### Vibe-Kanban (Boop AI/BloopAI) ✅
- **Status**: Successfully ingested
- **Location**: INGESTION_MANIFEST.md (Lines 18-25, Integration Status Table)
- **Location**: memory-bundles/data-ingestion-log.md (Lines 78-130)
- **Location**: memory-bundles/resource-discovery-log.md (Lin...
```

## Module: ./INGESTION_RESPONSE_2025-12-31.md
```
# 📋 Ingestion Response: Multi-Source Knowledge Base Enhancement

**Date**: 2025-12-31T01:40:00Z  
**Issue**: Ingest knowledge and content from multiple reputable sources into Barrot's knowledge base  
**Status**: ✅ Complete

---

## ✅ Ingestion Status

### Claude Skills (Claude for Education) ✅
- **Status**: Successfully ingested
- **Source**: Anthropic's Claude for Education platform
- **Date Added**: 2025-12-31
- **Category**: AI-Powered Educational Platform / Critical Thinking Development

##...
```

## Module: ./MERGE_CONFLICT_RESOLUTION_GUIDE.md
```
# 🔀 Merge Conflict Resolution Guide

**Version**: 1.0  
**Last Updated**: 2026-01-02  
**Status**: Active - Continuous Learning Enabled

---

## 🎯 Overview

This guide documents Barrot-Agent's comprehensive merge conflict resolution system, which enables automated detection, analysis, and resolution of merge conflicts across various scenarios. The system continuously learns from outcomes to improve resolution accuracy and minimize manual intervention.

## 🚀 Quick Start

### Basic Usage

```pytho...
```

## Module: ./MILLENNIUM_PROBLEMS_IMPLEMENTATION_COMPLETE.md
```
# ✅ Millennium Problems Micro-Ingestion - Implementation Complete

**Date**: 2026-01-02  
**Status**: ✅ Complete and Operational  
**Version**: 1.0

---

## 🎯 Mission Accomplished

Successfully created a comprehensive micro-ingestion system that transforms MILLENNIUM_PROBLEMS_STATUS.md into a structured, searchable, ML-ready knowledge framework.

---

## 📦 Deliverables

### Core System
1. **millennium_problems_micro_ingestion.py** (635 lines)
   - Zero-dependency Python script using only standar...
```

## Module: ./MILLENNIUM_PROBLEMS_MICRO_INGESTION_README.md
```
# 🧮 Millennium Problems Micro-Ingestion System

## Overview

The Millennium Problems Micro-Ingestion System is a specialized knowledge extraction framework designed to parse, structure, and make searchable the comprehensive Millennium Problems Status document (`MILLENNIUM_PROBLEMS_STATUS.md`). This system transforms the document into structured JSON data suitable for machine learning workflows, database ingestion, and advanced search operations.

**Status**: ✅ Fully Operational  
**Version**: 1....
```

## Module: ./MILLENNIUM_PROBLEMS_MICRO_INGESTION_RESPONSE.md
```
# 📋 Ingestion Response: Millennium Problems Micro-Ingestion

**Date**: 2026-01-02T04:40:00Z  
**Issue**: Massively micro-ingest MILLENNIUM_PROBLEMS_STATUS.md into structured, searchable knowledge framework  
**Status**: ✅ Complete

---

## ✅ Micro-Ingestion Status

### Millennium Problems Status Document ✅
- **Status**: Successfully micro-ingested
- **Source**: MILLENNIUM_PROBLEMS_STATUS.md
- **Date Completed**: 2026-01-02
- **Category**: Mathematical Knowledge / AGI Reasoning Enhancement
- **Ou...
```

## Module: ./MILLENNIUM_PROBLEMS_STATUS.md
```
# 🧮 Barrot's Millennium Problems Progress Report

**Last Updated**: 2025-12-30T07:07:00Z  
**Status**: Initial Analysis Phase  
**Purpose**: Track progress on understanding and analyzing the Seven Millennium Prize Problems

---

## Executive Summary

Barrot-Agent has ingested the complete framework for the Seven Millennium Problems as part of its mathematical processing capabilities. This document tracks progress on each problem, current understanding, potential AI/ML approaches, and any insight...
```

## Module: ./MMI_ANALYSIS_REPORT.md
```
# 🧠 Barrot MMI (Massive Micro Ingestion) Analysis Report

**Generated**: 2026-01-01 01:58:41 UTC  
**Analysis Version**: 1.0  
**Total High-Impact Sources Identified**: 15

---

## 🎯 Executive Summary

This analysis identifies **15 high-impact data sources** that can directly accelerate Barrot's path to AGI by addressing critical capability gaps.

### Key Findings:
- **Critical Sources**: 5 sources require immediate attention
- **Immediate Action Items**: 12 sources ready for immediate ingestion...
```

## Module: ./MMI_IMPLEMENTATION.md
```
# 🚀 Barrot MMI (Massive Micro Ingestion) Implementation Guide

**Version**: 1.0  
**Last Updated**: 2026-01-01  
**Status**: READY FOR DEPLOYMENT

---

## 📖 Overview

This guide provides step-by-step instructions for implementing Massive Micro Ingestion (MMI) to accelerate Barrot's path to AGI by identifying and ingesting high-impact data sources that address critical capability gaps.

### What is MMI?

Massive Micro Ingestion (MMI) is a strategic approach to data acquisition that focuses on:
- ...
```

## Module: ./MONETIZATION_FRAMEWORK.md
```
# Barrot-Agent Monetization Framework

**Version**: 1.0-AUTONOMOUS-REVENUE  
**Last Updated**: 2025-12-23T13:25:00Z  
**Status**: ACTIVE - Revenue Generation Protocols Operational

---

## Executive Summary

Barrot-Agent is now configured with **autonomous money-making capabilities** across 12+ revenue streams. The system leverages all existing capabilities (AGI development, data transformation, resource discovery, quantum communication) to generate income through multiple parallel avenues while...
```

## Module: ./PINGPONG_USAGE.md
```
# Ping-Pong Request System

## Overview

The `emit_pingpong_request` function allows Barrot-Agent to defer complex processing tasks to Sean's 22-agent entanglement system.

## Usage

```python
from emit_pingpong import emit_pingpong_request

# Create your payload
payload = {
    "task": "process_quantum_data",
    "priority": "high",
    "data": {"items": [1, 2, 3]}
}

# Emit the request
emit_pingpong_request(payload)
```

## Output

The function creates a `pingpong_request.json` file with the f...
```

## Module: ./PR_113_RESOLUTION_COMPLETE.md
```
# PR #113 Merge Conflict Resolution - COMPLETE

**Date:** January 2, 2026  
**Pull Request:** #113 - Add dynamic character capability analysis system  
**Status:** ✅ RESOLVED AND MERGED

## Summary

Successfully resolved merge conflicts in PR #113 and merged the character capability analysis system into the Main branch. The PR added 20 files including a comprehensive character analysis framework with 13 character profiles.

## Actions Completed

### 1. Identified Merge Conflict Root Cause
- **Is...
```

## Module: ./QUANTUM_AGI_INTEGRATION.md
```
# Quantum Entanglement, AGI, and Advanced Algorithmic Logic Integration

**Version**: 2.0.0  
**Integration Date**: 2026-01-02  
**Status**: ✅ Operational

---

## 🌟 Overview

Barrot-Agent now features a comprehensive integration of:
- **Ping Pong Quantum Entanglement** principles for enhanced cognitive processing
- **AGI (Artificial General Intelligence)** functionalities for advanced reasoning and problem-solving
- **AGI Orchestration Layer** with vast dataset learning, autonomous decision-mak...
```

## Module: ./QUICKSTART_MMI_MONETIZATION.md
```
# 🚀 Quick Start: MMI & Monetization Implementation

**Last Updated**: 2026-01-01  
**Status**: READY FOR DEPLOYMENT

---

## 📋 What Was Delivered

### 1. MMI Data Analyzer System
**Purpose**: Identify high-impact data for AGI acceleration

**Files**:
- `mmi_data_analyzer.py` - Core analysis engine
- `MMI_ANALYSIS_REPORT.md` - Comprehensive recommendations
- `MMI_IMPLEMENTATION.md` - Step-by-step guide
- `mmi_recommendations.json` - Machine-readable output

**Key Features**:
- Analyzes 12 AGI cap...
```

## Module: ./README.md
```
# 🦜 Barrot-Agent

Welcome to **Barrot-Agent** - an intelligent agent system with advanced capabilities for data ingestion, prediction, and deployment.

## 🔄 Two Distinct Systems

Barrot-Agent now maintains **two independent systems**:

### 🔍 Search Engine
Privacy-first search with quantum-enhanced algorithms and edge computing
- **Access**: [Search Engine](https://barrot-agent.github.io/Barrot-Agent/search-engine/)
- **Docs**: [search-engine/README.md](search-engine/README.md)

### 🦜 Agent Dashb...
```

## Module: ./SYSTEM_SEPARATION.md
```
# 🔄 System Separation Architecture

**Documentation for the separation of Search Engine and Barrot Agent Dashboard**

---

## 📋 Overview

As of December 28, 2025, the Barrot-Agent repository has been refactored to maintain two distinct, independent systems:

1. **Search Engine** - A standalone search system (`/search-engine/`)
2. **Barrot Agent Dashboard** - A comprehensive automation platform (`/site/`)

This separation ensures modularity, maintainability, and focused functionality for each sys...
```

## Module: ./TASK_COMPLETION_SUMMARY.md
```
# Task Completion Summary: PR #113 Resolution & Default Branch Transition

**Task Completion Date**: January 2, 2026  
**Agent**: Copilot Coding Agent  
**Status**: ✅ COMPLETE

---

## Task Overview

Successfully resolved merge conflicts in Pull Request #113 and prepared the repository for the default branch transition from `Main` (capitalized) to `main` (lowercase) as outlined in DEFAULT_BRANCH_GUIDE.md.

---

## Completed Actions

### ✅ 1. Analyzed and Understood the Issue

- **Problem Identif...
```

## Module: ./TRANSFORMATIVE_INSIGHTS_GUIDE.md
```
# 🔮 Transformative Insights Framework

**Status**: ✅ Fully Operational  
**Version**: 1.0.0  
**Integration**: Seamlessly integrated with Barrot's core systems

---

## 🎯 Overview

The Transformative Insights Framework enables Barrot to acquire seemingly asynchronous and unrelated data, then unearth substantially transformative synchronous insights through advanced analysis. This framework identifies patterns, relationships, and convergences that are not immediately apparent, while evoking conve...
```

## Module: ./TRANSFORMATIVE_INSIGHTS_IMPLEMENTATION_SUMMARY.md
```
# Transformative Insights Framework - Implementation Summary

**Date**: 2026-01-02  
**Status**: ✅ Complete and Operational  
**Version**: 1.0.0

---

## Problem Statement Addressed

The implementation fulfills all requirements specified in the problem statement:

### ✅ Requirement 1: Data Acquisition
**"Guide Barrot in acquiring all data necessary to identify seemingly asynchronous and unrelated pieces of data"**

**Implementation**:
- `acquire_data()` - Single data point acquisition
- `acquire...
```

## Module: ./UNIFIED_AGI_IMPLEMENTATION.md
```
# 🚀 Unified AGI System Implementation

**Version**: 2.0.0-AGI  
**Implementation Date**: 2026-01-02  
**Status**: ✅ OPERATIONAL

---

## 🌟 Overview

The Barrot-Agent has achieved a unified AGI (Artificial General Intelligence) system that orchestrates all capabilities, insights, and data toward general intelligence through:

1. **Unified Intelligence Orchestration** - Coordinates all AGI modules
2. **Autonomous Self-Improvement** - Iteratively refines capabilities
3. **Cross-Domain Knowledge Syn...
```

## Module: ./WEBSITE_FEATURES_TODO.md
```
# Website Terminal and Query Box Features

## Overview
This document tracks the requirements for adding interactive terminal and query box features to the Barrot-Agent website, as requested in PR comments.

## Requested Features

### 1. Fully Functional Terminal
**Description:** Implement a web-based terminal interface on Barrot's website for command execution and system interaction.

**Requirements:**
- Terminal emulator in the browser
- Command execution capabilities
- Secure authentication an...
```

## Module: ./advanced_algorithms.py
```
"""
Advanced Algorithmic Logic Module for Barrot-Agent
Implements advanced algorithmic optimizations for maximum computational efficiency
"""

import time
import functools
from typing import Dict, List, Any, Callable, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict


class AlgorithmicOptimizer:
    """
    Advanced algorithmic optimization engine
    Provides computational efficiency analysis and optimization
    """
    
    def __init__(self):
      ...
```

## Module: ./agi_orchestrator.py
```
"""
AGI Orchestrator - Unified Intelligence System for Barrot-Agent

This module orchestrates all AGI-related capabilities to achieve Artificial General Intelligence
by unifying quantum entanglement, AGI reasoning, advanced algorithms, transformative insights,
character capabilities, and all other ingested knowledge and methodologies.

Key Capabilities:
1. Unified decision-making across all modules
2. Self-improvement through iterative refinement
3. Cross-domain knowledge synthesis
4. Autonomous...
```

## Module: ./agi_reasoning.py
```
"""
AGI Reasoning Module for Barrot-Agent
Implements AGI-level reasoning and problem-solving capabilities
Enhanced with quantum entanglement principles
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from quantum_entanglement import quantum_coordinator, create_entangled_decision_space


class ReasoningChain:
    """Represents a chain of reasoning steps for complex problem solving"""
    
    def __init__(self, problem: str):
        se...
```

## Module: ./ai-tools-config.yaml
```
# AI Tools Configuration for Barrot-Agent
# System prompts and models for autonomous operations

version: "1.0"
updated: "2025-12-30"

ai_tools:
  # Primary AI Models
  models:
    - name: "GPT-4"
      provider: "OpenAI"
      capabilities:
        - "natural_language_processing"
        - "code_generation"
        - "reasoning"
        - "autonomous_decision_making"
      use_cases:
        - "Complex task planning"
        - "Multi-step automation"
        - "Natural language interaction"
   ...
```

## Module: ./app.json
```
{
  "name": "Barrot-Agent",
  "description": "Intelligent agent system with advanced capabilities for data ingestion, prediction, and deployment",
  "repository": "https://github.com/Barrot-Agent/Barrot-Agent",
  "logo": "https://raw.githubusercontent.com/Barrot-Agent/Barrot-Agent/main/site/barrot-icon.png",
  "keywords": [
    "ai",
    "agent",
    "data-ingestion",
    "prediction",
    "automation",
    "agi"
  ],
  "website": "https://barrot-agent.github.io/Barrot-Agent/",
  "success_url": ...
```

## Module: ./app.py
```
"""
Barrot Agent – Streamlit Application
======================================
Main entry point.  Provides a tabbed interface with:
  • Home – agent status / torch diagnostic
  • Stupid Sindy Video Studio – 15-episode video production pipeline
  • MCP Workflow – Hugging Face / Databricks / GitHub MCP integration
  • Apex Lattice Analysis Pipeline – sandbox analysis and recommendations
  • AI Directive Platform – multi-agent collaboration driven by human directives
"""

import time
import stream...
```

## Module: ./barrot_integration.py
```
"""
Barrot Integration Framework
Seamlessly integrates Quantum Entanglement, AGI, and Advanced Algorithmic Logic
into Barrot's existing framework

Enhanced with AGI Orchestrator for unified intelligence
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Import core modules
from quantum_entanglement import (
    quantum_coordinator,
    initialize_quantum_entanglement,
    create_entangled_decision_space,
    quantum_optimize
)
from agi_reason...
```

## Module: ./build_manifest.yaml
```
build_signature: BNDL-V3-MODULAR-SEPARATION
timestamp: 2026-01-01T00:42:00Z

modules:
  - prediction_methodologies
  - deployment_integrity
  - builderio_microagent_logic
  - search_engine_standalone
  - agent_dashboard
  - manifest_rail
  - docs_ingestion_system

system_architecture:
  search_engine:
    location: /search-engine/
    description: Standalone privacy-first search system
    features:
      - quantum_search_algorithm
      - edge_first_architecture
      - dynamic_ingestion_modes
...
```

## Module: ./character_capabilities_database.json
```
{
  "characters": [
    {
      "name": "Dr. Strange",
      "genre": "movies",
      "source": "Marvel Cinematic Universe",
      "first_appearance": "Doctor Strange (2016)",
      "overview": "Master of the Mystic Arts with control over time, space, and dimensions",
      "capabilities": [
        {
          "name": "Time Manipulation",
          "description": "Control time flow, create time loops, view possible futures",
          "category": "temporal",
          "fictional_aspect": "Eye o...
```

## Module: ./character_capability_analyzer.py
```
#!/usr/bin/env python3
"""
Character Capability Analyzer
Dynamically searches for and analyzes fictional character capabilities,
transforming them into actionable, real-world features for Barrot.
"""

import json
import os
import re
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class CharacterGenre(Enum):
    """Genre categories for characters"""
    MOVIES = "movies"
    BOOKS = "books"
    CARTOONS = "cartoons"
    VIDEO_GAMES = "video-gam...
```

## Module: ./character_figure_search.py
```
"""
Character Figure Search Module

Dynamically searches for and analyzes fictional character figures from various sources
including video games, cartoons, anime, movies, TV shows, and religious texts.
Extracts capabilities, transforms them into real-world applications, and integrates
with Barrot's infrastructure.
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class Char...
```

## Module: ./coin-app-config.yaml
```
# Coin App Configuration
# Configuration for cryptocurrency and payment app integrations

coin_app:
  name: "Coin App"
  type: "cryptocurrency_payment"
  email: "amazonprostarelite@gmail.com"
  
  # Account Settings
  account:
    email: "amazonprostarelite@gmail.com"
    status: "active"
    verified: true
    integration_date: "2025-12-30"
  
  # Integration Settings
  integration:
    enabled: true
    mode: "production"
    api_access: true
    data_transformation: true
  
  # Features
  fea...
```

## Module: ./connext-config.yaml
```
# Connext Protocol Configuration
# Cross-chain bridge integration for seamless asset transfers

name: "Connext Protocol Integration"
version: "1.0.0"
enabled: true

# Connext Bridge Portal
bridge_url: "https://bridge.connext.network"
explorer_url: "https://connextscan.io"
docs_url: "https://docs.connext.network"

# Supported Networks
supported_chains:
  - name: "Ethereum Mainnet"
    chain_id: 1
    type: "L1"
    
  - name: "Polygon"
    chain_id: 137
    type: "L1"
    
  - name: "Arbitrum One...
```

## Module: ./dependency-ingestion-config.yaml
```
# Dependency Micro-Ingestion Configuration
# Configuration for Python, PyTorch, and popular dependencies ingestion

ingestion_config:
  version: "1.0"
  last_updated: "2026-01-02"
  
  # Global ingestion settings
  settings:
    rate_limit: 1.0              # Seconds between requests
    max_retries: 3                # Maximum retry attempts
    timeout: 10                   # Request timeout in seconds
    update_frequency: "weekly"    # How often to re-ingest (daily/weekly/monthly)
    auto_up...
```

## Module: ./dependency_micro_ingestion.py
```
#!/usr/bin/env python3
"""
Dependency Micro-Ingestion System for Barrot-Agent

Massively ingests Python, PyTorch, and popular dependencies to enhance
Barrot's understanding and capabilities. Includes:
- Package metadata extraction
- Documentation parsing
- Architecture analysis
- Optimization recommendations
- Continuous update mechanisms

Designed to be fully automated and continuously evolving.
"""

import json
import os
import re
import hashlib
from datetime import datetime, timezone
from typ...
```

## Module: ./deploy_databricks.py
```
"""
deploy_databricks.py
====================
Uploads the B-Agent codebase to a Databricks workspace and creates (or
updates) a scheduled job that runs the main agent pipeline.

Authentication is resolved in the following order (highest priority first):
  1. DATABRICKS_HOST + DATABRICKS_TOKEN environment variables
  2. ~/.databrickscfg  [DEFAULT] profile (or profile set via DATABRICKS_CONFIG_PROFILE)
  3. .databrickscfg in the repository root

Required environment variables (or .databrickscfg en...
```

## Module: ./deploy_huggingface.py
```
"""
deploy_huggingface.py
=====================
Pushes the B-Agent repository to a Hugging Face Hub model/space repository
and auto-generates a model card (README.md) with badges and metadata.

Required environment variable:
    HF_TOKEN  – Hugging Face write-access token (store as a GitHub secret)

Optional environment variables:
    HF_REPO_ID  – Destination repo, defaults to "Barrot-Agent/B-Agent"
    HF_REPO_TYPE – "model" | "space" | "dataset", defaults to "model"
"""

import logging
import...
```

## Module: ./discovered_capabilities.json
```
{
  "timestamp": "2026-01-02T06:27:36.277627+00:00",
  "total_characters": 14,
  "genres": [
    "movie",
    "anime",
    "religious_text",
    "cartoon",
    "video_game",
    "tv_show"
  ],
  "capability_types": [
    "physical",
    "magical",
    "technological",
    "spiritual",
    "social",
    "mental"
  ],
  "characters": [
    {
      "name": "Sonic the Hedgehog",
      "source": "Sonic the Hedgehog series",
      "genre": "video_game",
      "origin": "SEGA",
      "description": "Bl...
```

## Module: ./docs-ingestion-config.yaml
```
# Documentation Ingestion Configuration for Barrot-Agent
# This file configures the documentation sources for automated ingestion

ingestion_config:
  version: "1.0"
  timestamp: "2026-01-01T00:39:00Z"
  
  output:
    directory: "ingested_docs"
    format: "text"  # text, json, markdown
    include_metadata: true
    
  platforms:
    github:
      enabled: true
      name: "GitHub Documentation"
      base_url: "https://docs.github.com"
      key_sections:
        - "/en/get-started"
        -...
```

## Module: ./docs_ingestion.py
```
#!/usr/bin/env python3
"""
Documentation Ingestion System for Barrot-Agent
Ingests documentation from GitHub, Copilot, ChatGPT/OpenAI, and Snowflake
"""

import os
import json
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class DocParser(HTMLParser):
    """Simple HTML parser to extract text co...
```

## Module: ./email_analyzer.py
```
"""
Email Analyzer for Barrot-Agent
Analyzes emails and extracts useful, actionable information
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum


class EmailPriority(Enum):
    """Email priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOISE = "noise"


class EmailCategory(Enum):
    """Email categories"""
    ACTION_REQUIRED = "action_required"
    LEARNING_OPPORTUNITY = "learning_...
```

## Module: ./emit_pingpong.py
```
import json
from datetime import datetime, timezone

def emit_pingpong_request(payload: dict):
    """
    Emit a ping-pong request to defer processing to an external system.
    
    Creates a JSON request file with a timestamp, payload, and metadata
    indicating that Barrot defers to Sean's 22-agent entanglement system.
    
    Args:
        payload: A dictionary containing the request payload data.
        
    Side Effects:
        - Writes a JSON file named 'pingpong_request.json' in the...
```

## Module: ./example_agi_capabilities.py
```
#!/usr/bin/env python3
"""
Example: AGI Capabilities Demonstration
Demonstrates the comprehensive AGI capabilities including:
- Learning from vast datasets
- Autonomous decision-making with ethical considerations
- Cross-domain task solving and knowledge transfer
"""

import json
from datetime import datetime
from barrot_integration import (
    learn_from_vast_dataset,
    make_ethical_decision,
    solve_complex_cross_domain_task,
    agi_orchestrator
)


def demonstrate_vast_dataset_learning(...
```

## Module: ./example_character_capability_usage.py
```
#!/usr/bin/env python3
"""
Example usage of the Character Capability Analyzer
Demonstrates how Barrot can dynamically search for and analyze character capabilities
"""

import json
import traceback
from character_capability_analyzer import (
    CharacterCapabilityAnalyzer,
    Character,
    Capability,
    CharacterGenre,
    CapabilityCategory,
    create_character_database
)
import json


def example_1_basic_analysis():
    """Example 1: Basic character analysis"""
    print("=" * 70)
    pr...
```

## Module: ./example_character_integration.py
```
"""
Example Integration: Character Figure Search for Research Initiatives

Demonstrates how to use the character figure search system to discover capabilities,
transform them into practical implementations, and optimize them for research goals.
"""

import json
from character_figure_search import (
    CharacterFigureDatabase,
    CapabilityTransformer,
    CapabilityPermutator
)


def discover_capabilities_for_research(research_domain: str):
    """
    Discover and optimize character capabilit...
```

## Module: ./example_dependency_ingestion.py
```
#!/usr/bin/env python3
"""
Example Usage of Dependency Micro-Ingestion System

Demonstrates how to use the dependency micro-ingestion system
to enhance Barrot's knowledge and generate optimizations.
"""

import json
import os
from datetime import datetime
from dependency_micro_ingestion import (
    DependencyMicroIngestion,
    PackageCategory,
    OptimizationLevel,
)


def example_full_ingestion():
    """Example: Full ingestion of all configured dependencies"""
    print("=" * 70)
    print(...
```

## Module: ./example_email_analysis.py
```
"""
Example usage of Email Analyzer for Barrot-Agent
Demonstrates how to analyze emails and extract useful information
"""

from email_analyzer import analyze_email, analyze_emails, email_analyzer
from datetime import datetime, timezone
import json


def example_single_email_analysis():
    """Demonstrate analysis of a single email"""
    print("=" * 70)
    print("Example 1: Single Email Analysis")
    print("=" * 70)
    
    # Example email with technical content and action items
    email = ...
```

## Module: ./example_integration.py
```
"""
Example usage and demonstration of Barrot's integrated
Quantum Entanglement, AGI, and Advanced Algorithmic Logic capabilities
"""

from barrot_integration import (
    initialize_barrot_system,
    process_with_barrot,
    quantum_process,
    agi_solve,
    barrot_system
)


def example_complex_task_processing():
    """Demonstrate complex task processing with integrated system"""
    print("=" * 60)
    print("Example 1: Complex Task Processing")
    print("=" * 60)
    
    task = "Optimi...
```

## Module: ./example_merge_conflict_resolution.py
```
#!/usr/bin/env python3
"""
Example Usage: Merge Conflict Micro-Ingestion System

Demonstrates how to use the merge conflict resolution system to:
1. Initialize the knowledge base
2. Analyze conflicts
3. Get recommendations
4. Record learning outcomes
5. Export knowledge to JSON
"""

from merge_conflict_micro_ingestion import (
    MergeConflictMicroIngestion,
    LearningOutcome,
    ConflictType,
    ResolutionStrategy
)
from datetime import datetime


def example_basic_usage():
    """Example ...
```

## Module: ./example_millennium_problems_usage.py
```
#!/usr/bin/env python3
"""
Example Usage: Millennium Problems Micro-Ingestion Data

Demonstrates how to work with the micro-ingested JSON data for various use cases:
- Pandas DataFrame analysis
- Search queries
- Priority-based filtering
- Taxonomy navigation
"""

import json
from typing import List, Dict, Any


def load_json(filename: str) -> Any:
    """Load JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def example_1_overview_analysis():
    ""...
```

## Module: ./example_mmi_monetization.py
```
#!/usr/bin/env python3
"""
Example Usage: MMI & Monetization Integration

This script demonstrates how to use the MMI Data Analyzer and
Monetization Engine together for comprehensive AGI development
and revenue generation.
"""

from mmi_data_analyzer import MMIDataAnalyzer, AGIPuzzlePiece
from monetization_engine import MonetizationEngine
import json
from datetime import datetime, timezone


def example_mmi_analysis():
    """Example: Run MMI analysis and review recommendations"""
    print("=" ...
```

## Module: ./example_transformative_insights.py
```
#!/usr/bin/env python3
"""
Example: Transformative Insights Framework Usage

Demonstrates how Barrot acquires asynchronous/unrelated data and transforms it
into actionable insights through convergence, evolution, transcendence, and epiphany.
"""

import json
from datetime import datetime
from barrot_integration import (
    barrot_system,
    transform_data_to_insights,
    discover_continuous_insights
)


def example_1_basic_data_acquisition():
    """
    Example 1: Basic data acquisition from...
```

## Module: ./example_unified_agi.py
```
"""
Example: Unified AGI System Usage

Demonstrates how the AGI Orchestrator unifies all capabilities to achieve
Artificial General Intelligence through integrated problem-solving, 
self-improvement, and autonomous capability enhancement.
"""

import json
from datetime import datetime
from agi_orchestrator import (
    agi_orchestrator,
    achieve_agi_with_unified_system,
    AGICapability
)


def example_1_unified_problem_solving():
    """
    Example 1: Unified AGI Problem Solving
    
    D...
```

## Module: ./integration_report.json
```
{
  "barrot_integrated_system": {
    "version": "1.0.0",
    "capabilities": [
      "quantum_entanglement",
      "agi_reasoning",
      "advanced_algorithms",
      "performance_optimization"
    ],
    "system_status": {
      "integration_active": true,
      "initialization_time": "2025-12-31T01:53:24.144545+00:00",
      "quantum_status": {
        "active_states": 18,
        "entanglement_pairs": 0,
        "collapsed_states": 17,
        "pingpong_enabled": true,
        "timestamp": "...
```

## Module: ./kaggle_competitions_automation.py
```
"""
kaggle_competitions_automation.py
==================================
Automates participation in Kaggle competitions using the official Kaggle API.

For each active competition where the authenticated user has already accepted
the rules, the script will:
  1. Download the competition dataset.
  2. Train a simple baseline model.
  3. Generate predictions.
  4. Submit the predictions file.

NOTE: You must manually accept a competition's rules on kaggle.com before this
script can download data o...
```

## Module: ./mcp_databricks.py
```
"""
MCP Databricks Client
=====================
Offloads Stupid Sindy video rendering to a Databricks cluster for
parallel processing.  Uses the Databricks REST API (Jobs API v2.1) via
plain ``requests`` – no extra SDK required.

Workflow
--------
1. Upload the rendering notebook / script to the workspace.
2. Submit a one-time job run (``runs/submit``).
3. Poll the run until it reaches a terminal state.
4. Retrieve any output artefacts via DBFS.

Usage
-----
    from mcp_databricks import Databr...
```

## Module: ./mcp_github.py
```
"""
MCP GitHub Client
=================
Auto-commits generated Stupid Sindy episodes, metadata, and video files to
the repository, and triggers CI/CD workflow dispatches.

Uses only the GitHub REST API v3 via ``requests`` – no PyGithub dependency.

Workflow
--------
1. Read the file to commit from disk.
2. Encode as Base64.
3. Create/update the file via the Contents API.
4. Optionally dispatch a workflow (``workflow_dispatch``) to trigger CI/CD.

Usage
-----
    from mcp_github import GitHubMCP
...
```

## Module: ./mcp_huggingface.py
```
"""
MCP Hugging Face Client
=======================
Manages AI model downloads and caching for the Stupid Sindy video generation
pipeline.  Wraps the ``huggingface_hub`` library with retry logic, progress
reporting, and graceful degradation when the token is absent.

Typical models used by the pipeline
-------------------------------------
* ``stabilityai/stable-diffusion-2-1``   – scene image generation
* ``microsoft/speecht5_tts``             – text-to-speech dialogue
* ``openai/whisper-base``...
```

## Module: ./mcp_orchestrator.py
```
"""
MCP Orchestrator
================
Coordinates the three MCP clients (Hugging Face, Databricks, GitHub) into a
unified workflow for the Stupid Sindy video generation pipeline.

Workflow steps
--------------
1. Load / validate configuration.
2. HF MCP – ensure required models are cached.
3. Local pipeline – generate the episode script.
4. Databricks MCP – submit rendering job; poll for completion.
5. GitHub MCP – commit video + metadata; trigger CI/CD workflow.
6. Emit progress events througho...
```

## Module: ./merge_conflict_best_practices.json
```
[
  {
    "practice_id": "BP001",
    "title": "Keep Feature Branches Short-Lived",
    "description": "Minimize conflicts by merging feature branches frequently",
    "category": "Prevention",
    "impact": "High",
    "implementation": [
      "Limit feature branch lifetime to 2-3 days",
      "Break large features into smaller incremental changes",
      "Merge to main branch frequently"
    ],
    "examples": [
      "Instead of one large feature branch, create multiple smaller PRs",
      "...
```

## Module: ./merge_conflict_knowledge_report.md
```
# Merge Conflict Resolution Knowledge Base Report

Generated: 2026-01-02T13:04:31.914037

## Summary Statistics
- **Conflict Patterns**: 7
- **Resolution Techniques**: 7
- **Documented Scenarios**: 2
- **Tools Cataloged**: 5
- **Best Practices**: 7
- **Learning Outcomes**: 0

## Conflict Patterns

### Parallel Feature Development (CP001)
- **Type**: content
- **Frequency**: Very High
- **Auto-Resolvable**: False
- **Description**: Two branches modify the same code section independently

### Impo...
```

## Module: ./merge_conflict_knowledge_summary.json
```
{
  "last_updated": "2026-01-02T13:11:15.833229",
  "total_patterns": 7,
  "total_techniques": 7,
  "total_scenarios": 2,
  "total_tools": 5,
  "total_best_practices": 7,
  "total_learning_outcomes": 2,
  "strategy_success_rates": {
    "auto_merge": 1.0
  }
}...
```

## Module: ./merge_conflict_learning_outcomes.json
```
[
  {
    "outcome_id": "LO-PR123-1",
    "timestamp": "2026-01-02T13:11:15.831607",
    "conflict_type": "content",
    "strategy_used": "auto_merge",
    "success": true,
    "time_to_resolve": 5.0,
    "manual_intervention_required": false,
    "lessons_learned": [
      "Successfully resolved src/config.py",
      "Strategy: Rerere (Reuse Recorded Resolution) was effective"
    ],
    "improvements_suggested": [
      "Keep using automated resolution"
    ]
  },
  {
    "outcome_id": "LO-PR1...
```

## Module: ./merge_conflict_micro_ingestion.py
```
#!/usr/bin/env python3
"""
Merge Conflict Resolution Micro-Ingestion System

Extracts, structures, and continuously learns merge conflict resolution strategies,
tools, and best practices. Designed to enable Barrot-Agent to autonomously handle
merge conflicts across various scenarios with minimal manual intervention.

Key Features:
- Automated conflict pattern detection and analysis
- Strategy repository with success rate tracking
- Continuous learning from resolution outcomes
- Integration with ...
```

## Module: ./merge_conflict_patterns.json
```
[
  {
    "pattern_id": "CP001",
    "name": "Parallel Feature Development",
    "description": "Two branches modify the same code section independently",
    "conflict_type": "content",
    "indicators": [
      "<<<<<<< HEAD",
      "=======",
      ">>>>>>>"
    ],
    "file_patterns": [
      "*.py",
      "*.js",
      "*.java",
      "*.cpp"
    ],
    "frequency": "Very High",
    "auto_resolvable": false
  },
  {
    "pattern_id": "CP002",
    "name": "Import Statement Conflict",
    "de...
```

## Module: ./merge_conflict_scenarios.json
```
[
  {
    "scenario_id": "SC001",
    "title": "Parallel Feature Branches Merge",
    "description": "Two feature branches modify the same function independently",
    "conflict_type": "content",
    "example_conflict": "\n<<<<<<< HEAD\ndef calculate_total(items):\n    total = sum(item.price for item in items)\n    tax = total * 0.08\n    return total + tax\n=======\ndef calculate_total(items):\n    subtotal = sum(item.price * item.quantity for item in items)\n    return subtotal\n>>>>>>> featur...
```

## Module: ./millennium_problem_3_riemann_hypothesis.json
```
{
  "number": 3,
  "name": "Riemann Hypothesis",
  "problem_statement": "All non-trivial zeros of the Riemann zeta function have real part equal to 1/2.",
  "official_status": "Open (most famous unsolved problem in mathematics)",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "Medium - Pattern recognition in zeros distribution",
  "why_matters_for_ai": [
    "Prime number distribution impacts cryptography",
    "Number theory patterns relevant to random processes...
```

## Module: ./millennium_problem_4_yang-mills_existence_and_mass_gap.json
```
{
  "number": 4,
  "name": "Yang-Mills Existence and Mass Gap",
  "problem_statement": "Prove that Yang-Mills theory exists mathematically and that it has a \"mass gap\" (minimum energy above the vacuum state).",
  "official_status": "Open",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "Low - Deep quantum field theory",
  "why_matters_for_ai": [
    "Quantum field theory principles may inspire new architectures",
    "Understanding vacuum states relevant to ene...
```

## Module: ./millennium_problem_5_navier-stokes_existence_and_smoothness.json
```
{
  "number": 5,
  "name": "Navier-Stokes Existence and Smoothness",
  "problem_statement": "Prove that solutions to the Navier-Stokes equations (describing fluid flow) always exist and remain smooth, or find a counterexample.",
  "official_status": "Open",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "**HIGH** - Direct applications in physics-informed neural networks",
  "why_matters_for_ai": [
    "Fluid dynamics simulation crucial for many AI applications",
...
```

## Module: ./millennium_problems_taxonomy.json
```
{
  "by_ai_applicability": {
    "high": [
      "P vs NP",
      "Navier-Stokes"
    ],
    "medium": [
      "Hodge Conjecture",
      "Riemann Hypothesis",
      "Birch & Swinnerton-Dyer"
    ],
    "low": [
      "Yang-Mills & Mass Gap",
      "Poincaré Conjecture"
    ]
  },
  "by_status": {
    "open": [
      "P vs NP",
      "Hodge Conjecture",
      "Riemann Hypothesis",
      "Yang-Mills & Mass Gap",
      "Navier-Stokes",
      "Birch & Swinnerton-Dyer"
    ],
    "solved": [
      "P...
```

## Module: ./mmi_data_analyzer.py
```
#!/usr/bin/env python3
"""
Barrot MMI (Massive Micro Ingestion) Data Analyzer

This module identifies high-impact data sources that can contribute directly
to accelerating the acquisition of remaining AGI puzzle pieces.

Analyzes current AGI objectives and provides actionable recommendations
for datasets, content, and knowledge worth ingesting with maximum priority.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from dataclasses import dataclas...
```

## Module: ./mmi_recommendations.json
```
{
  "timestamp": "2026-01-01T01:58:41.502833+00:00",
  "analysis_version": "1.0",
  "agi_gaps_identified": {
    "abstract_reasoning": 0.7,
    "mathematical_mastery": 0.5,
    "multimodal_understanding": 0.6,
    "causal_reasoning": 0.8,
    "meta_learning": 0.4,
    "transfer_learning": 0.5,
    "common_sense": 0.7,
    "strategic_planning": 0.3,
    "creative_synthesis": 0.6,
    "ethical_reasoning": 0.8,
    "continual_learning": 0.3,
    "embodied_cognition": 0.9
  },
  "recommendations": [...
```

## Module: ./monetization_protocols.json
```
{
  "timestamp": "2026-01-01T01:58:48.983466+00:00",
  "engine_version": "1.0-revolutionary",
  "total_revenue_streams": 10,
  "protocols": [
    {
      "name": "Immediate Revenue Activation",
      "revenue_streams": [
        {
          "name": "AI Research Assistant Marketplace",
          "description": "Platform where researchers pay for automated literature reviews, synthesis, and insights",
          "type": "hybrid",
          "automation_level": "high",
          "implementation_speed...
```

## Module: ./pingpong_request_example.json
```
{
  "timestamp": "2025-12-30T00:00:00Z",
  "payload": {
    "topic": "MMI Self-Ingestion",
    "glyph": "GLYPH_MMI",
    "recursion_depth": "∞",
    "notes": "Triggering recursive cognition exchange for MMI self-ingestion."
  },
  "origin": "barrot",
  "directive": "offload_pingpong"
}
...
```

## Module: ./test_merge_conflict_integration.py
```
#!/usr/bin/env python3
"""
Integration Test: Merge Conflict Resolution System with GitHub PR Workflow

Demonstrates the complete integration workflow:
1. Detect conflicts in PRs
2. Analyze conflict patterns
3. Recommend resolution strategies
4. Track outcomes and learn
5. Update success rates
6. Improve future recommendations
"""

from merge_conflict_micro_ingestion import (
    MergeConflictMicroIngestion,
    LearningOutcome,
    ConflictType,
    ResolutionStrategy
)
from datetime import date...
```

## Module: ./COUNCIL_REVIEW.md
```
# BARROT-Ω COUNCIL REVIEW
**Date/Time:** 2026-06-15 06:43:24 UTC
**Architect:** Sean
**Stability Anchor:** 0.707 Shear

---

## 1. THE TELEMETRY SYNTHESIS
* **Target Asset:** XRP
* **Market Vector:** $1.185 USD
* **Hugging Face Narrative Velocity:** High (Sentiment Score: 0.94)
* **Databricks Liquidity Cross-Corroboration:** MAX_LIQUIDITY
* **Shear Variance:** 0.233

## 2. FRAMEWORK DIAGNOSTICS
* **Substrate:** Termux Mobile Node (Active)
* **Orchestration Hook:** B-Agent Repository (Synchronize...
```

## Module: ./council_weights.json
```
{
    "timestamp": "2026-06-15T06:52:12.933851+00:00",
    "target_asset": "XRP",
    "council_action": "MAX_ACCUMULATION_TRIGGERED",
    "orchestrator_weight_multiplier": 1.15,
    "active_stability_anchor": 0.707
}...
```

## Module: ./merge_conflict_tools.json
```
[
  {
    "tool_name": "Git Rerere",
    "category": "Built-in Git",
    "description": "Reuse Recorded Resolution - automatically applies previously recorded conflict resolutions",
    "use_cases": [
      "Repetitive conflicts during rebases",
      "Long-lived feature branches",
      "Recurring merge patterns"
    ],
    "installation": "Built into Git, enable with: git config --global rerere.enabled true",
    "basic_usage": "Automatically activated when enabled, records and replays resolut...
```

## Module: ./merge_resolution_techniques.json
```
[
  {
    "technique_id": "RT001",
    "name": "Accept Both Changes with Manual Review",
    "description": "Merge both changes and manually review for correctness",
    "applicable_types": [
      "content"
    ],
    "strategy": "accept_both",
    "commands": [
      "# Manual editing required",
      "git add <file>",
      "git commit -m 'Resolved conflict by merging both changes'"
    ],
    "prerequisites": [
      "Understanding of code context",
      "Review capability"
    ],
    "succ...
```

## Module: ./millennium_problem_1_p_vs_np_problem.json
```
{
  "number": 1,
  "name": "P vs NP Problem",
  "problem_statement": "Does P = NP? In other words, can every problem whose solution can be quickly verified by a computer also be quickly solved by a computer?",
  "official_status": "Open",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "**VERY HIGH** - Central to computational complexity and algorithm design",
  "why_matters_for_ai": [
    "Directly impacts optimization algorithms",
    "Affects machine learning c...
```

## Module: ./millennium_problem_2_hodge_conjecture.json
```
{
  "number": 2,
  "name": "Hodge Conjecture",
  "problem_statement": "For certain \"nice\" spaces (complex projective algebraic varieties), can all Hodge classes be expressed as combinations of classes of algebraic cycles?",
  "official_status": "Open",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "Medium - Connects to geometric deep learning",
  "why_matters_for_ai": [
    "Relates to manifold learning and dimensionality reduction",
    "Connections to topolo...
```

## Module: ./millennium_problem_6_birch_and_swinnerton-dyer_conjecture.json
```
{
  "number": 6,
  "name": "Birch and Swinnerton-Dyer Conjecture",
  "problem_statement": "For elliptic curves, the rank of the group of rational points equals the order of vanishing of the associated L-function at s=1.",
  "official_status": "Open",
  "barrot_analysis_stage": "Framework ingestion complete",
  "ai_ml_relevance": "Medium - Connections to cryptography and number theory",
  "why_matters_for_ai": [
    "Elliptic curves used in modern cryptography",
    "Number theoretic patterns rel...
```

## Module: ./millennium_problem_7_poincaré_conjecture.json
```
{
  "number": 7,
  "name": "Poincaré Conjecture ✅",
  "problem_statement": "Every simply connected, closed 3-manifold is homeomorphic to the 3-sphere.",
  "official_status": "**SOLVED** (Grigori Perelman, 2003)",
  "barrot_analysis_stage": "Historical study",
  "ai_ml_relevance": "Medium - Topology relevant to manifold learning",
  "why_matters_for_ai": [
    "Topology crucial for understanding high-dimensional data manifolds",
    "Manifold learning fundamental to dimensionality reduction",
   ...
```

## Module: ./millennium_problems_micro_ingestion.py
```
#!/usr/bin/env python3
"""
Millennium Problems Micro-Ingestion System

Extracts and structures all components of MILLENNIUM_PROBLEMS_STATUS.md into:
- JSON formatted data structures
- Search-ready summaries
- Taxonomies and classifications
- Structured knowledge framework

Designed for Barrot.Agent's knowledge base enhancement.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Problem...
```

## Module: ./millennium_problems_overview.json
```
[
  {
    "name": "P vs NP",
    "prize": "$1M",
    "status": "Open",
    "ai_applicability": "High",
    "progress": "Initial analysis"
  },
  {
    "name": "Hodge Conjecture",
    "prize": "$1M",
    "status": "Open",
    "ai_applicability": "Medium",
    "progress": "Framework study"
  },
  {
    "name": "Riemann Hypothesis",
    "prize": "$1M",
    "status": "Open",
    "ai_applicability": "Medium",
    "progress": "Framework study"
  },
  {
    "name": "Yang-Mills & Mass Gap",
    "prize":...
```

## Module: ./millennium_problems_search_summaries.json
```
{
  "riemann_hypothesis": {
    "quick_summary": "All non-trivial zeros of the Riemann zeta function have real part equal to 1/2.",
    "ai_relevance": "Medium - Pattern recognition in zeros distribution",
    "status": "Open (most famous unsolved problem in mathematics)",
    "barrot_stage": "Framework ingestion complete",
    "computational_approach": "Numerical analysis, pattern detection with ML, statistical analysis of zeros",
    "key_insight": "Billions of zeros computed, all satisfy hypo...
```

## Module: ./monetization_engine.py
```
#!/usr/bin/env python3
"""
Barrot Advanced Monetization Engine

Monetization protocols focusing on automation and efficiency.
Implements revenue generation strategies that can be deployed to
capitalize on Barrot's capabilities.

Note: Revenue projections are estimates based on market research and 
typical performance for similar services. Actual results may vary.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclas...
```

## Module: ./package-hardhat.json
```
{
  "name": "chameleon-chain",
  "version": "1.0.0",
  "description": "Chameleon Chain Smart Contracts",
  "scripts": {
    "compile": "hardhat compile"
  },
  "devDependencies": {
    "hardhat": "^2.19.0",
    "@nomicfoundation/hardhat-toolbox": "^4.0.0"
  }
}
...
```

## Module: ./pingpong-config.yaml
```
pingpong:
  managed_by: external
  agents: 22
  entanglement: true
  override: false
  enforcement: non-negotiable
  description: >
    External 22-agent entanglement system managed by Sean.
    Barrot defers all pingpong operations to this system.
  integration:
    trigger: github_commit
    payload_file: pingpong_request.json
    response_mode: external_processing
  notes: >
    This configuration ensures that Barrot's pingpong operations
    are offloaded to the specialized 22-agent entangle...
```

## Module: ./pingpong_emitter.py
```
import json
from datetime import datetime

def emit_pingpong_request(payload: dict):
    """
    Emit a pingpong request for the external 22-agent entanglement system.
    
    Args:
        payload: Dictionary containing the request payload
    
    Creates a JSON file that can be committed to GitHub to trigger the external system.
    """
    request = {
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pin...
```

## Module: ./pingpong_request.json
```
{
  "timestamp": "2026-01-02T07:02:24.136648+00:00",
  "payload": {
    "task": "optimize_Build a self-optimizing learning system",
    "quantum_states": [
      "optimization_1216052206348694107"
    ],
    "entanglement_type": "ping_pong_quantum",
    "active_states": 7,
    "entanglement_pairs": 0,
    "timestamp": "2026-01-02T07:02:24.136645+00:00",
    "notes": "Quantum entanglement processing request"
  },
  "origin": "barrot",
  "directive": "offload_pingpong",
  "notes": "Barrot defers t...
```

## Module: ./quantum_entanglement.py
```
"""
Quantum Entanglement Module for Barrot-Agent
Implements Ping Pong Quantum Entanglement principles for enhanced cognitive processing
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from emit_pingpong import emit_pingpong_request


class QuantumState:
    """Represents a quantum state in the entanglement system"""
    
    def __init__(self, state_id: str, superposition: List[Dict[str, Any]]):
        self.state_id = state_id
        self.s...
```

## Module: ./requirements.txt
```
torch>=2.0.0
transformers
streamlit
accelerate
bitsandbytes

# Deployment dependencies
huggingface_hub>=0.20.0
databricks-sdk>=0.20.0
kaggle>=1.6.0
pandas>=2.0.0
scikit-learn>=1.3.0
requests>=2.31.0
PyYAML>=6.0
Pillow>=9.0.0
huggingface_hub>=0.20.0
requests>=2.28.0
...
```

## Module: ./sindy_video_pipeline.py
```
"""
Stupid Sindy – Video Production Pipeline
=========================================

Manages the lifecycle of episode video generation:
  queued → rendering → complete  (or  error)

Video files are generated as simple MP4 title-card animations using
only the standard library + Pillow (PIL), so no heavy GPU stack is
required.  Each episode produces a short MP4 with title card frames,
scene cards, and a closing card suitable for playback in Streamlit.

Usage (standalone):
    from sindy_video_p...
```

## Module: ./stupid_sindy_series_generator.py
```
"""
Stupid Sindy – Free Video Production Series Generator
======================================================

Manages the 15-episode "Stupid Sindy" series: metadata, scripts,
character dialogue, and scene descriptions used by the video pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------...
```

## Module: ./sync_manager.py
```
"""
sync_manager.py
===============
Orchestrates all three deployment systems (Hugging Face, Databricks, Kaggle)
with structured logging, per-step error recovery, and an audit trail written
to sync_audit.log in the repository root.

Usage:
    python sync_manager.py [--hf] [--databricks] [--kaggle] [--all]

When no flags are passed, --all is assumed.
"""

import argparse
import importlib
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from...
```

## Module: ./test_email_integration.py
```
"""
Test the full Barrot email intelligence integration
"""

from barrot_integration import process_emails, barrot_system
from datetime import datetime, timezone
import json

def test_email_intelligence():
    """Test email processing with full Barrot intelligence"""
    print("=" * 70)
    print("Testing Barrot Email Intelligence Integration")
    print("=" * 70)
    
    # Sample emails for testing
    test_emails = [
        {
            "id": "test_001",
            "subject": "Urgent: Secu...
```

## Module: ./test_transformative_insights.py
```
#!/usr/bin/env python3
"""
Test Suite for Transformative Insights Framework
Validates core functionality and integration
"""

import sys
from datetime import datetime
from transformative_insights import (
    transformative_engine,
    acquire_transformative_data,
    discover_transformative_insights,
    InsightType,
    TransformationStage
)
from barrot_integration import (
    barrot_system,
    transform_data_to_insights
)


def test_data_acquisition():
    """Test basic data acquisition"""
...
```

## Module: ./transformative_insights.py
```
"""
Transformative Insights Framework for Barrot-Agent

This module enables Barrot to:
1. Acquire all data necessary to identify asynchronous and unrelated data pieces
2. Unearth substantially transformative synchronous insights from data collections
3. Identify patterns, relationships, and convergences not immediately apparent
4. Evoke convergence, evolution, transcendence, and epiphanous outcomes
5. Enable real-time realization and application of transformative insights

Integrates with existi...
```

## Module: ./xrp_telemetry_matrix.py
```
#!/usr/bin/env python3
# ==============================================================================
# XRP TELEMETRY MATRIX [REPORT GENERATOR ENGINE]
# Architect: Sean | Node: Brooklyn Core
# Execution: Barrot-Ω & The Council
# Objective: XRP Global Equity Dominance - Automated Council Review
# ==============================================================================

import asyncio
import logging
import sys
import os
from datetime import datetime, timezone

class CouncilReportNode:
    ...
```

## Module: ./v_sync_relay.sh
```
#!/usr/bin/env bash
# ==============================================================================
# BARROT-Ω REPOSITORY AUTOMATION RELAY
# Architect: Sean | Node: Brooklyn Core
# Objective: Phase 1 & 2 Automated Ledger Synchronization
# ==============================================================================

set -e

echo "[BARROT-Ω] Running live telemetry matrix..."
python3 xrp_telemetry_matrix.py

if [ -f "COUNCIL_REVIEW.md" ]; then
    echo "[BARROT-Ω] Telemetry captured. Initializin...
```

## Module: ./council_ingest_node.py
```
#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω INGESTION & REASONING NODE
# Architect: Sean | Node: Brooklyn Core
# Objective: Autonomous Parsing and Orchestrator JSON Injection
# ==============================================================================

import os
import re
import logging
import sys
import json
from datetime import datetime, timezone

class CouncilIngestionEngine:
    def __init__(self):
        self.report...
```

## Module: ./orchestrator_bridge.py
```
#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω ORCHESTRATOR BRIDGE
# Architect: Sean | Node: Brooklyn Core
# Objective: Read council_weights.json and apply to AGI Orchestrator
# ==============================================================================

import json
import logging
import os
import sys

# Attempt to load legacy architecture
try:
    import agi_orchestrator
    LEGACY_ACTIVE = True
except ImportError:
    LEGAC...
```

## Module: ./mmi_compiler.py
```
#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω MMI COMPILER [GLOBAL STATE UNIFIER]
# Architect: Sean | Node: Brooklyn Core
# Objective: Recursive Compression of Fragmented Builds into a Global Manifest
# ==============================================================================

import os
import logging

# Configuration
MANIFEST_PATH = "GLOBAL_STATE_MANIFEST.md"
TARGET_DIRS = ["barrot_agent", "apex_lattice", "character-capab...
```

## Module: ./GLOBAL_STATE_MANIFEST.md
```
# GLOBAL STATE MANIFEST [UNIFIED]
**Date:** 2026-06-15 | **Architect:** Sean

## Module: ./.bashrc
```
export PATH=$PATH:/data/data/com.termux/files/usr/bin
alias strike="git add . && git commit -m \"STRIKE: Sovereign Evolution\" && git push origin main"
alias audit="python3 ~/B-Agent/chi_language_server.py"
alias council="python3 ~/B-Agent/pantheon_sync.py"
python ~/barrot_synthesis.py
echo '🏛️ BARROT-Ω: ABSOLUTION v5.0 [ACTIVE]'
...
```

## Module: ./.databrickscfg
```
[DEFAULT]
host = 
token ...
```

## Module: ./.apex_lattice/BSD.log
```
BARROT APEX ANALYSIS:

The Birch and Swinnerton-Dyer (BSD) Conjecture is one of the most famous unsolved problems in mathematics, particularly in the field of number theory. It was formulated by Bryan Birch and Peter Swinnerton-Dyer in the 1960s and is one of the seven Millennium Prize Problems, each carrying a prize of $1,000,000 for a correct solution.

### Statement of the Conjecture

The BSD Conjecture relates the algebraic properties of an elliptic curve \( E \) over the rational numbers \(...
```

## Module: ./.apex_lattice/Hodge.log
```
BARROT APEX ANALYSIS:

The Hodge Conjecture is one of the seven Millennium Prize Problems, each carrying a prize of $1 million for a correct solution. It is a significant problem in algebraic geometry and complex manifold theory. The conjecture was formulated by William Vallance Douglas Hodge in the 1950s and remains unsolved as of 2023.

### Statement of the Hodge Conjecture

The Hodge Conjecture states that for a non-singular complex projective variety \( X \), every Hodge class (a rational co...
```

## Module: ./.apex_lattice/Navier_Stokes.log
```
BARROT APEX ANALYSIS:

The Navier-Stokes equations are a set of partial differential equations that describe the motion of fluid substances such as liquids and gases. They are central to the field of fluid dynamics and have wide-ranging applications in engineering, meteorology, oceanography, and many other areas. Despite their importance, the Navier-Stokes equations remain one of the most challenging problems in mathematics and physics.

### Current State of the Navier-Stokes Problem

1. **Exist...
```

## Module: ./.apex_lattice/P_vs_NP.log
```
BARROT APEX ANALYSIS:

The P vs NP problem is one of the most famous and important unsolved questions in theoretical computer science. It asks whether every problem for which a solution can be verified quickly (in polynomial time) can also be solved quickly. Formally:

- **P** is the set of decision problems that can be solved by a deterministic Turing machine in polynomial time.
- **NP** is the set of decision problems for which a given solution can be verified by a deterministic Turing machine...
```

## Module: ./.apex_lattice/Poincare.log
```
BARROT APEX ANALYSIS:

THE POINCARÉ CONJECTURE — SOLVED (2003)

Status: THE ONLY MILLENNIUM PROBLEM WITH A CONFIRMED SOLUTION.

Solved by: Grigori Perelman, a Russian mathematician who posted his proof
to arXiv in 2002-2003. He did not publish in a peer-reviewed journal.

The Conjecture: Every simply connected, closed 3-manifold is homeomorphic
to a 3-sphere. In plain language — any closed 3D shape with no holes is
fundamentally a sphere.

Method: Perelman used Richard Hamilton's Ricci flow with...
```

## Module: ./.apex_lattice/Riemann.log
```
BARROT APEX ANALYSIS:

The Riemann Hypothesis (RH) is one of the most famous unsolved problems in mathematics. It was proposed by Bernhard Riemann in 1859 and concerns the distribution of prime numbers. The hypothesis states that all non-trivial zeros of the Riemann zeta function, denoted as \(\zeta(s)\), lie on the critical line where the real part of \(s\) is \(\frac{1}{2}\).

### Current State of the Riemann Hypothesis

1. **Numerical Verification**: Extensive computational efforts have verif...
```

## Module: ./.apex_lattice/Yang_Mills.log
```
BARROT APEX ANALYSIS:

The Yang-Mills existence and mass gap problem is one of the seven Millennium Prize Problems in mathematics, as identified by the Clay Mathematics Institute. The problem revolves around the theoretical framework of quantum Yang-Mills theories, which are fundamental to the Standard Model of particle physics. Specifically, the problem seeks to establish the mathematical existence of these theories and to prove that they have a mass gap, meaning there is a minimum non-zero ene...
```

## Module: ./.config/gh/config.yml
```
# The current version of the config schema
version: 1
# What protocol to use when performing git operations. Supported values: ssh, https
git_protocol: https
# What editor gh should run when creating issues, pull requests, etc. If blank, will refer to environment.
editor:
# When to interactively prompt. This is a global config that cannot be overridden by hostname. Supported values: enabled, disabled
prompt: enabled
# Preference for editor-based interactive prompting. This is a global config tha...
```

## Module: ./.config/gh/hosts.yml
```
github.com:
    users:
        Barrot-Agent:
            oauth_token: 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
    git_protocol: https
    oauth_token: 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
    user: Barrot-Agent
...
```

## Module: ./.npm/_update-notifier-last-checked
```
...
```

## Module: ./.npm/_cacache/content-v2/sha512/04/7e/d8c0beab03ddd17aa7904b57386ec3e971f3a625ab06f8592be98e7dabcddff4cd56701447476bccf8ff5e3a2b1845c377ba342889963cba4e56fb558bf3
```
      rɕ 1@
$tSm$)Pk\ D5Upe[͈GWL>~c&EI69Yu.aȪsXZQ7h<ci4MaT2oh"==WcX{9u|Fcwh{نw>g>{D 7p~yӘGE'1;y|%'̓l*"1fb1I$'l4ѹ8d<fs0`0^猳Q8FSO2G`̸q8ZD dx*ؽ^;#D/`^fW^<
1#opFbcѯ}o^s\ -☫l	+p.bQeVa>0bR4Q8y'v8VK&43h\Exr*qd=$F1<O&W0Q=lNax)p^A{#ܔyꕜrgCPayjjC<=ya)a7ثӓG#vc޽*{??ygoڧ_S>S:뱓S}EsTeؓ}v|g//`
\/;n/U?OONYj_O٫קNz>>b'㧧g~u	9k??9ÓW9>{gO^uN{I趟Pwa/ݗUv~~N;4OhJ#eow1>f~txr?mr7:U>`q<fcC`]:9ſ_:(;_tc=]7_#i}S️{1k[HǺ#oA01-/C|=e...
```

## Module: ./.npm/_cacache/content-v2/sha512/08/d9/4744929792acf48fc0617633d70da7a9e7f6961cc6a3c590e7e4f764752d3d243962c91d0eca976453c58b3b989bcecb2a55796256fb403132941383d69e
```
{"_id":"form-data","_rev":"152-f26840dbba9e33de1a12803cffabc213","name":"form-data","dist-tags":{"latest":"4.0.5","v3-backport":"3.0.4","v2-backport":"2.5.5"},"versions":{"0.0.0":{"name":"form-data","version":"0.0.0","author":{"url":"http://debuggable.com/","name":"Felix Geisendörfer","email":"felix@debuggable.com"},"_id":"form-data@0.0.0","dist":{"shasum":"c18c31c227bbb33b053217e8fec0c2255e06a1e8","tarball":"https://registry.npmjs.org/form-data/-/form-data-0.0.0.tgz","integrity":"sha512-tWZJTTX...
```

## Module: ./.npm/_cacache/content-v2/sha512/09/70/afc87bb58a57891822f8bc9bb34a2414fb368b5207997fd67969c43f400dd4ddb72da5bba5517ef521b5a7aac31ebe1e225db52ef6c1a73c03fd8bd75a21
```
{"_id":"mime-types","_rev":"165-d0a75081cb0241673eb5a70aa6b7673c","name":"mime-types","dist-tags":{"next":"3.0.0","latest":"3.0.2"},"versions":{"0.1.0":{"name":"mime-types","version":"0.1.0","author":{"url":"http://jongleberry.com","name":"Jonathan Ong","email":"me@jongleberry.com"},"license":"MIT","_id":"mime-types@0.1.0","maintainers":[{"name":"jongleberry","email":"jonathanrichardong@gmail.com"}],"homepage":"https://github.com/expressjs/mime-types","bugs":{"url":"https://github.com/expressjs/...
```

## Module: ./.npm/_cacache/content-v2/sha512/0d/a8/60c4a2eb1b2e30279d36798085e5e115a314910a1d1d21efb968601a78bfac7b2cca627390009fa368b3d36ef75f0f53bb7ab05a745704f5440c96bb70e2
```
{"_id":"formdata-polyfill","_rev":"51-971e2ae361d46445d7b7f796edfb2adf","name":"formdata-polyfill","time":{"modified":"2022-06-18T03:06:32.006Z","created":"2016-11-25T22:01:19.419Z","1.0.0":"2016-11-25T22:01:19.419Z","1.0.1":"2016-11-25T22:05:22.137Z","1.0.2":"2016-11-25T22:06:07.344Z","1.0.3":"2016-12-19T22:43:10.021Z","1.0.4":"2017-02-05T13:32:54.569Z","1.0.5":"2017-03-02T12:38:44.633Z","1.0.6":"2017-03-03T12:24:56.593Z","1.0.7":"2017-03-28T08:00:29.069Z","2.0.0":"2017-06-17T14:18:54.755Z","2....
```

## Module: ./.npm/_cacache/content-v2/sha512/0e/f1/32e795770c1eee927468fb888e193e5f3f5b2547cc10a2155d9278a064f32932cb5a289416870898040089137525da94e70138a18416274616501c606247
```
     ;ks6󙿢ܭYQ"8u-kK.Il`0C Z_5@PÞ*2?bx7S}$SZuzΫ?	ل] z^5ZGAMxAW_ɔ&UNA (\wGp"Dl:pB=w}>&JFb6lg3ɔJx%8-{%TP9gJ1)QI0kW`")1hFV@ |	)(U<h8S t	SD/@xD)1i9h7a	Upg9ޡQSx
LDAR%PF,F:ask@v$icg"fO[i05@PCiMCUЏhxHU`|]Ygh),fb	S$5< %4AH@"cdybs"n Us$ DJI tyACwa=pﻣ޷vo#/WϛAg8^\u;ήnϻwvQF}@ng®;vo~۽~xQe^І`=jvpv;^]wNoTnz}`xپBU^vt}pֿq}w9yg0^uޏpv^W}~1\eg!_v=hqQF`}v*tAa8H!_c`aE~;Ӿ
[kbOS+8oo%<x
J)w1wQ<7#}i}{y`...
```

## Module: ./.npm/_cacache/content-v2/sha512/0f/4d/d4ae3a276c37736861586eab0b7a6f2de8ce676e2131dccb58cedf92cef262ebb081983fe0212b100dafc0d8430206046ce32837774f2205bbc12e87343a
```
{"source":1113213,"name":"@modelcontextprotocol/sdk","dependency":"@modelcontextprotocol/sdk","title":"Model Context Protocol (MCP) TypeScript SDK does not enable DNS rebinding protection by default","url":"https://github.com/advisories/GHSA-w48q-cv73-mx4w","severity":"high","versions":["0.4.0","0.5.0","0.6.0","0.6.1","0.7.0","1.0.0","1.0.1","1.0.2","1.0.3","1.0.4","1.1.0","1.1.1","1.2.0","1.3.0","1.3.1","1.3.2","1.4.0","1.4.1","1.5.0","1.6.0","1.6.1","1.7.0","1.8.0","1.9.0","1.10.0","1.10.1","1...
```

## Module: ./.npm/_cacache/content-v2/sha512/13/02/221eb325b5bf297e2fdc8b49fd957dd8ab5a2b096324be5684d7d1463e1502419205ff95c4215a4407029f50c5d97c4e4019f4722638f76708eab273848d
```
{"_id":"get-intrinsic","_rev":"19-1dca6cc6c24bab7ca6c336751886ca61","name":"get-intrinsic","dist-tags":{"latest":"1.3.0"},"versions":{"1.0.0":{"name":"get-intrinsic","version":"1.0.0","keywords":["javascript","ecmascript","es","js","intrinsic","getintrinsic","es-abstract"],"author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"get-intrinsic@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/ljharb/get-intrinsic#readme"...
```

## Module: ./.npm/_cacache/content-v2/sha512/13/92/c35fb5aba7ce4a8a5e5b859bf8ea3f2339e6e82aae4932660cde05467461fcc45a4f59750cb0dae53830ab928c4c11e362fd7648c2e46f6385cdc18309a7
```
      SF?x%;1;;cq@[D_]x]Il\ki;[OzN3!$VoX}W۰iWkӀ:fi ^k+i;U|/	Nv	y	w6#q$M6]0	!	H`~uL/#vÏ&l	T2i$q2w"ϡ;u$~*KQM#b4
ARjot7ެo4eq%SyPW9j4^]+zhQ$	na^}>H&;^ߝMxQ~JMmCc/h/SVD^n?YA<fSh2~ABIM(Oa$f<Q)ԟV|7^?f>R++4;S֭2MǪ[2W]D96x?gNVwk%'Ә
].f.T۰z8\w3qH//"$!"'%2GMA$6ԖTEWu<חx<7S#nPilg{qh^]b
|(
IL9]yl7Ou_b wR0"{|~+aQ3Ggھ$Ċ#gkb6Rg\
B#M+ !<Ud{u!
UWO	Oi$֤<'ZC^Ja >j}~E}Nf\窋%oR)hBNBE{>g77p_dd
ΔÞ[VyPAP3BC,0TTE*Xgo<...
```

## Module: ./.npm/_cacache/content-v2/sha512/14/68/07da1f3328d8a6f658e3edd6a79053dc20220af42a796e6f9cda041261e3e1a5a1b9f9eb2b2ce0e2848a2b9fe3dee85189cd6857428b4fbfbde34da95d5c
```
     <s65+0w}lYӥvqwYhʢ&J{$'Y5vV@$@0cIG~ڏ0Z)W\YxdiXF,|da?B!>DaMU>}=',Ty{HFr0a0W<qYc˝Eq4!Zqrˢ͂%\YБ]l_D!U[
mw䡢"yW?Oڣs9lwO_2U7xtpKԴC\x˰*_rk5-SWJWJ`k̏	A8`OX8D
R Fs}[ךp pK"0R.v<E?bd
q=Mr')F.<*t#QFkŜxȪ=w-_jXbAYCQ#ϕpH Pud($zfE	J9w
XC$\NtYWjNP-ɣw_>w״*YEIw棚V	<aa-R2b~2V5m
'[6tNmS}	tNr3x{7[~;z/~t
	ZN Nx7no ǝ7A=SR	{nu3͗>m?;nIZ#~BnSSZuOa/Ϋx;>jOE;/px)QMU[a}m*Z]h:.qA`s]VsB{SШ;{/	%n;B]
K#w'...
```

## Module: ./.npm/_cacache/content-v2/sha512/15/03/783117ee25e1dfedc05b04c2455e12920eafb690002b06599106f72f144e410751d9297b5214048385d973f73398c3187c943767be630e7bffb971da0476
```
      Z{s[gȀݺ&1s1x47EZ!ZɄǺ_~{YM&>ΞCz˧b/T}^ئqxz}xTo4hqMO"c+KG	òϿOY휰gs߱·om1IS>ioXe^q|SC>$C#Gդ-a>i15dċ,gZ YƝFO3x-"RkusW0r+ݩϒ	Jr-md4a 8@Uc2$@Py`~~C͹K̛{;K_yQ*9FqRge/J|+\[9el-B-7_4~E7nu8ӯ|Z﹖%p7'or߬?>,,;ŬbUYl3@g]X[Ba\hJD^Jp,&K6j̉ì P{BjLb =ן2,<mƥ,#v`%ss\OHVv鎝*bpNOr,\iԘ[^b#zC	T#
 H y`~
+L&+g5fHz0(qT
 	3 %#YWd=DƩ$, %q$G
c2:bNyEvQ"yb#Z,IU \Y53yl"Ro'&=Wӄ/l6zYgȮ:s}^vF#+?c+NC˫n
cYy=}u;^T=Db...
```

## Module: ./.npm/_cacache/content-v2/sha512/1f/70/512c2fa883c0da0defb537ae6aba2179f87a072a6ec2046e81572fcc9e70b71aad9e8fd86211b2192c39bdfa9f811826ebcfbdb5520299069aad253ca34b
```
{"source":"QsjtvJ5ac/TGCZ47ZpJnb997xn2P0kWf5E68zc5qUNkotHFHRxUp3JpqYWPPIDFjZFErROUvgKj2wUESmsIfgw==","name":"@modelcontextprotocol/server-github","dependency":"@modelcontextprotocol/sdk","title":"Depends on vulnerable versions of @modelcontextprotocol/sdk","url":null,"severity":"high","versions":["0.2.0","0.3.0","0.5.0","0.5.1","0.6.0","0.6.1","0.6.2","2025.1.17","2025.1.23","2025.3.19","2025.3.28","2025.4.7","2025.4.8"],"vulnerableVersions":["0.2.0","0.3.0","0.5.0","0.5.1","0.6.0","0.6.1","0.6....
```

## Module: ./.npm/_cacache/content-v2/sha512/24/82/08ded6aa4399e21b553a2ab89520de128f3dd75815f1a6538aab5b00f3ac8394fc64c86e4b281bf095b9ddc51c5d55c482bb9a3083b4dd3c8e7d20203c6f
```
{"_id":"safer-buffer","_rev":"9-194c14f9664bd82349dfb53b880b0067","name":"safer-buffer","dist-tags":{"latest":"2.1.2"},"versions":{"2.0.0":{"name":"safer-buffer","version":"2.0.0","description":"Modern Buffer API polyfill without footguns","main":"safer.js","scripts":{"test":"standard && tape tests.js"},"author":{"name":"Nikita Skovoroda","email":"chalkerx@gmail.com","url":"https://github.com/ChALkeR"},"license":"MIT","repository":{"type":"git","url":"git+https://github.com/ChALkeR/safer-buffer....
```

## Module: ./.npm/_cacache/content-v2/sha512/25/dd/8c860a9fbe7d42cce4d98282819ea2a1ba0da577894351aace633ad815ac9816aeb418c63a9c4e031cc76d4d3dfadf3d6e6c3ca697b92baeb674986a3f0c
```
{"_id":"iconv-lite","_rev":"225-c63051d8e2033a0f9b944f6f178baa98","name":"iconv-lite","dist-tags":{"bleeding":"0.4.0-pre3","latest":"0.7.2","next":"1.0.0-alpha.1"},"versions":{"0.1.0":{"name":"iconv-lite","version":"0.1.0","keywords":["iconv","convert","charset"],"author":{"name":"Alexander Shtuchkin","email":"ashtuchkin@gmail.com"},"_id":"iconv-lite@0.1.0","maintainers":[{"name":"ashtuchkin","email":"ashtuchkin@gmail.com"}],"homepage":"http://github.com/ashtuchkin/node-iconv/","dist":{"shasum":...
```

## Module: ./.npm/_cacache/content-v2/sha512/28/5a/94f127c3ab2e4cf2543dcf54148bba1a2436a0fdb2befabecbbdd43c121d33494a8b14a0f401b1362d03d6063c01f93a0b7c5039ddfe45671cbbd31e006c
```
{"_id":"mime-db","_rev":"108-7d3c81826b0d95fb3706544023835ec4","name":"mime-db","dist-tags":{"latest":"1.54.0"},"versions":{"0.0.0":{"name":"mime-db","version":"0.0.0","keywords":["mime","db","type","types","database","charset","charsets"],"author":{"url":"http://jongleberry.com","name":"Jonathan Ong","email":"me@jongleberry.com"},"license":"MIT","_id":"mime-db@0.0.0","maintainers":[{"name":"jongleberry","email":"jonathanrichardong@gmail.com"}],"homepage":"https://github.com/jshttp/mime-db","bug...
```

## Module: ./.npm/_cacache/content-v2/sha512/28/71/fc4add904b6a87bb4ab33a54c20281e52dd944236c2275c4a925bd5d01862cd8f78635ce416e8d8454012d6736df65c343b2accbbd366dd1c858911ead28
```
{"_id":"function-bind","_rev":"21-9aa01cf26f7dbb16477c93bbb7628ab7","name":"function-bind","description":"Implementation of Function.prototype.bind","dist-tags":{"latest":"1.1.2"},"versions":{"0.1.0":{"name":"function-bind","version":"0.1.0","description":"Implementation of function.prototype.bind","keywords":[],"author":{"name":"Raynos","email":"raynos2@gmail.com"},"repository":{"type":"git","url":"git://github.com/Raynos/function-bind.git"},"main":"index","homepage":"https://github.com/Raynos/...
```

## Module: ./.npm/_cacache/content-v2/sha512/28/83/7f9c3241411717c3430b561644f62407986ebca80548060f42aa65188e64088608a3f54e4c16faea9142f915bb72cb366e39e3add3375e45ee1463b72df8
```
     <mw8Ŕ)Ƽd.Mhr}asaX^K3m$Mmݽ8yHF<'3Z)wO擯Ѭr4jhJiQT*<1<rA'i$!G-
]AH+A=gw!{6'4[n'o2>Z5&?5</dF`˚,4$+(p ugyDs1i7"zB5ڡg
ye4 9nHtzebML&Y7Aj
{aWfecW]I=N5mׁ3ț:uϝ״#,aN:Y@<A"l0$"Ļy8̀k lqI
ĳpLjA Ry1=0Ģ.KGY( \40Ep< (C\:'R\BNR",fuEX(UYvY f2ߡd[IGHEK.lkvxSc1Lr<Kl<ˑuWs
d.l`	T/{5s0¨$՜ sA<pi@~5m_h4Ow 1E?~;|?_Qw0
;
~Q#;(B?xޏa0a];aD;FbzV^z8.uGޏ=`0G޻`C !mYiãF7ovxxë{7?'㷽`J:m_w q8fQw\p4NPQ!GwE
9|...
```

## Module: ./.npm/_cacache/content-v2/sha512/2b/9c/d08c3965c5691fed9e7125d574fc1d164cdab1eafc46ef4cc9138374901b382e8be6118589cd01b10bd6d2f5100abb76e0338d25adde73a0b275d8c43904
```
     <s7{?⾋$WZvm[ItgYi/q+j[+G}7]$ɵ̛f2H  AɌOǽE﫿t<z;cޓ'GUg[gRU'L@hN?STRG 8J\A=j~g{)Qsy:Ƿ<%tBX_|9Qk'<%D\0x6~f)||,/+xEłIx
L
:YLTѸ	SA))Ds"f	IWQXDt">5g$"(4"%Q4G(7e	PWs
;vNC)I.ajsJ%X8(cu'l,%%!llS=,$LΛ3D=mF&ΣH$A3F%蹖id=C*+"-7s΄`9cbkoi<I
N-ipF0p=	_R=RXdĭZ]rN&
 t2.4iA0zك磟/Ivпi#;v7p7	..|^{'MO_/Gp?z'0:$hQ{7<~ћf? C«p?~}«W=N`p>`B seIףC__ӓ}v3o?kIG^=lBztGN|0vGMGП&tY3@q?G 
z*9߯/zB8uOT_}՟]V~v9??ǧ ]5
...
```

## Module: ./.npm/_cacache/content-v2/sha512/32/de/2a88828b76a99a4cbd675bc8039b5978d572c1859b134339e6a5300bfc8ce01ea4586c7f1c50ef2a98e00c0f37646862cc449cf7d29b3e4e08a1b5a3b0a7
```
{"_id":"es-errors","_rev":"4-df089f891c962764c4960eba2190445c","name":"es-errors","dist-tags":{"latest":"1.3.0"},"versions":{"1.0.0":{"name":"es-errors","version":"1.0.0","description":"A simple cache for a few of the JS Error constructors.","main":"index.js","exports":{"./range":"./range.js","./syntax":"./syntax.js","./type":"./type.js","./package.json":"./package.json"},"sideEffects":false,"scripts":{"prepack":"npmignore --auto --commentLines=autogenerated","prepublishOnly":"safe-publish-lates...
```

## Module: ./.npm/_cacache/content-v2/sha512/36/a0/0307c5633c52ccd95d15bc751ec30c2cc3465605a21d828fa2787b4ade16ac2f3e2a78246361ca9f07a010ac182044aa69285f0be76fd5a9d56c3b8ec397
```
     =]w6}
Tٳs%DQrۺ(uKioA`S J%'q%`` $"c0YgWcYVՂMqUm[n[-ʲmr+Gxf"'W;tҲ,X|I_'y65xRso	J`|}󞴐d|7m^s+%$LhpU5ȘV "o2,YeFb6l^|IbPT&69&,rnKY'1[HL$6-	N,DFƓ'5SW'[e?z;ݭ??cDP8<cI;.8cC?)
rx=042!O	Ќsg$iX(xdcZILd
A>aQ ID0BPMT
'*
QٕK >!"ϘT-5`	x)- 0r3AkLy"[̏ dڟ%k؏@862*@uI\H`̈́OW{Ͳ	0!e8.9#$dRpBʾMxn9 rT+1!q>!H;6/rĀFۻM0z08}1=;; J
~_gg'ßOj߷g NόQ
''/wC89qM;)`U7@dozgNßjƋq8=x{p6;>8ޞzppr''g7	89!^cS3OtjNzg{Go...
```

## Module: ./.npm/_cacache/content-v2/sha512/38/91/424eab51c0557a06f8d77c1bb0fe1f04cc26535bf4cd87ca8399648b86b61ed29637b3968d4a76d39d832a040372de115f552c51e14636bbd02065c5a333
```
{"_id":"delayed-stream","_rev":"23-fbb445ffaf4b8fd4d11e28793929c6e1","name":"delayed-stream","description":"Buffers events from a stream until you are ready to handle them.","dist-tags":{"latest":"1.0.0"},"versions":{"0.0.0":{"author":{"name":"Felix Geisendörfer","email":"felix@debuggable.com","url":"http://debuggable.com/"},"name":"delayed-stream","description":"TBD","version":"0.0.0","homepage":"https://github.com/felixge/node-delayed-stream","repository":{"type":"git","url":"git://github.com/...
```

## Module: ./.npm/_cacache/content-v2/sha512/39/e8/bd387e2d461d18a94dc6c615fbf5d33f9b0560bdb64969235a464f9bb21923d12e5c7c772061a92b7818eb1f06ad5ca6f3f88a087582f1aca8a6d8c8d6d1
```
      =v6ͧ@{*)dI]oqcS"d1H-IQp>ɝ|R>:nO`0  +
$
V576jnZCó^ꍭzYo~WMȿoBQ1{0y>:=
8^2^83jՍjMz<09~܀QQ>$lYwb7ٍY$,
Q,>aC 2:H%nu#
!?yя')RИ@ȇQ бJ%HwqrHdBTK}¬J2]+
+Q`8IxPJ[EE(&v0
ӕ YQǽBUP*iL  P
Jv2B|]  |]{(큚l;l9ՁyFpP:R.
8)Oi:Lwԩkn?@hMuK&Ĵv	Ѝ &o>pԪw7ݱz:y״qxƦnHw;J1q'4W1Äz}*`i){p[d-VG>I4zo~x3ܢp.bz&eW&S4j@bA"_T12/Lu30+erLw4O*0':#?PH-
ch
䭛<5!BDJ\>3u%-
SFK	 lu+MHՃMtsKG}kǭuMH[6u5	Wߗ녜}vD(E%e5<ڵYgI:n/pӒ)vssS	Isf\q>Ws:PF ;䦱{'5i...
```

## Module: ./.npm/_cacache/content-v2/sha512/3a/88/cc03eaed577572a719bf32168ce7d613175d17d5e3c8b00ef3a3ea3e6e7f76d88d710eb21c2dcd0f623e2bd6d126d773cf84a6fcfd5c6336209c11959b1d
```
{"_id":"universal-user-agent","_rev":"18-22b7546121d8d08fd6cedb81b276c8c8","name":"universal-user-agent","dist-tags":{"latest":"7.0.3","release-6.x":"6.0.1"},"versions":{"1.0.0":{"name":"universal-user-agent","version":"1.0.0","keywords":[],"author":{"url":"https://github.com/gr2m","name":"Gregor Martynus"},"license":"ISC","_id":"universal-user-agent@1.0.0","maintainers":[{"name":"gr2m","email":"gregor@martynus.net"}],"homepage":"https://github.com/gr2m/universal-user-agent#readme","bugs":{"url"...
```

## Module: ./.npm/_cacache/content-v2/sha512/3d/70/9e407e6f3f59d8bf9189580edf77bce75b0d73d1eaae1ea7f0c20e364f8f0fa94d555a9a24e394123b4417de5981f73d033b4512e2756c93bb197a62d026
```
{"_id":"web-streams-polyfill","_rev":"51-95063035045738f933f4eb74891766d7","name":"web-streams-polyfill","dist-tags":{"next":"4.0.0-beta.3","latest":"4.2.0"},"versions":{"1.0.0":{"name":"web-streams-polyfill","version":"1.0.0","keywords":["streams","whatwg","polyfill"],"author":{"name":"Diwank Singh","email":"diwank.singh@gmail.com"},"license":"MIT","_id":"web-streams-polyfill@1.0.0","maintainers":[{"name":"diwank","email":"diwank.singh@gmail.com"}],"homepage":"https://github.com/creatorrr/web-s...
```

## Module: ./.npm/_cacache/content-v2/sha512/40/6a/51569cd2694b37d0905218f8ce83852f7aedfce1eadb1c1a13d7378e36fc827f043122452c84b00ea8dfe4f448c6be23d19964d37ba687daac9258a4d54b
```
      ;r~fUyN$ue1"U$oJ]3M00xl}~Vs%ۉSޭ<XFn4`!}|9C-/ljEC;oVsw;xo_QትaEb!P|҉<Ew^fyV׿z/^ &

eT|0m)rfPH*fuy*Zs)kX	~
f
Ss"TZ
Søb<--C9H5SLg}(Uf<@
[fP'm+GX\ pBjG|j><"ЖkYkJ/)F4zQil־5OC*8<qn޹$Ed`Lz!k+-/AK+wAd&@^4=)|Nm+r/[(Qɐ^ )&DVH
m0IeN9IΨ1GP팡7cor2<hL~1t?ztla8zg^a7 '0N;MG0Z	^wLOÓ`y&,d@#Yg4;#8;
]`0ǣC;ԡ7vt}gu''
óF'81By:qsеTI͓PK`@phJd9`2M2qQoL9
OdcB
vuU1n|q:ݔ"9:C[x(sOfڰ [,˗]!YF|CGaĦ]9%A]Q3.\T...
```

## Module: ./.npm/_cacache/content-v2/sha512/43/96/6ec997140d6c26823474add9d4db04de9ee20f5de56fcf6c642be4e18477373a839ae46b6ca86b5bb7d9da8274061e61d0376ba956d942fcec3ac7b925c6
```
{"_id":"toidentifier","_rev":"7-bdf3a62827cc4ee2e391b3c8e445910d","name":"toidentifier","description":"Convert a string of words to a JavaScript identifier","dist-tags":{"latest":"1.0.1"},"versions":{"0.0.1":{"name":"toidentifier","description":"Convert a string of words to a JavaScript identifier","version":"0.0.1","author":{"name":"Douglas Christopher Wilson","email":"doug@somethingdoug.com"},"bugs":{"url":"https://github.com/koajs/toidentifier/issues","email":"niftylettuce@gmail.com"},"contri...
```

## Module: ./.npm/_cacache/content-v2/sha512/47/7e/33f6b6481e364723ac64b27cd3d174a019c7bcb3cba0851930d9e6c365b7e7e78ba1a94feb8f8516ee4a5e170890178db04f4f32e7fc5de948e35a497989
```
{"_id":"@types/node","_rev":"13527-e2855ea3690525159d7eaba1d4d01cef","name":"@types/node","dist-tags":{"ts2.5":"12.12.6","ts2.7":"12.12.6","ts2.3":"12.12.6","ts2.6":"12.12.6","ts2.2":"12.12.6","ts2.4":"12.12.6","ts2.0":"12.12.6","ts2.1":"12.12.6","ts2.8":"13.13.4","ts2.9":"14.0.1","ts3.0":"14.6.0","ts3.1":"14.10.1","ts3.2":"14.14.9","ts3.3":"14.14.20","ts3.4":"14.14.31","ts3.5":"15.6.1","ts3.6":"16.6.2","ts3.7":"16.11.7","ts3.8":"17.0.21","ts3.9":"17.0.41","ts4.0":"18.7.14","ts4.1":"18.11.9","ts...
```

## Module: ./.npm/_cacache/content-v2/sha512/4a/9d/5a6e52748af0e44b38dc68977112e9cde7f5ef92c149dac30115fabac74af285057fd9bfcac057b6d5c329987b4f3928a3f0af7dff049fa04b9339b9ae31
```
     =kw6j$EiɱSŖ:lG]C$(1.AI/=;V`K`f00-ѲNQh}0l+ǧZ7jafa;4M=³	3H0 'y+{І(\RUQ
]D}P{3' åGWpdA
m0T|ښGY4OK|zY$(a\QEEӛ;|D=W{4Qܵ
ao?L$6wQHTT3/S&/>ݳ	oEY]ڬx^{kNŮiHfx\	i4\,Hx[PA|h7}gyK]H1(
dNJc<z#8w-s(',
<}R&>$\pr2\s-BGV	)5'ጪ1 -46X,Uݐm 3%frA ף9e\PDlJ<%ƍlAHyP!k]1.ϕSUٮhVz.`z
 UlG)\A5N 
4Eıf-q,Cs*8P+wl|KȔ]Sٽ>\K[t@jω6>\sB$#G. 'L]QF/p98vw	zS(t.wYP~A?UaC=U?9}뿀G7h H0F^"WNy;~Qި8CEg8ꝼ>bpمN~6_t_u#z}n/;HJ?8\2x9w...
```

## Module: ./.npm/_cacache/content-v2/sha512/4e/69/c400402c04955933f0000c42ec2bbea5967c1c7fdbcc2ae3f3f097e53b57eb3bc2dc862b6bd1f35a37d77e029d018cab6a5aa77f275eea7839d787c08bd8
```
     \{6gJok$ŎS6*kזr^l6ȡ (Y(^'~E3f~3xKʂK6:!^o4C;=Fyt8fI	<h<'ӆdрRDfh.4ۇw `ϬR3fgϞAENb`*?C%[SUME@T_\{JV&id"Ĉo4@o u6F5aoSDR%O	
/yCXp%EXqMcԻnAm<|[Û|h>Xp
	T".Tz9V5.a" =Ylb\%\BO)*4iS'JPp+(.fOi!ȝhrBZԚrɜ
թmio49|X(3GR \fER2ws
kUgr?'6IvԅpO<:lKy!hQYO(αn[ROgZsB#)C_YVKqu+o>><x*%XiC%RdUjU*UgTW
)aOM^Rx/%W`cKL 6[7OĲR94
SjE3nٴ=S^j)UH^_XfRپ(IL4͍Iu^w@&ubX<@tC]T\*4Z-cp	>߽Uj^ksvįn-7^"v"i*BHN%49kl˗XmM!Ĵ6ͤ?C
S׹-1E8...
```

## Module: ./.npm/_cacache/content-v2/sha512/5d/d9/086ce7ea66be8a1f0ee1048d4de2ba3ae8d88dd3b8a5f56c82cd1ed415975d29db023235a1c76de2a3b4f6c5b28cd53dd86d82ec045128325b725f23da0d
```
{"_id":"zod-to-json-schema","_rev":"100-3d99282ec3ef460aa58ea78df279dbe2","name":"zod-to-json-schema","dist-tags":{"alpha":"3.14.0-alpha.0","beta":"3.22.1-beta.0","latest":"3.25.1"},"versions":{"0.0.0":{"name":"zod-to-json-schema","version":"0.0.0","keywords":["zod","json","schema","conversion"],"author":{"name":"Stefan Terdell"},"license":"ISC","_id":"zod-to-json-schema@0.0.0","maintainers":[{"name":"stefan-terdell","email":"stefan.terdell@live.com"}],"homepage":"https://github.com/StefanTerdel...
```

## Module: ./.npm/_cacache/content-v2/sha512/61/9a/372bcd920fb462ca2d04d4440fa232f3ee4a5ea6749023d2323db1c78355d75debdbe5d248eeda72376003c467106c71bbbdcc911e4d1c6f0a9c42b894b6
```
      }vH`LT-vf˖f-y$.$,`dVϩ93̦?w%s (;]/qƍ;vG1(l6;9:6v/[[[Fd4IPT8<a#ģGQe\Oϣ*qG!l[6?d2I޼<obOi*QaǮ)L"qtjLR=¸n Rw"6I N:ӿ{n
A#Bύ=4v	Ww
3T5k?uutőj`\?I}uiL
t7#ܴ
ϯ^]l0_wϙzDF,*M*O~|umOG
݉sROɛC9'Á/-zo[z2~۩՛,`7pDqꇣ3e}zP
G23è;޵G==jimV?
!Ӛ'n?"i''j
)M)4iqnXOE,eǲ\'
~_+Q+RvzC2LǪ+1
o]˙X7ܭB7MNn7q4q:öD!zG?5!5<|o\FC<&35P9
l\Y7=&h&X1[.c	WK0ӰS.m&@7[# N&S?ԇPcӧN}dVF i<(\:#h:1
ї!TT#=~Z֠y"_h
Qn'OfSٍL?...
```

## Module: ./.npm/_cacache/content-v2/sha512/64/36/3e6cf9b9cd34c5f98a42ac053d9cad148080983d3d10b53d4d65616fe2cfbe4cd91c815693d20ebee11dae238323423cf2b07075cf1b962f9d21cda7978b
```
     <s6ޜĤDY#m(Jӌ(`m.(عff"/.v 5fy48\;V鐢vms|iNZfm
@@'">Sr<#6
M;CR4Hevȏgs#ތ|׾7s1WЏf<`<sGk43owvFq q(t@f"ӀROdn3EBXY b,2ysixgmbqOO"z")s('pNEQk&6<FIܱpG!	(6A[ 4q"eH;e1DJH4sͦn-|KG!4rl6~4p8HܢthThHn'ixڢ>Lp w,=aKMC-}>!*E@,2ƏT
^KNalz!/@[y.O!.ྶE>O?	@N[;D589?/.9
[dprpppS$@txJaLjq=O[`x49zEٓs?
mpmܐ#?}:{?$O%OQopE{ǽw}u
TX,}z`88=AvKSԏ.P!oO<0N;K*jZK- ؋L~h] j>C"̳qͿ|5SWyN\R=|XPwi2/,  T675YӴ̷#B]PGo׋B...
```

## Module: ./.npm/_cacache/content-v2/sha512/65/42/9187afe4505a0089302d4d83d9277870f70371c7e04804e8a39e51bd3e7ac9b027128ecd70cb20fabc9a5a62d827cc3aca6114aa7f738ee917daf77c6c46
```
     <WƲSlYߒIiCI|Kl8롼F@j%>NYI|wzݙMHȃ'icYvzLK'h8O4]5hO)E''(i,~MߕVyچ"/(-.0
EkZ/lweciMm81:
1HXΊa7tZZ۠ɖyq
|i Qx
XV$FeC1«uQ'NkaZq*E6$}Gy<Y?|{޵p( Sǳ<
>KCE9|b3ѿiD9"˧؁Ko \_8)0xvY,@b9KC`B f$'!}
Dq6BhmI&!DSbrEDq$eH24I<k.Jؑrv`8(J?ŬaLj!=z<I<Qu)!3Т"A-W3>I,XP1(#$TxSn+d|~RjzS^A5r]bƒ|CS`+^,-b@sﮚLxj px4i?؇1[y8y3~7wvG_`
vG~}x48>2|{x0w`8;x?&0O`v8dİ&57pKGy5d`;ڇx4:^F#a`47J}7y3>"`o|	 //w;|ہݷk<y38R...
```

## Module: ./.npm/_cacache/content-v2/sha512/65/fe/47d8ac6ddb18d3bdb26f3f66562c4202c40ea3fa1026333225ca9cb8c5c060d6f2959f1f3d5b2d066d2fa47f9730095145cdd0858765d20853542d2e9cb3
```
     ][s8Ϋ+zu#Q]v6J-$yLy|Fٔ ev濟j(N['q/h\	MlxGgYV^רZiU*ͦU'VRz _"c=eWGG	
c71,AGÌEBx?wiWFkVU!ND8"YZ:xˢ	xϥ" .aN0XS7B=c`B@LbL-!\g\n|"86g1:;1YL\g0LKg (/˂kDC2Mu8$Cq_DbQY_8ܥQ&YNUO )Q5d($zaJ:ECԠqDRg_ׄKM2 )hǔB<qM"p8i$c4C`1G@ͭ: \j%g`i< S'"2fA̙M5MΠ!;@3ްP{#3t_5t?{"t;蝽?uO^o#8F1LuTYwpu^N{_ިOu>@wig /χ]O_z7ݳndBs`szJzoގIw0W]8u^v5/p|syUGoȴt.%N:ǣy8>QFѲϽaAoH
zp~V49_IO]]55@vIsRaR1#6w>cq<
UlVnQ~~!¿OFپlI<4...
```

## Module: ./.npm/_cacache/content-v2/sha512/67/24/83ecd7fdd5a2c1d11c4be0a1ab28705797b11db350c098475ca156b05e72c3ed20e1a4d82db88236680920edaed04b8d63c4f499d7ba7855d1a730793731
```
      ZnFS:?,
uN]TXeHrAD#r$ѡH./v_k_`_lsfHh	'3~"|3Ո}Wj6ww}?f[j{g_5[Ϛx	teI*ckhfD~ؒY:J'Zy
7X|;]5f39턋DmAQ]ol	iM4 ~5y HUBz>C¾ Eʗ}
U{QmyMAg"Ե
DLp!D/nLX	,"
\D:W[=G	<5$-i7<\B$Ry<X\p tM*
dۈoRf÷8N1HI7iʔ`*YA0wM{K;Ss!R)*4|x偆4ԴF¼뵦b֝{ʟ2qaa>??"[-c"ycuOuMp<^%oK\Gat{y*jΎh7[-q\t[xr)-B/Ix@5&b (ĔT8sT.܊EP9t0I8MoXC&d'7t*<IuzJD
[;Uҷ;?7(,EsF]xg.ѐ?ch@u]oJي%pD׼XLh]N|4X$-@@#%uHHQB+76x5 (qC1^)'>
}?!PqX$V̋| U@
Z5}1QF`-Ąb["
cƷʦ
...
```

## Module: ./.npm/_cacache/content-v2/sha512/6d/58/58ca2f854d409890c6eefff1df3c1e9f1767297ac156bef2991d6a4a6442c30706cb49dee1e3f0b96ed73648527ad6fe6889467a67d78c5548b128538e36
```
{"_id":"raw-body","_rev":"116-f947d8edcfbfe8bfc5184ac798ed8290","name":"raw-body","dist-tags":{"next":"3.0.0-beta.1","latest":"3.0.2"},"versions":{"0.0.1":{"name":"raw-body","version":"0.0.1","author":{"url":"http://jongleberry.com","name":"Jonathan Ong","email":"me@jongleberry.com"},"license":"MIT","_id":"raw-body@0.0.1","maintainers":[{"name":"jongleberry","email":"jonathanrichardong@gmail.com"}],"bugs":{"url":"https://github.com/jonathanong/raw-body/issues"},"dist":{"shasum":"5fdd13390c80a4ac...
```

## Module: ./.npm/_cacache/content-v2/sha512/6e/e7/b01f332f60bdbd8dd7904d520b79c49a64a9edfd12568e8642179396eb467aeff1a648b06438533baa1d4f237cc536d25b6992f9790bb5bcb7daccec23e2
```
     }vFSD DʗĤamٖbؖ#ɹ,@DL JHOsةNάmU_0wѐ<~voƯl>^{o<lZ6!]{5_eCSN!WeiY6dn챽f!G:\Ffht:t7<EfSls޿f<< e|}Vf,^Ȑ(B1,b1T@r٠rΰ(8<d|§eTb}t#jg2GͣJt0NEe(42|N<6q:Ie
hQ8P輀`;}6ɒt9uk6b$Ţ$؏,g(!vS_M(
6}-%
ejO)T)Oɨ_y\b&dqv]ibCT.9E4+	8 332E1sI0YɱzG2lTr7!;;9:7'??|jg^/Nޞ3Hqz'vr^y|szxvNNWo^Bg/>?~-{
^ ?WC'+EaaO׃/X);`oNϏ}yp޼=}srv?b_>:Z_>Vc;{q%V֟bس7?✽8yB<UA<8~=\'PʩD/1;n<;y}~
>\gggHӓW'T{}(JARʈ@|{vd^BYg>3y1	&4eO_jE>I2j̲5hq...
```

## Module: ./.npm/_cacache/content-v2/sha512/75/10/7bf2cacdfe5ea0a96ba56a1f52af17989f179d7481b7d3e18ea8affd3a52d5c8b8371cf9ebe92a8e59358e5ca4700b6786602919e7d34db9282f4aba6038
```
     ^X0:OP5m;eܓ@H5!I8@BŲ-*05{̣'9ol \.,iky~'L$:A/I6=f-..zUʲO+kKKPnqiuim
ӟoA
C
_4n{W/¼?|d.w&cwz
Yu<ym*EqgA?p4
^cfy;YfW?a<<gvYNy6a|rz[^3ԛX^6Bڽu퟾ſI˖>n8k󿼾Y8|0+#{2^VIXc<0΃<JboA4@iTn~0ɧixk0ʠ[o
:VP!\Pw^4
ɸԄE'G^2(O88?m]}{ۜ啥󿴲3[=TO>Ip3pda>L 1wM0tׄwu (x&/dndT (E>'ir10qEgNijϦgga+$^гQғg=xa"Iσ<hquTv oۓdtyF0(!
\ܯ"g`lU2ZˋGaA
-3q *"+oMQ#ԋ7@\x#(8Q7 4"}GX0<y>6:<}?}b~wC#:Ix@7Z	Aoz/N7_~y$<
7LFEc{OM³`:R7 pa-pßkFpUi<KxOG#3...
```

## Module: ./.npm/_cacache/content-v2/sha512/75/73/0530927ce781a2b4a588fb70cc2e27e456f897b42a630ae9bd6efa7b0a7c94823edbd8ef09fcc9f1daff2d4f91d25a43ddcd39899a81a5baea0817de2442
```
{"name":"@modelcontextprotocol/server-github","dist-tags":{"latest":"2025.4.8"},"versions":{"0.2.0":{"name":"@modelcontextprotocol/server-github","version":"0.2.0","dependencies":{"node-fetch":"^3.3.2","@types/node-fetch":"^2.6.12","@modelcontextprotocol/sdk":"0.6.0"},"devDependencies":{"shx":"^0.3.4","typescript":"^5.6.2"},"bin":{"mcp-server-github":"dist/index.js"},"dist":{"shasum":"86be664be1a1fe05b295cf76d505a6b3fda47046","tarball":"https://registry.npmjs.org/@modelcontextprotocol/server-git...
```

## Module: ./.npm/_cacache/content-v2/sha512/77/62/562c28af999613488a207bd32c805099aede7bd418a47161989230b59219656d3783946a99d83f2f0fc13f9496bc58659b6fb3e59bcfd725857b2091d967
```
     v6?:)lv;i,O6;+ȶ^[Xd盛cI1%ْSU 	 	vlgn|[ƏP(
UZ8yr|z~o>᣽?߿y7fz7؟Ye-Çwb˓"yZp6|yr1zIyɆ=zk2(8(OxZ4}Þ7A՜]d?x狸(,eq<[viɣ1圳ly_1+3l"KY6-8+0[>f+YyiĂ8(yĢ,\-xZ%7^a9sQv y_g(86,Nd
$^ĢsP<(3*E3㰖i1bhz*!ƱI ̖1/ KRLQ̳>x0[i\9։2Vd<,(>˒$Y0b``]s-qqHӍWU|Ũ$aS.&G,NY'2H8H2˱?s.g?>f'볿<=~>?:g'矏O'~`?~}tzv'O^>>?gg|阝>yӓ/{q)8cСh{yӋ'/N.1~|vWG/N5{Wg);=;=9}ǧvrNߏO//G?^<?{
'gًǯccɋcXPc?=?Svѓ18{}QUx̎^Ä<{}r 99z
L5V5q {z|sC'ǟOR vYr;dG2>3?t?ؗ{q7|S9...
```

## Module: ./.npm/_cacache/content-v2/sha512/7b/79/d17e07d4678acd18bdb7da05205f4e90372c9ecf4e0a76316b17e2d34683979ab3a014a0e0e0109db235bc1274faf5ea9d606991a49c223d560dac2696de
```
     <mw~Ŕ;^@sݖ$LڧElJ>sf%b4uOoчΌ2M G4V1
^uKujBua3<YB4
"GP8G	PěG9cѤ(ۣGj
 +60*bX®u0x@8#*a
gvAѿweNy{	sn?D?Cukfs?)e=<1:M\|΢b;s^
Ixc(.)cqQ)\TQw-7Ny©gc PQxxyY{>QahGQ0{Bx< O#4bANES,Ćb$x |3/)0yxp'@p7f`Bpc1:p;c3"|Fq_ / ˻ڋg<!BGM4d^6%,K>0_
YHO Q
LbCr+$@LDZg|9O(nq8.GD;wkǓׁgl(.ocN- \j%fa/ 61b@wO:p;=@ǝc(ϡ{^,OI~jg迅vg;.Csnn0^a}3R9{{iwsYy pGN808w;^t{:;
IR'Gw'C8wN:Tg8:mwߗ#Ó@...
```

## Module: ./.npm/_cacache/content-v2/sha512/7b/99/cd9925f93b3a1e2632463b312f30d21c0b70f5f0d8e125d217cad60affd38150866e6a1a7ddf494f3457d0122c3ff84436d9d92a067231e302fb26c93a92
```
{"_id":"undici-types","_rev":"93-ab54db5776afc9268dc2bf6864093d94","name":"undici-types","dist-tags":{"test":"5.24.0-test.6","six":"6.23.0","latest":"7.22.0"},"versions":{"0.0.1":{"name":"undici-types","version":"0.0.1","author":{"name":"Matteo Collina","email":"hello@matteocollina.com"},"license":"MIT","_id":"undici-types@0.0.1","maintainers":[{"name":"ethan_arrowood","email":"ethan@arrowood.dev"}],"homepage":"https://undici.nodejs.org","bugs":{"url":"https://github.com/nodejs/undici/issues"},"...
```

## Module: ./.npm/_cacache/content-v2/sha512/81/8d/aa0e9c2308afca3f9c89998471ca9e556904ff58f2b624c483712292e3c81ebca42561aa94700f5938a8be11f07fa22bed901628a431b44e5f8317bf274f
```
{"_id":"unpipe","_rev":"7-2717c441cd12050aba2f061fdc2ee1cf","name":"unpipe","dist-tags":{"latest":"1.0.0"},"versions":{"1.0.0":{"name":"unpipe","version":"1.0.0","author":{"name":"Douglas Christopher Wilson","email":"doug@somethingdoug.com"},"license":"MIT","_id":"unpipe@1.0.0","maintainers":[{"name":"dougwilson","email":"doug@somethingdoug.com"}],"homepage":"https://github.com/stream-utils/unpipe","bugs":{"url":"https://github.com/stream-utils/unpipe/issues"},"dist":{"shasum":"b2bf4ee8514aae616...
```

## Module: ./.npm/_cacache/content-v2/sha512/83/35/2dfeab7cd675ec14628815c0b76277c4031e4d92e9c27e70e5bee0524854b4d9b717bb82e679ad001485306cb5b158fc7777da7c4b94286ae8ca70d43171
```
     [wu/g|,hF.$ud$$Er,(L$@ZYۉ(VEeK^-҃߀IkWUwWuW\ | k}µ- /,,|0MMM͞>TSSS3SSkNMONF_=6#9.655JNMMC*׈鐉Vk.*Jhfj:o..XIcb2薉tml젆MheT	AV6 eZ;El2b¨fv&:r7u9Vݽm!8VM.ѐfռ&1]Byu *VxBlL&8?
MsMk@tfxGzS%@v ΄k!!eg5-M_B6,#MKȁ@ڒeǤe#ft Zא;XoAi5DݳM$4f!Ǣ% 5B y2&Tf5r
kк5-W
{G90
F4ձxŦc,febbheo_Y@+/,\@R(o,~}*+KDϣo[\PF
Z2xŅetK/箮Utq@Njqa]ZrK-^\\fy%4._Y]<t+h~ZZ^Z\zV+hq	--V/^&毮~}
/_|8V7hկ/\d;/@7ϯ../A5//^?ZFWVX\Y(++ _YT\~,.AFI=|~_]Y^XP...
```

## Module: ./.npm/_cacache/content-v2/sha512/83/b9/c7e8fe9dc838a8268800006a6b1a90ad5489898693e4feba02cdd6f77c887ad7fb3f9cfb1f47aa27c8cc2408047f3a50b7c810b49444af52840402cb08af
```
      =rH(k6SdӲDܕ%$C0AH Jft7Cyfd3LL;-TeeeeUY?o]¿v%oskv8c{_eY)KO?b#`%̆i8$ƊC9MϥH?ǙiƀvJY~:#?iZM!K&WsLW(p(H{ջPe6I
/he-6rdas(sK$ﲆ Mn3IGş0P͟xJ$' 
'~^qT
$p$vsӂ,
O1LQ8nƁֱph6F8&idlB:&Ȁo>YBH Y2MIlk5;-w!fVs[WLᵯXi3$h&lfaz=(
iFa$	y֭^$%GyP
|I?H7&c+ovC)YY|[#)rZNWE*tBwY}nˌZ/"AAhClgFPx2$};IE[0n-Eo`OhF6Ej/INwSSf﷬>[7sk-~@DKl;Ovcs[y aLE6fTMC grC)@e?Y&nZ!F}8ĎZΰ%* x 	2!B<PfY_^{<1DA4:ct=!t<H0,A`<JgIdeogYKFΪ/ ⹫...
```

## Module: ./.npm/_cacache/content-v2/sha512/85/a2/8e1df3f60e23142e45728bafb2ad57985042f9db1108d5d95af321b9c6ff4712770cccd611db1f0d68767706738c51e64cb2bbf222b96b76864a79ff2b28
```
{"_id":"statuses","_rev":"75-840f45060c26a2ac20c2c7fa881967cc","name":"statuses","dist-tags":{"latest":"2.0.2"},"versions":{"1.0.1":{"name":"statuses","version":"1.0.1","author":{"url":"http://jongleberry.com","name":"Jonathan Ong","email":"me@jongleberry.com"},"license":"MIT","_id":"statuses@1.0.1","maintainers":[{"name":"jongleberry","email":"jonathanrichardong@gmail.com"}],"homepage":"https://github.com/expressjs/statuses","bugs":{"url":"https://github.com/expressjs/statuses/issues","email":"...
```

## Module: ./.npm/_cacache/content-v2/sha512/86/47/894e330ef9f8eb5ff3045eb88af4dfe68b44a6ddec2e683d977fbc0f78fe59f3441a9505b23e25237e45234c3739de3e498ae26bdf57063dbd80d29f24c3
```
{"_id":"depd","_rev":"58-8221bb04850ae16cde9adbe7d43aa715","name":"depd","description":"Deprecate all the things","dist-tags":{"latest":"2.0.0"},"versions":{"0.0.0":{"name":"depd","description":"Deprecate all the things","version":"0.0.0","author":{"name":"Douglas Christopher Wilson","email":"doug@somethingdoug.com"},"license":"MIT","repository":{"type":"git","url":"git://github.com/dougwilson/nodejs-depd"},"dependencies":{"supports-color":"0.2.0"},"devDependencies":{"istanbul":"0.2.10","mocha":...
```

## Module: ./.npm/_cacache/content-v2/sha512/8a/0d/4994fc763eec202445ba8dd77c2a07ff7c41fd1920780c360a282dc7366afcc1b41ba0a6deab92baf83fd210686e96c7859fa539625fc83bb50ec268e9c6
```
{"_id":"es-set-tostringtag","_rev":"5-6eed393ee82b280131abc7117248596b","name":"es-set-tostringtag","dist-tags":{"latest":"2.1.0"},"versions":{"1.0.0":{"name":"es-set-tostringtag","version":"1.0.0","author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"es-set-tostringtag@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/es-shims/es-set-tostringtag#readme","bugs":{"url":"https://github.com/es-shims/es-set-tostringtag/i...
```

## Module: ./.npm/_cacache/content-v2/sha512/8a/6f/438c40d0e79b3d7cbe04633380bf4c8caa6301499a7a1b456f1724cc3ca5b1892047523f4d5bfaaa2e65d4c17aeb33b02fa9295309fbea45bd1c33cc98ab
```
     kWG0:I`'Ll4RmD20<m/kug=ke,˼_$p֮8q<xy!.{ڵo+znrmks_|>_]M
r+|UZUumﯫՠ_*+߯ÿ$3|w0IχBxP{dT(GU>5"j#^/)}$q8	"9E`Y	](Èl(̊#Sf8KPS$$	]r?#჈$!12DA!cy..JLaKJ帓 ˄#E#=BDF"+"6*B A8 A@}BOO+qROEI;#2[$(<JAD
A+u,2GτPWD9
Hp[ـ@.!9>%%=,b:m,1/\# lb>zPu%`lX#B2ǄPXqizKJ:>kAmk:h؂Zцmk]ݲ6
Ekgm:M76j[}޺~uEI7llioGmQ
k[[VWk7n])Zo@k[׵vFm:M5%Z66ִiU֎?T55mQдyڦhæ[P%ַ_u-ZwxQz
e}jiZUӦ65mO?@]ݲj)YڴjmjPڦuhuӺO[[mlDPZpQzԴ55w/i[wllj@m;Whmo@M[...
```

## Module: ./.npm/_cacache/content-v2/sha512/8b/00/d9aa0d10006ae0f516afe47e27d0ceb87379a4479f5c27ac10a7eec2e2723482c984c5a79d6982cd3b8e1e4f802d041c236d38863cc96dd8c7744fd1fd25
```
     }ks6~(oJΕ'3jlM%'C$$1H-AՍ#=E Fh4SAs[[["kkkk/;k;;k[/kk;k/ky/kkO0ȵ5@Z?Q8T4	ÔԼerBӔ  F>Gi&iJ% Hɐ%7%F)뤟0F>4:IcB){)
 Jx<}NxOh°[y4e>co2bQJSZ:dd#[,-c'>a%"rx4	<Q'ApPa0
dI+iL&:~Ї3x>?6N8|DaqB8Ê	5 c h*I0#	x?Iccw0`h^7+ڋoEx'ȍ0fU!
Cc`'AD1)Ҁd'_~JM:g﻿.C/~9:lVuף.uq:Fޓo:i鐳QNN/N".KNC=#Сu i[{
0ߟ]9o]t.[&CrzvztI GivIC.. ?rpvOaC޵Qq[tu98naS[u?/*PM`G~ІO_딴Gg0E['ݳnQ]'I<{UNi[@RkF.ev4!ʍ_^_;>7>WY-5t:f|%,# 
w5gKq*ZB8b...
```

## Module: ./.npm/_cacache/content-v2/sha512/8f/ab/d6cdfac655fc97c607be3b4c79b21e9cbf10288346bfe1175dd8adfacc2315e5e27effeb4e0278113bc70e0cc3566d545d5659866502f6612df247c6c850
```
     <kw6*
DݭDpM][Itױsle{{T# %&%(;>=%iiӽX`xΆ:iU%y˴<AO4|=1|ϊW|b$
@#Z[yCUb}MtهewPQWAGfj@pCS/:]1?aWUg =N%YU&OHm
{n'?S?&oo?Nfwd/Y笻brS"/+V¦VC5>Zϳ.l.@etʰUW\<?wG'?a[g<y=㄰3M;̋2/*CveX>8'eRT|,a2<3p`%ѼYh%c(YrήQJg(*dI6GU#.E$bќ,0D(NRN`{0bp%]%"_Ud*4(uw,5	pъ೏9MbĴU&|G4Ѫb}ġQ%,M5	Hu͝hDġj/7gp-^YL\
Z <4<4m`G%sUBUU]|EL	QdSYk񶧩ktp6Bsy~O^N&?gQioǣ>=D?	:OFGhr`@Ej<:bGgN&?Ǔڋh8=Cd|y{|Nd	:9EN&1:=雟/_MЫ9q?P'?>::x}r$N...
```

## Module: ./.npm/_cacache/content-v2/sha512/92/6b/13d853dd4ac731829758cc1cf229baff35c6ef3a2e1272d1b8da79a9316d458076444b954f355f6a3330a8902799e79d99ab6862077a12a03d58b3c14bc6
```
{"_id":"@modelcontextprotocol/server-github","_rev":"17-f670ccba6469b8513e0a87093af7e247","name":"@modelcontextprotocol/server-github","dist-tags":{"latest":"2025.4.8"},"versions":{"0.2.0":{"name":"@modelcontextprotocol/server-github","version":"0.2.0","author":{"url":"https://anthropic.com","name":"Anthropic, PBC"},"license":"MIT","_id":"@modelcontextprotocol/server-github@0.2.0","maintainers":[{"name":"ashwin-ant","email":"ashwin@anthropic.com"},{"name":"thedsp","email":"experimentalworks@gmai...
```

## Module: ./.npm/_cacache/content-v2/sha512/93/fb/c6697e3f6256b75b3c8c0af4d039761e207bea38ab67a8176ecd31e9ce9419cc0b2428c859d8af849c189233dcc64a820578ca572b16b8758799210a9ec1
```
      YmOHu(|B&aF{t/a8XvOJޫ\ΝF5&*G<=>ur&qrV䩑%COn_
Н3ړ/b&{uND2J
yCR`IzY 摛q ^>č'	o$9""N
Gf<ΡwbyIgi( y$:Q*Z}
/}XTLJsӶrܕZMQÞ\ݒzcK]a"RLUdęL
	5d^،@ =&:4Πo~͵ME2FFCŹ'zRTG`*+#+e7nףOguz[GͷCN ]FBMMYq߯hG#i~`jt)E*NzO%!3)"Y+HئBu5U2 lXƩ8ZIg&ZA&4z,l.bM {Xn@TβxZ|(jF9}xg< 2*PJrNSkXq|i(\߈OAI,?Pxڋj{l~o=Ov%F/YG&d,,^{	5I, 9U,pa٢B,c
I}$'Tr l繩Ӂ(iʄ'riQӶOGɣypw_b}A-V23?FO'a܈x.)UA1-|3	`6d˄5M]\UpiDYx+ ,8s+K.u177/AX-4U
3X~....
```

## Module: ./.npm/_cacache/content-v2/sha512/98/83/e26de150e53c68696fb46f30309be0971027b3c377d7a849af575ecab9943ba33ed1ef9ffd6825996b5bd0a09ba7ccf175c46c6917ca18495957041abc72
```
{"_id":"es-object-atoms","_rev":"3-c974d2127b54dfc4a2fae7614342fcfc","name":"es-object-atoms","dist-tags":{"latest":"1.1.1"},"versions":{"1.0.0":{"name":"es-object-atoms","version":"1.0.0","keywords":["javascript","ecmascript","object","toobject","coercible"],"author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"es-object-atoms@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/ljharb/es-object-atoms#readme","bugs":{"...
```

## Module: ./.npm/_cacache/content-v2/sha512/98/9a/68e84545cf186953b6927c75871a5e5f661d07ef805b585fa7c3a0c5be109626fd58145345d8bb858e94e1b66b59937dc1c3d4eb628c1c660dea5c352de7
```
{"_id":"bytes","_rev":"69-3378ae4662dff77463ea8aaba1891eae","name":"bytes","description":"Utility to parse a string bytes to bytes and vice-versa","dist-tags":{"latest":"3.1.2"},"versions":{"0.0.1":{"name":"bytes","author":{"name":"TJ Holowaychuk","email":"tj@vision-media.ca","url":"http://tjholowaychuk.com"},"description":"byte string parser (5mb etc)","version":"0.0.1","main":"index.js","dependencies":{},"devDependencies":{"mocha":"*","should":"*"},"_npmUser":{"name":"tjholowaychuk","email":"t...
```

## Module: ./.npm/_cacache/content-v2/sha512/9a/20/280bd0336faab3f36d34408dbfb3008695078223a3a415152693629e2112e4a9bc3a6a01baf40ecf5d245521afa533aae92cf51352e8ea9ba47fbba1511a
```
{"_id":"math-intrinsics","_rev":"1-c70720a6cd2492f31b90c842a967f3a5","name":"math-intrinsics","dist-tags":{"latest":"1.1.0"},"versions":{"1.0.0":{"name":"math-intrinsics","version":"1.0.0","author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"math-intrinsics@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/es-shims/math-intrinsics#readme","bugs":{"url":"https://github.com/es-shims/math-intrinsics/issues"},"dist":{"s...
```

## Module: ./.npm/_cacache/content-v2/sha512/9b/0d/d352ac2c224d7afd5789048e0e9b109d13ec9381e7b4693a04f51c2a486a43f3cc7ca1015c096a85d687b51b6300e3505f11ac709c4fb75afeab5c65a5af
```
{"_id":"@modelcontextprotocol/sdk","_rev":"92-68bee9660cb610a7890bf43e86dad7fe","name":"@modelcontextprotocol/sdk","dist-tags":{"latest":"1.27.0"},"versions":{"0.4.0":{"name":"@modelcontextprotocol/sdk","version":"0.4.0","author":{"url":"https://anthropic.com","name":"Anthropic, PBC"},"license":"MIT","_id":"@modelcontextprotocol/sdk@0.4.0","maintainers":[{"name":"jspahrsummers","email":"justin@jspahrsummers.com"}],"homepage":"https://modelcontextprotocol.github.io","bugs":{"url":"https://github....
```

## Module: ./.npm/_cacache/content-v2/sha512/9d/38/ea7dc045122a4a7570afe180d05827e670b64a9bcd65745d29028a53bf2ac51956dc47a3ff54001de46ecdfb4b53afc42a894d2d15a743e852b836d27038
```
     m{>WLH IcΩ`9
> H/Mޙݕ28m/}Z#3/;{̣No^<}
i6
fk{hި77_Yĉ(%;C8Ĭip~yi
zcķchO#/NE0дͼ8 ]$5GA8gjGV$;9/h68Ȗ )qreG]8t<:;!~cg1T)Qr&.} m+/"'9%fߛys[Dt$g
fqߋ5"ʘ*UkF3'
uͥ0EAi"jΊƋ(@h2-sB+T
YGŻF]n_":U@0{U6Se`0Eڊ:$~F]5
hw0|[Ikgڇrkr
^wWC@~;|hu;fo
Ccנmt_p@wpX#a$ձ@;C,^t:758D vگZ}8y?
,ddAXVwhh.ց+`p::ZP>;y<ahJzqd	V7Z9~X=`RׇB~-vz]IXӆ0C}X5h;2AɜDk	*djZzAHW+ej!!gh<<\/pٵ6~5wx̍GlP|H0͜Q9 AX65D-kA`}6fvLa%ۑ=c	RRPYsҁ-A!w...
```

## Module: ./.npm/_cacache/content-v2/sha512/9d/ff/e882ddff28f922cc7638d9595c211fd469ca708b36c0b2b51b824c7ddba0d7abb78768d81317d7275563f6540bc5aa0de1aa54ae8510a3a93bbafbe329ab
```
{"_id":"@types/node-fetch","_rev":"1131-4f0b29b41107e91ee52f299bfa6fa974","name":"@types/node-fetch","dist-tags":{"ts2.3":"2.5.3","ts2.0":"2.5.3","ts2.1":"2.5.3","ts2.5":"2.5.3","ts2.6":"2.5.3","ts2.7":"2.5.3","ts2.2":"2.5.3","ts2.4":"2.5.3","ts2.8":"2.5.7","ts2.9":"2.5.7","ts3.0":"2.5.7","ts3.1":"2.5.7","ts3.2":"2.5.7","ts3.3":"2.5.7","ts3.4":"2.5.8","ts3.5":"2.5.10","ts3.6":"2.5.12","ts3.7":"2.5.12","ts3.8":"2.6.1","ts3.9":"2.6.1","ts4.0":"2.6.2","ts4.1":"2.6.2","ts4.2":"2.6.2","ts4.3":"2.6.4"...
```

## Module: ./.npm/_cacache/content-v2/sha512/9f/99/01df232feec3831a447db25086f4a89c8fedd2c1b70602e94dd384268611107242b8afb0405a303bd62113f3e6c71775f20d5e5def88fa7ab7d561e374b3
```
{"_id":"content-type","_rev":"37-442c13f025bb769d4623dc3e3f10d603","name":"content-type","dist-tags":{"latest":"1.0.5"},"versions":{"0.0.1":{"name":"content-type","version":"0.0.1","keywords":["content-type","parse","http","header"],"author":{"name":"Austin Wright","email":"https://github.com/Acubed"},"license":"Unlicense <http://unlicense.org/>","_id":"content-type@0.0.1","maintainers":[{"name":"deoxxa","email":"deoxxa@fknsrs.biz"}],"bugs":{"url":"https://github.com/deoxxa/content-type/issues"}...
```

## Module: ./.npm/_cacache/content-v2/sha512/a3/9b/123ca12483f0c840d987e37574fee7ab2eba7355e764521f2d18dbda797a5fa6ec2329e9e54a8c7fd8efc14e5654b447be246eece58844cfad3c3e500744
```
     Yms6grDJ~S%:fN<\! :zk'ssxFb] 1L=Gγߣ5]m};{Vk7[}}-)OД ON1'"-x<Wfk*\CgHx. "Ǿ7Z"hF_׌$ZKdPDL0Kx
DPS<:
xX$&)aȉ<Zy#B<%}S
t.2*$*5<`2+Vs&#:2l(B'iu/+̰lH=/	zHD4ޮ8lAAf+CE(snDj6͒U
#+tIx)Q}@<FcaƒHhjnM@բKyDC^6cE*1O
C
ݮӅJ{ߕ:|p'1 ǰ1n[gCg4g=Aλn-\厠uFv;'>r{c>aІpv{!#w9uc"
vGX}}oOp2u$9hYpP^=C}~H;0:xup:r<%NBA>9K@:bHX2[SӴ2g~|y'i=h }̡r*EBJ7ĿVFm3ŘaS~)hHoLr[E?]ʮep=UIfFDF4Q1
ySV'<_r/$iȉH1{eۦ...
```

## Module: ./.npm/_cacache/content-v2/sha512/a4/cf/d253d777600820ce2e8cb51e21eebbae425a8ab5a77c7bd4b47e6c5c322fae7802b92a8af2b3f696715f4b2081d355b8f4d4d773c5c9d748df8eef864854
```
     v۶(~)_JŲ(u}iݕ9]+IHB̋AV= g/v@$AJeNX$ļ6/4_;8}<VkEVFXlۛ.GlngZ$[}$edm7t0PլNӪNo^[{K|2F=3RG7ԑY?#ZMGeO/A2ļ~p};Yy>O
O.&hc7 V|ZB(/+fFcv=⑆F#}D]mM	3N~CǇN=C/^1?݃
~zc5shdx_/G/!:uXi_kyzRZ{w݃ݟ_7!c
(cyzux{ދurhI{_`Gʟk{r|:;	~?ޫ'P:׽_`Ļk/NÃ]/;xyãߏPGG' CÃ="7c۽WGovy7Q>g$?צ5GggMNlߒ}UU<1#0T^'f`XO]F&Ur3Q;x&:=&=ckЮ;yIh]yBk 
HpDl+wٻ6F>ϘZ1fUjc +W}g5q
!hF	ГmTFݥ<>	ƾ>NWS18[.oNa/0+MZT3QcםLF ;D|?cE60c&ZhC:!&O=y8 	(8<;ڪkH...
```

## Module: ./.npm/_cacache/content-v2/sha512/a6/3c/b66d8852b2e7f05a52b03dcfa5ddc37bfb0b8994aeaecf461d2443a54036e5ea3a3f6253e2e266fc6a0524542f0117b57c36ecdec8f36a464b00de1ced29
```
      Y{s:΅`iҝKi<KL&s#lk2wH~@Bf}lgPu?3x/E+FqxxF5[[ֿ#T&4FWW=I_`'sv0۩)Ǥ("TKz	($ftX́ _Cd&`̥FhdT&+Y@%tDD>XxkK1gÙB==HHxșs4Auh]c˙D^8.4nF@\>U2J*$`T$;mkm*8`ti̽BGXULGV{fstO|k3
O#h_ΞcG1h^W̸	~>s?F?HP"fዚ]P:\QᏹR	?
S<|J_`(r0X>0i[%ܑؑfYƧvd$!Wϯ3xWa49u=납+n@PO^_yגyE)ElM7Vդ`=Ny8Iʳ-̧1tf_QyxvuD͍  <[)KZ=5{I4WbǬZ(B|5sfpOnx	3`aE 5@Ĕ%Q4`a={>jI%vBB-VI5YFE_P<?d1M6GQFu <2L\E2h*Dd9Y+7'I$ߘ&sxDsý!3RJ)!Yqz-~<4QTm&L %Q&_5q_2kkґ]m>"K6މ...
```

## Module: ./.npm/_cacache/content-v2/sha512/a7/d8/ff298663e8ee2d918a19a0a00435a7537ce757a337e6dd8597e213c9e56d4ce61b5be30c4b719c5054fed981c51f78a88f5389a1922dab4dcf5248e83c4c
```
{"_id":"node-domexception","_rev":"6-47d9682afd8aa9ac2d4962d619aaa3b6","name":"node-domexception","dist-tags":{"latest":"2.0.2"},"versions":{"1.0.0":{"name":"node-domexception","version":"1.0.0","author":{"name":"Jimmy Wärting"},"license":"MIT","_id":"node-domexception@1.0.0","maintainers":[{"name":"endless","email":"jimmy@warting.se"}],"homepage":"https://github.com/jimmywarting/node-domexception#readme","bugs":{"url":"https://github.com/jimmywarting/node-domexception/issues"},"dist":{"shasum":...
```

## Module: ./.npm/_cacache/content-v2/sha512/a8/31/b33a7b7e3a552ffd5239b8b925c1bb6fef170979f1e11240acf18dc5fa358e0a3eeb71754e096412d5e4c3a47a9901ed76bfbc9e5df96906ab0c7ba9359f
```
{"source":1111906,"name":"@modelcontextprotocol/sdk","dependency":"@modelcontextprotocol/sdk","title":"Anthropic's MCP TypeScript SDK has a ReDoS vulnerability","url":"https://github.com/advisories/GHSA-8r9q-7v3j-jr4g","severity":"high","versions":["0.4.0","0.5.0","0.6.0","0.6.1","0.7.0","1.0.0","1.0.1","1.0.2","1.0.3","1.0.4","1.1.0","1.1.1","1.2.0","1.3.0","1.3.1","1.3.2","1.4.0","1.4.1","1.5.0","1.6.0","1.6.1","1.7.0","1.8.0","1.9.0","1.10.0","1.10.1","1.10.2","1.11.0","1.11.1","1.11.2","1.11...
```

## Module: ./.npm/_cacache/content-v2/sha512/a9/da/cc80fdf4cf5775f08a0bad130aa414b5d7ac6d515239127103b75c178823a49560d08c2b255c97a224975e84ff1ebdf5a28ba3d788cad4e59e1ff2436a9a
```
{"_id":"zod","_rev":"871-cf2f5f205fb5b594e2d2764d28ce5847","name":"zod","dist-tags":{"next":"3.25.0-beta.20250519T094321","alpha":"3.25.68-alpha.11","beta":"4.1.13-beta.0","latest":"4.3.6","canary":"4.4.0-canary.20260125T215152"},"versions":{"1.0.0":{"name":"zod","version":"1.0.0","author":{"name":"Colin McDonnell @vriad"},"license":"MIT","_id":"zod@1.0.0","maintainers":[{"name":"hypermask","email":"team@hypermask.io"}],"homepage":"https://github.com/vriad/zod#readme","bugs":{"url":"https://gith...
```

## Module: ./.npm/_cacache/content-v2/sha512/ac/1c/7865a5ac22a0bb027fcfbce2f71d4397d8847e951d782302ffd6e7dc65b329403a8408bddfe2410655ebc3a9e60ba4322b2930e6d32a039078654b548e94
```
{"_id":"data-uri-to-buffer","_rev":"29-c5a183076097a5c40a95b5e4ff187602","name":"data-uri-to-buffer","description":"Create an ArrayBuffer instance from a Data URI string","dist-tags":{"latest":"6.0.2"},"versions":{"0.0.1":{"name":"data-uri-to-buffer","version":"0.0.1","description":"Generate a Buffer instance from a Data URI string","main":"index.js","directories":{"test":"test"},"scripts":{"test":"mocha --reporter spec"},"repository":{"type":"git","url":"git://github.com/TooTallNate/node-data-u...
```

## Module: ./.npm/_cacache/content-v2/sha512/b0/f5/38b95edd625bed589c70c311c3d0fba285536213b4f201b439496c43081f66518bce82ba103b061040e28f27c0886c4fb51135653a82b5502da7537818be
```
     }6';&]~z힝˄'c )UOwJU"!w[RI_&DDx*w...]_/ƾ˥w.ˋ廷^_
RVE/+/{!U+'z?E
5j/ۍhTmDomŷj߬FUZf/oZpjV՟LkfbzaIh]T
57RQ蛅l*@Ax[IZfZ`,ނrd_jdV?9&zF?-6̬Dkj7!\df8 )
% 9, w%ۢfza ]~KPo_
дY]YsX.$TUY	$V5%%VxCxu-6heCHWЋP!:2tF+ 4|lOz}5TkG{;@lK-?~\~?}\|y~ߟo/O__?a]O?|>ǟw>~fo~ſ[~c)p飥ë?_>7?|z7O珖O?'%,~}X}g+ONo~_e?Zɾ>~oo~QhQ~r?,N_~yˏ?@O?|O?C-<TсX>(P @)GYwg o?ߋ5~bK8HV쉣K=W_Aښ.hӻ·߸2}W޶LKR~*'tW/}{uq<o^}...
```

## Module: ./.npm/_cacache/content-v2/sha512/b1/34/9f063a17069f3d26f20a21e7eac3b53608279bb1cef892263a6b0886a202ada1219b823604fc6ffe97db05dcc5853cd73d21ca0e0b83837ca1dfc459a9d2
```
     <vڸ?:k=!NiBE̝EsaˠH>)'kK6@LӋm-iɈ*CU=yujVUdnruD*?qPB&'k#r
PqBWr_{~xqRldmloD*Es:g&(>+孛nշXOp9oLs4&#k@@B{bX8׀AN+ed2!4W}c5	<wZ)
0D(뀡T9kt"ZW[/^^c\}8dZ֞1lz}C}:I&aLc:(&\QAL) 1GJ Sh,1TqG@1 E.ILpcDQ|%Q/`!r)F}Y\25J3iqF(C	K9 _ZJ@"iQYYT%Ðq|Eب
YD=J"IDĨ\:
GhPHbXLk¤$1grL5/@
# x P\j>Cdòc
d(.<^.O5c0YP'FR	wSMǲ-8쵠}Go>>v{҇ߛ^o~mwϣ^=/Bwx'}tp~djػVo7_?֛v4t{Єf;9lw=nAnykw޶޵:}t[Ӈ!'n僽ۃ>t[cx݂va˰{"75߶4VYfZ؄h{ͽ~^{Uf}...
```

## Module: ./.npm/_cacache/content-v2/sha512/b2/52/dd15ac5027d025460fa1c36f22893b46bd28403a038a5dc0f417dd6751c45888e32e4bd64162371d3594575bd1b9250e75d46453754cb5cd05590e927ee3
```
     }k[HpWTgt@.Ӱ̬0Nin=lvȒ[$s^*2RթSN{M'v{qiϞ<!v{9ag'j{*LO~h0vM^tiO|`מ/FI<	
rYZ:8H HMh'~a%F~rN$]	M8"q?(ΉOz)>#(HIe~B
 3:$x0(3,iJو1.wQ<HB,	G :>KYL)m 
2OqZi?Q?hـyℤ4$)*
>fE)<cs&At6M Qf4?AOY%LmG fn,-(Ź,0tLԪWCҧatHt>(Lǳ\Z:y%/N~wL~twH;&Z;yuy'o%wã198Z;
$oN	N;^:u^y'voww}88"9Nz79|stxp%?8uOOH	9~PKޛWG =|uB^tv.j-z]Uh	1ﯺ94:'G^ANN䧿
!/K΃ФwY/jb+;$;]o>)ͥ\?~'k
 1}gy?ux(9K1Qxo;ǃO4.REhQ2Rҕ^e+aQ$d+Q+...
```

## Module: ./.npm/_cacache/content-v2/sha512/b3/37/93e93f081f1b52eaeea513a0d2047eb67c9867c0cfd0c50715fa684257899895194977f387b0cf247f1a55c95619796aae5c2ccd16a941242e1fd3923d51
```
{"_id":"http-errors","_rev":"102-a5ccaf95802a37db050c23518f932893","name":"http-errors","dist-tags":{"latest":"2.0.1"},"versions":{"0.0.1":{"name":"http-errors","version":"0.0.1","keywords":["util","errors","http"],"author":{"url":"Egesté","name":"Steve","email":"npm@egeste.net"},"_id":"http-errors@0.0.1","maintainers":[{"name":"egeste","email":"npm@egeste.net"}],"url":"https://github.com/egeste/http-errors","dist":{"shasum":"caa1ff00ef680ee6cef845d4dd5e23aecc2617e0","tarball":"https://registry....
```

## Module: ./.npm/_cacache/content-v2/sha512/b9/56/167f35417bf11731609680f2aa0beca7bcb3ba6074475ffa8413c32af0d790c8399245ad0c71b685a088fd45171ddeb59e81665ef88031b37afacdfea8f7
```
{"_id":"gopd","_rev":"5-00039d9c1c4528d08bf80575c3d614b1","name":"gopd","dist-tags":{"latest":"1.2.0"},"versions":{"1.0.1":{"name":"gopd","version":"1.0.1","keywords":["ecmascript","javascript","getownpropertydescriptor","property","descriptor"],"author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"gopd@1.0.1","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/ljharb/gopd#readme","bugs":{"url":"https://github.com/ljharb/gopd...
```

## Module: ./.npm/_cacache/content-v2/sha512/ba/87/1d601e8fc0d3534f3cfe4a7c93e094c6a87064e8034be58274b369cb6eaa81cb10d0c2512702754c553574d790254507289530cdcb2ba18b42f1cc8c8741
```
{"_id":"setprototypeof","_rev":"17-588553621efc16fdd88f4319ebd8f3b6","name":"setprototypeof","description":"A small polyfill for Object.setprototypeof","dist-tags":{"latest":"1.2.0"},"versions":{"1.0.0":{"name":"setprototypeof","version":"1.0.0","description":"A small polyfill for Object.setprototypeof","main":"index.js","scripts":{"test":"echo \"Error: no test specified\" && exit 1"},"repository":{"type":"git","url":"https://github.com/wesleytodd/setprototypeof.git"},"keywords":["polyfill","obj...
```

## Module: ./.npm/_cacache/content-v2/sha512/c6/2f/51a634f454060024c57d0b3d37cc5553daf51d185c7261beddb30762da7e236c51218c5db531b0290c72813c4a96dc1e5170c1c251730d48e72946eaea09
```
{"_id":"inherits","_rev":"97-53ea97dee2e9541a65b649ecb349a05d","name":"inherits","description":"Browser-friendly inheritance fully compatible with standard node.js inherits()","dist-tags":{"latest":"2.0.4"},"versions":{"1.0.0":{"name":"inherits","description":"A tiny simple way to do classic inheritance in js","version":"1.0.0","keywords":["inheritance","class","klass","oop","object-oriented"],"main":"./inherits.js","repository":{"type":"git","url":"git://github.com/isaacs/inherits.git"},"author...
```

## Module: ./.npm/_cacache/content-v2/sha512/c9/45/069b0d0bb095bc66fbbe72d800607393cae27a2c706674a4fcf2800e296008c28fc45af6881be928befc9ce90ac4223ae18c1100fb56232933981d957bf8
```
{"_id":"hasown","_rev":"11-a074973674b38963c608b6224deaaf66","name":"hasown","description":"A robust, ES3 compatible, \"has own property\" predicate.","dist-tags":{"latest":"2.0.2"},"versions":{"1.0.1":{"name":"hasown","version":"1.0.1","description":"JavaScript curried hasOwn helper","main":"index.js","scripts":{"test":"make test","test-w":"make test-w","test-debug":"mocha --debug-brk"},"devDependencies":{"mocha":"~1.21.0","should":"~4.0.4"},"repository":{"type":"git","url":"git://github.com/ra...
```

## Module: ./.npm/_cacache/content-v2/sha512/c9/a6/84ff18a003077a9cb20cb3a542f8cda23c689e247fd26ec7ef5645c0c19f44c6be59d718f54077cf176c33f363b716098c57a827780409e4695d2a131816
```
{"_id":"has-symbols","_rev":"11-be2020b00b7958b01a41a76a09e5b397","name":"has-symbols","dist-tags":{"latest":"1.1.0"},"versions":{"1.0.0":{"name":"has-symbols","version":"1.0.0","keywords":["Symbol","symbols","typeof","sham","polyfill","native","core-js","ES6"],"author":{"url":"http://ljharb.codes","name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"has-symbols@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"contributors":[{"url":"http://ljharb.codes",...
```

## Module: ./.npm/_cacache/content-v2/sha512/ca/8b/5db2dd3f9bc534d9fdf138a84b86495af76c312f065fbff300503e9c4fdf8770f7aac92f92b1f11600ae755d0842053762fcbc5bdd8b74c5f8cf49ef3708
```
{"_id":"call-bind-apply-helpers","_rev":"2-56963b9eaf7a0f6cfb8657f38a8b4b46","name":"call-bind-apply-helpers","dist-tags":{"latest":"1.0.2"},"versions":{"1.0.0":{"name":"call-bind-apply-helpers","version":"1.0.0","author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"call-bind-apply-helpers@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/ljharb/call-bind-apply-helpers#readme","bugs":{"url":"https://github.com/ljharb...
```

## Module: ./.npm/_cacache/content-v2/sha512/cc/04/bc93fa5f1731a368286f4894a3eb4ba17263ba31f4fa3633aa9b9baa76bc44c3c61adeace2911c89d8da616e7d221a7e0c16f874cff11a275c45018b7ee9
```
{"_id":"asynckit","_rev":"8-a9ce4a5d61bb17e1fec505a12b233356","name":"asynckit","dist-tags":{"latest":"0.5.0"},"versions":{"0.1.0":{"name":"asynckit","version":"0.1.0","keywords":["async","jobs","parallel","serial","iterator","array","object"],"author":{"name":"Alex Indigo","email":"iam@alexindigo.com"},"license":"MIT","_id":"asynckit@0.1.0","maintainers":[{"name":"alexindigo","email":"iam@alexindigo.com"}],"homepage":"https://github.com/alexindigo/asynckit#readme","bugs":{"url":"https://github....
```

## Module: ./.npm/_cacache/content-v2/sha512/d1/1f/629116faebc1c1ed00f14f5be4a6e501b6a739dd8c80c0cc0679414a4688d8fcd58abdd67ef5462d45f1a686a35b4644d256931b9b28578a9145bf671bfc
```
     v62W J	MפVh'Hr> 	o%!;n.N4v2	> в[Z918~mVdU?g0[ݭ3<<V;hY
r߿H<y'K,cbA}6h@4۔#lJĹ>Y"]f3`6")"#{,r51L Y@='
)>=|׋@#b	gCױᵢa126si
Iaث81866KKҿ
EAT.q(1F0V
)ȕ[oaSR䤊k'p+B:>y/jnerя+85t$g.=,X$?]5lx }9QY*_:rIM`d}{~}Yy;"q%D.h^z^DƜ(%gØ{byGͱqKKR)Z1݆αƴ@"GrշX9w0s]G1 
 eE+oIs?aSx4HT>/	Jyl),IR^Q"mA}2}Q]js`9H
Wcu7]dzfkDOcDe1io]5L{|q8"4(pFt{bǏCɋP%r%J9YMPԷt$7(`'0mx?H #%+NN 
iy>r!lgŒ/^
2SS6r7P].xF
P!1)Sl\| "ן|#hR)<2I ;)Ɇ!]jq...
```

## Module: ./.npm/_cacache/content-v2/sha512/d2/12/54f5208fbe633320175916a34f5d66ba76a87b59d1f470823dcbe0b24bcac6de72f8f01725adaf4798a8555541f23d6347e58ef10f0001edb7e04a391431
```
     ;s6+:Γ(~:b+.u
$OII3~aX `lmE20\ǁi#4MÂGƣx
!Y04ֿms. O@4}|bhjjvϟ^߶awx=
-_bΖ8B\b8yC'EN+{!x8'8JIϥ7!S@o4,R_F<U@KwYm
EHX٤7B6]?g߰n?v4T:+	Ok{,
<yBaDBD<H
saTbЄ0Gb 92O{Ei.ϳk W CyrT܏ 6	<+YE8PBd@mu\Er	9
G*4!J)us%Q%ȕ-&9J&$<BEխHD
6APIhƱ,BAee"AOn$ZXi$Vh+Kz_Q|
6[!0_K9)_[
@ժIX0(՝Rh ywS״!M^~L0:w	4g0:k4~L''x34aó3LwIF'+x~NGoG	&@+V1{;g짦r4ϗ)`:?LOƣhjv80x(m~z2%xgba)jFop2x;x5TTT#R;@$o0l4S7'tp<kl2I...
```

## Module: ./.npm/_cacache/content-v2/sha512/d5/c0/cd77027625aa2199bdec8383a629a301c2e0b8f2c6278b91d4c360efb02f0b8c64cb2bd87e79bd57e91cae3877b8853d142c25baf22a26863528294aa53d
```
     }w۶oZ޵mJ@/dﺉxβ[1HIqg
@Jeَvܞk}%3Nz/wYU>RpNz<?+3iY+J?A%)dOYyKb
Ngc+tK6BntX\JT0*{(z4]rvo3l|8b, Ul:P jQ"iOcd+::_=}ϤٍC#?n\_F῱T~	0LĨ4)LfUǢ+l&\Tˀ}ٌ
jq4̿}bdwC4?)y*Jt^䓛"+vKY@Zd(tqZi$C(@ސA!
t$ @T9
@Qe%,DOn:yBaZ2O+Q &,s
4ѹ""#(v5yRSlB4Q'5I*"U*%iehG8K@rSSdZB%\	STr%:ErZA()a4|BIL]ҙ<(Z**0/$-;ɴrFM@U'h_aTkTv:C B`b7˫TYu[N*b4"j&iFD:_V"R1"t:Wӟ	y{|σ/	98쒟N_tJ~;>;<@!88|%xw޼}}K_N)y}t%9="X``?~jtt;?"yw|z{OoNKrxtxpoOrpH...
```

## Module: ./.npm/_cacache/content-v2/sha512/d6/ba/56acfd6adfd6c6530f2cd14ef6bd60e7d01c424c7665fa0c747ba4ef2bd5bd0f3c4ae426e096445266b289a65b8ff67c1a3aebe5b9fd23dd52ca8167ce20
```
{"_id":"get-proto","_rev":"1-fb55047c66343413eea8b52de307da9f","name":"get-proto","dist-tags":{"latest":"1.0.1"},"versions":{"1.0.0":{"name":"get-proto","version":"1.0.0","keywords":["get","proto","prototype","getPrototypeOf","[[Prototype]]"],"author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"get-proto@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/ljharb/get-proto#readme","bugs":{"url":"https://github.com/ljha...
```

## Module: ./.npm/_cacache/content-v2/sha512/d7/c9/a1e38b8fea15d4c0a365cc03107d6cacb577c99fa1ce816893a01f5bc0faf3196191c9287571ed396565ec6af665262a3a02e97c8e9d43ded175e55eb657
```
{"_id":"es-define-property","_rev":"1-a657896e70009de2081c1ca06b9a0f64","name":"es-define-property","dist-tags":{"latest":"1.0.1"},"versions":{"1.0.0":{"name":"es-define-property","version":"1.0.0","keywords":["javascript","ecmascript","object","define","property","defineProperty","Object.defineProperty"],"author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"es-define-property@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://g...
```

## Module: ./.npm/_cacache/content-v2/sha512/dc/51/8c065a25f5fedde32ad0e8a6e4480efb8f55410fbd3ec09d0c174cbf68a5a3e5697580b4f32a155d9bbbaf24f4a03788acf608a444baf364885f2780b2d9
```
{"_id":"combined-stream","_rev":"45-8071877f56d51159c12935cada0a84d7","name":"combined-stream","description":"A stream that emits multiple other streams one after another.","dist-tags":{"latest":"1.0.8","next":"1.0.6-rc1"},"versions":{"0.0.0":{"author":{"name":"Felix Geisendörfer","email":"felix@debuggable.com","url":"http://debuggable.com/"},"name":"combined-stream","description":"A stream that emits multiple other streams one after another.","version":"0.0.0","homepage":"https://github.com/fel...
```

## Module: ./.npm/_cacache/content-v2/sha512/e0/56/d17405fe6d2766a3801416e4b458d88fcfc36016dfabf138603569a5ae3423b7543b651f7ecd395c7b6f39f71e0a497af022c69e4ea0e82909ad3fca4b99
```
     <s6b㾫V(rR_VDl#+븙
&!		E h[N?@;o]\4	.vb`JdF[g?>lj^ h}"h6||	~TD|AA "?o<p>i")];R\A=܅Nއ	QsE2Of1B,/ֻ	f1p<L*ΩY,yf?JjΒ>i$%&%	0	s*f$F
JO!1
PH
oa	Kf@ SPs&A#I" RE#x-hBzSS	u5se{j"%w+cj3J%X80"!L҆)O&frހ!LHlԓq Iyʨ=֒;
(PeE$nՑ0M309OArM
 1á<HzZ
z,FXhĭ' -gվspCh,)@RD1Cʅ:LƯpuq:7
.G?
N'ӻN~__ϽѨ7OQ
.Fl?i`x|d0|/ߌax1`? AjпBdp{98ixq^xp77ˋ>'0U?0?cz;;CR^_FW?}8^
/p|7w{׽.Ư#w>6!zq|1z/Fσ~z
ttqP2ba`AQCeF.FU@'`
Zϒ'5|...
```

## Module: ./.npm/_cacache/content-v2/sha512/e1/71/f77479e68534ec1a2b93d8fc47c7a1399a534f50e98fda4e5c47d2d7210a51a869c271f2732f74df3aba4c3cbc0a5e2d47cc03390b056afb8d95767b0a3c
```
{"_id":"node-fetch","_rev":"354-1674ab6986e1950f61b479e91269e4ee","name":"node-fetch","description":"A light-weight module that brings Fetch API to node.js","dist-tags":{"latest":"3.3.2","next":"3.0.0-beta.10","cjs":"2.6.7","beta":"4.0.0-beta.4","release-2.x":"2.7.0"},"versions":{"0.1.0":{"name":"node-fetch","version":"0.1.0","description":"A light-weight module that brings window.fetch to node.js","main":"index.js","scripts":{"test":"mocha test/test.js"},"repository":{"type":"git","url":"https:...
```

## Module: ./.npm/_cacache/content-v2/sha512/e5/31/40b34ba2216870b47d1233b97640069129254e43e43f590b47dac5d9dd1bed96acfe6867de306d30e33f385faec886ecbb5cdfc7a09c3069df101a2dc370
```
{"_id":"dunder-proto","_rev":"1-8990e995311508d36bd7745acfe3fa2d","name":"dunder-proto","dist-tags":{"latest":"1.0.1"},"versions":{"1.0.0":{"name":"dunder-proto","version":"1.0.0","author":{"name":"Jordan Harband","email":"ljharb@gmail.com"},"license":"MIT","_id":"dunder-proto@1.0.0","maintainers":[{"name":"ljharb","email":"ljharb@gmail.com"}],"homepage":"https://github.com/es-shims/dunder-proto#readme","bugs":{"url":"https://github.com/es-shims/dunder-proto/issues"},"dist":{"shasum":"c2fce098b3...
```

## Module: ./.npm/_cacache/content-v2/sha512/ed/71/cdc47eea5fdc46e66230c6486e993a31fcc21135c3a00ebc56b0cb76a40af6dd61e9e8cad194dec50521690a9afea153b417be38894811f369c931f1b648
```
     }rvWh")CRae͌6dSZoR$ݔuUnU{-{)9@7٤([8X3888wRU9&U!~,
<O7/\?l;,|_3++^ߟ/7<6~C&ĭEF:`+qM.ӣl"Մj<w{MD=G]k~"sQ}fڨTY7}}. jT*'
#(PVE&4+?hcimZ?;j<]7^lkn1,S2GOM .q5erP]ee6NT<h?'7'	-&pK?JwAa)IyQqC5(g1/n6L_߫j<oKb2
Att.mB=}Nhn^-M>L+l~bx<=;ؿc-wg?UŶ6s,e'f^*YY,YV+U](+%,-byKgU!YT< +`	CI=/
K2d23r mUWmۺM=kYu*V(QGeCx"/{tq.*ݭ,eUɌNfntS	Q;yJ5PCu_2Z"*|ܓ쥳b&9D[|DEwxF{'2ӮIwG<O}1:+jX.F~T^!DC٤G<dRe|(P{݄Ɯ}N=;<eNp9;5Ͼ?~}Pdٟ...
```

## Module: ./.npm/_cacache/content-v2/sha512/ef/20/10a43d94309ccb8b50eabfba856273db68fc7b65f14ae8f888c50e0f7e418fc8dca5d94831f9afee994a2798aaa384ce039df6ccbdd5faa2d5eaf37b2841
```
     =z6O8URFkR'NJoLz*,&!(+}}}=)qSwk}b	܁=w)~OڄͭVV[k[[OK $#ALt:	.5ZZyWA_Id(đD%ԥ_DJ?KYi,ZeCK 
K	qe:0*S/и/<b? d$KqAJ%PScF:A$TiI*$F]NQG4y Љ u1 Jx5~{
*q8JcGm1.hHat3	3$)O?%?H?l>088#8gP+IsὍPep*5P^0׳pp4B1<MGoET+{.w;dqF 9ܫOOщ98ﴡsz^;
wّ5NO^:Λ!|st"vYq
}><saT(qvwrv'x}tI绷g^
_Wm
&zsP{ߵ@9qc'޿mc>4^:,sڮݓ).ț	=;l3\jQhߝ3bN3N4v?=|}Z+Hu}5'W77}|OLQ"ON)6_WT?&1~GA|>Hqw3/I늪T*:g[숭-	zyDz}SqѻQܗLͩu...
```

## Module: ./.npm/_cacache/content-v2/sha512/f0/de/376d0c3d325501d298936472b624c87c9183cac47e7b77867b59bf0f4b86f2d8c919d05cc8e713c89a0df1ba6a5ebfcd95670d95587409249629f9693013
```
     }[{8`?WRDL+8s98ۙٳ
Eʱ  	R,;I!k]P(
U~"EiGq#&[o[խ'?)_>LZIcrM2ј4D^I#)81e"N*9Nύ(Mc? 61ۼWf8]vؘZWzDU}d(1r	VPM':qA!
#bv?~i?)sȸُ1rl	?FZSxHǌDD\aghvoЅn!fI}kq	gU[X:4N}MT_$lylHA, ɼWQ-
hȋi O6faL3D*tP:gsٗϫ"$O̯o#ʙD`dԏ<:Dz=:YѸp](7Gw=Ά7b1ܐwP.XKhY<!6VL7KcwDZ?[pa`HZ?fG6gD3L܍G(&C?rLBZ1GV ++n̏4b']C^!rA	94ِlSUe]3i Ϙţf'~yWQ* :1iFZ溸)V!b&;]7zI,8
gYA9,$apX*)Jn5e+R(ĔFAS͡S6,Ctp(Fp}ﾚ`3+l@b>eK[?<|?(~ߌjz<u<>	fNUo|J~}8"'Ap:>cV:0E...
```

## Module: ./.npm/_cacache/content-v2/sha512/f1/18/a944ba25dfb6cdb366e1a15ebb7e24c4bdd4eb6cc5187054e2cb7fb0bae3a75288364011c26565c34628d641f0248418f651fe549d56a25b0039bdd77cdb
```
     vǵ g|Ee Pl")}(Rۋ1
X"c{V<[|@ϟȪ,H1KD 3w\vر4gj]!$v=GLEXĪ_ //~Uכ
&<jm}qWG"0~.,1Q..k+k}[UߴAuhꮫEUweh.Z?bB]"T}Sum,^ԋTY^eU]
GuM|
a硫PyU ^|0^TrxWfWmvIU/|ay}U. <;fW]8IC=_G7-Wv^w'pRu0mYV]:ty񥏠% /hj{.uwPUː|SuMzxf>o\5LwpPͻIb8Oܬmy] -^TlQzk3Mz9'ի_×O_<<|U=}u_u/_>|Ջ/PO'O^^<~OTO?zW}ճ_=}qE건+h'/}뇟?}N/~~eO}o^~Փϟ>{ՓgՓ{uˇϞA_o^%z?|/_W_xWOgO~IG>z𫇿{^˃]`/3O_<<zˇ^T_|WON/|W' In,/^ydbgOU"~?ϲڞٶy߅v]S~'pՅ*~~]n^/ӰxW~}vp<A_/CՃ&3oҳM{Wy~rgc^ɛ9G?eT[δգ֋_...
```

## Module: ./.npm/_cacache/content-v2/sha512/f3/3f/5f545883735913820f7b9388c4bb8f5506d3a5342991621e9eb2d29c70ead7e24ed11fd239488463723f922bd375fd8cb1aeaf5d0118c7475cb516a11090
```
{"_id":"fetch-blob","_rev":"30-98e0558b27a68f35fb1d4d542781d5c2","name":"fetch-blob","dist-tags":{"latest":"4.0.0","RC":"3.0.0-rc.0"},"versions":{"1.0.2":{"name":"fetch-blob","version":"1.0.2","description":"A Blob implementation on node.js, originally from node-fetch","main":"index.js","scripts":{"test":"ava","report":"nyc ava","coverage":"nyc --reporter json --reporter text ava && codecov -f coverage/coverage-final.json"},"repository":{"type":"git","url":"git+https://github.com/bitinn/fetch-bl...
```

## Module: ./.npm/_cacache/content-v2/sha512/f5/f4/a349aa2cfdf448548a7ec5226513a95fc21112ecb36d29a08121a987b23af69dad418800493e8d263a38f3f062435116ab9823c6a9a89583999f8dbf7c09
```
     }v7QPJH-WeGsmGRfvdnNwS$+gO 'd9'bUP(
`A2QRdw?0\F}a`,50v]F30~˼ Wa;YȖb4OHx{v-iF2ғCή
C~)WR:Y4N)󲤗qJ
g=D!6[Ƣ$ 2aD1N8J!2da,/b)*$7o]#K88Nq{-e	l%
3X$bVɧ1""J]Z`\W@y3:=/H!")4dIXWp `Mf@Y:q^u$xN'9Y]Pf+STs"".+y5فf
#	ȋof@Q㘑EYPT
~ͿE;OQVWg}'q\+]6ØX'SPXY!2T|NwVcS&RO,^runEY*:_;_>?98pV?[{sz^GL$,
piI'%	މly&(LdޡiFB
3!P"6#TP"ܡ4A)-HD 
Q1rad#)H!8)[BrB@{L/ă(AWfQ1KD^dF(J@ev#]"E\$#4Oy_!X8g## MeCir."#Yך;	/AD9|vM|.$gB,'
H0҄G...
```

## Module: ./.npm/_cacache/content-v2/sha512/fb/d4/605fc98bc84a453b52ab7f613b8919879d138309a9dba1e29b315bb7d41b05c5f589e83817a96311f7c6e23cb95cace6594c621241b3c8f4017557bef439
```
{"name":"@modelcontextprotocol/sdk","dist-tags":{"latest":"1.27.0"},"versions":{"0.4.0":{"name":"@modelcontextprotocol/sdk","version":"0.4.0","dependencies":{"zod":"^3.23.8","raw-body":"^3.0.0","content-type":"^1.0.5"},"devDependencies":{"ws":"^8.18.0","tsx":"^4.16.5","jest":"^29.7.0","eslint":"^9.8.0","express":"^4.19.2","ts-jest":"^29.2.4","@types/ws":"^8.5.12","@eslint/js":"^9.8.0","typescript":"^5.5.4","@types/jest":"^29.5.12","@types/node":"^22.0.2","eventsource":"^2.0.2","@types/express":"...
```

## Module: ./.npm/_cacache/content-v2/sha512/fc/56/43434c60b8e06ec225be7d14500463926b84455c5290ade1d01dc700dea00d2ff56680a3eb6ee73aec70f05aef59c19b480c38b2a9a52af2b5005ecae6ae
```
{"_id":"has-tostringtag","_rev":"3-e000ca38bc06031d385168717b376307","name":"has-tostringtag","dist-tags":{"latest":"1.0.2"},"versions":{"1.0.0":{"name":"has-tostringtag","version":"1.0.0","author":{"name":"Jordan Harband","email":"ljharb@gmail.com","url":"http://ljharb.codes"},"funding":{"url":"https://github.com/sponsors/ljharb"},"contributors":[{"name":"Jordan Harband","email":"ljharb@gmail.com","url":"http://ljharb.codes"}],"description":"Determine if the JS environment has `Symbol.toStringT...
```

## Module: ./.npm/_cacache/content-v2/sha512/fc/85/ed6f0124e474cfc84c32297ea11a4617c4cf676e3eb807e8a55499c2fd1e81d291f91b85776f4a556cbec3063e2d921040a696d05257fa17a5e5f4b1eed6
```
     ]yw۶Ͽ槸U:V-Rv9M[Vs[izj%&GP^%}H(98^2"|b'Z(w/'j4 /z	O͖nހ'azOOt>RuH>V)`,,AiEQJ*K{P}7%$K1VD
K՛n鬂LԛSl$B=zȢέIIaFw1	5}FTh*$wGcE<)upJ_[2ZQ.׃:&8U}_dY^k@u?33sypҀa/VR`6SLhBĻy!q<Ǜ 
!:8KP sf:$X̜Ϩ4`;.N)N"RYDbQ*HIpS6!<uTLwnab̜(9ӊHgfrlKgi,U! @*SUL;E&
,r9e8\)2Dh0m?d()2fT|,`)[(ՈħuaL8=:"e'G/F087G
PTWGoG{7G/79T_o''pt^9*0=_¯oG0<`?`A
G_`4D/ozǣ1y{eu8`0GpwxQ)WGǘ>?z::<}8~=˨ao׽}!u4z...
```

## Module: ./.npm/_cacache/content-v2/sha512/fc/d7/fb4f2cd3c7a4b7c9124e6ce015efde7aafc72bdbe3a3f000b976df3048fdc1400a1e5f9f0da07c8253c3fccc690d5d2b634d28ba7f33ba174a4175c61b12
```
     ;rrk7L uZ^(kRQS!		 Y$?S>(  xYr֧岀LtCӺ3Ǵ~9jw?adY;<ͦ ?lpFh$,6#?@HxHSO(9əcQъ,rƓ
imn05g$#ķ;	Gm-E;G3fO~>yTWM0CF&4GSJF$kbFcZ%q@LFB!`c$FxdX0fD&&c@؁xԏ2R'T+]IR3j.2uI$,iTrǠ]s$D`H4a JvFrd:lRlI6Y ".Rp`\lth!*4*|T4J"XR8[jHG
KvP"ih20\1~PplVe0!Մ/̉!{X~ bM.N[6\ŇqZW]>^D.NHtZ_/{+r#˳NJ:ݣǝ[rxXX@A$iމvgsN4Oh\zV\]^\1v'=>owBiru:;Za=>O>98;nCaF:<kVOYs^%ǭ6Ǻ *=&G͛_;]E߃ϪֿSԏvz+TIȣ:n[PAU㨵tF xrn+DO3PǷ}Y{<$YL|]_؟)lkZ	Fꛛ....
```

## Module: ./.npm/_cacache/content-v2/sha512/fe/32/99a0ca70d05f06470978fde2d138f03771f717b4b0293f44332e6513fc7b8f0995b207b218f59acc78ac363bf9c522a3d00773d533d6989b4177d760170d
```
     ]{sHjs$^JI-oسxV"H&V}b3Xz*h{^_whbZ_!+7wVxERU^ª|LeÓJjZb9US˺!E<4l$&X'ك}bgOf365g
B*!a֟00? kdCVӛ+t<&XJpǸaaL}1Qؾ7p\!IܦTb3Uĵ%:ȏB2
x٢
ˮ3v
?WPhı3$v~b&r %? \WA	[uhDh9ӑ?^ÕAx:C&5~fV(rDTt==/̾d_7ALdVK|d.Y2`Lu';^.L@;"k@{a{s؅\sxm Kt{hAlct(̓yn+lcVpW2
A(LD5v`tvvs{_P@^shсãak]j:80Z"j<0~}#;o{𶽿k`涁-kl*~yPAWCj"ŭwo
%5Nnn[~,`/;EwͮQFi1X-`KC
K3E磮FceuEeyJB?f_?
WkeVW<;e_*:1/z_UgF󿖄o8`:\oO,1/,f|cSQ~t{p&؄...
```

## Module: ./.npm/_cacache/index-v5/00/60/6a2298196c9cd65881a7267db2824adff4d9c24f0ed6d3a2ca4c81d3e235
```

11bc78857b10ec8cf6619b94baebd7d4bd378123	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz","integrity":"sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g==","time":1771959187511,"size":4431,"metadata":{"time":1771959187264,"url":"https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557...
```

## Module: ./.npm/_cacache/index-v5/04/5a/2b5d7a7c407d85d746baa0f5c9388a333e35a717a8a0a81943daa6cb1364
```

a252a8b9352cd48ef08256eb1ef8c2a5992082b0	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/zod","integrity":"sha512-qdrMgP30z1d18IoLrRMKpBS116xtUVI5EnEDt1wXiCOklWDQjCslXJeiJJdehP8evfWii6PXiMrU5Z4f8kNqmg==","time":1771959185135,"size":3489329,"metadata":{"time":1771959184967,"url":"https://registry.npmjs.org/zod","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"Tue, ...
```

## Module: ./.npm/_cacache/index-v5/06/4b/6c1d4325f34a83acf333ab8a7d0e98a29bb01013836bc053b0634e1e8d0e
```

9506dcc5b81a94a36c6f01ff34d1e42f8fe7e804	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/gopd","integrity":"sha512-uVYWfzVBe/EXMWCWgPKqC+ynvLO6YHRHX/qEE8Mq8NeQyDmSRa0McbaFoIj9RRcd3rWegWZe+IAxs3r6zf6o9w==","time":1771959186416,"size":11458,"metadata":{"time":1771959186387,"url":"https://registry.npmjs.org/gopd","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"Tue, ...
```

## Module: ./.npm/_cacache/index-v5/0b/bf/4226971e16d707d9180cd9fe4d4c5d07b40fa7d4311fe932f69a7fce4e53
```

85620e4004d261946a6aa5321249fe52a61886ad	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/unpipe/-/unpipe-1.0.0.tgz","integrity":"sha512-pjy2bYhSsufwWlKwPc+l3cN7+wuJlK6uz0YdJEOlQDbl6jo/YlPi4mb8agUkVC8BF7V8NuzeyPNqRksA3hztKQ==","time":1771959187585,"size":2096,"metadata":{"time":1771959187307,"url":"https://registry.npmjs.org/unpipe/-/unpipe-1.0.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","...
```

## Module: ./.npm/_cacache/index-v5/11/e1/1c483d2122bd9cb1fa851dc036984e3754849f699fe4eca57537ef5d33ee
```

a205949f95a177a0bdc51085e3f68893af91038b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/unpipe","integrity":"sha512-gY2qDpwjCK/KP5yJmYRxyp5VaQT/WPK2JMSDcSKS48gevKQlYaqUcA9ZOKi+EfB/oivtkBYopDG0Tl+DF78nTw==","time":1771959185994,"size":3609,"metadata":{"time":1771959185980,"url":"https://registry.npmjs.org/unpipe","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"Tu...
```

## Module: ./.npm/_cacache/index-v5/12/ad/2e4b9bede85539a905759e778f29d254cc59f18f1152b470275947579336
```

0a4d058dfa54a7e16735d6aab4392ba18092c2bf	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/zod-to-json-schema/-/zod-to-json-schema-3.25.1.tgz","integrity":"sha512-pM/SU9d3YAggzi6MtR4h7ruuQlqKtad8e9S0fmxcMi+ueAK5Korys/aWcV9LIIHTVbj01NdzxcnXSN+O74ZIVA==","time":1771959188177,"size":46288,"metadata":{"time":1771959187416,"url":"https://registry.npmjs.org/zod-to-json-schema/-/zod-to-json-schema-3.25.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31...
```

## Module: ./.npm/_cacache/index-v5/13/29/572bf43d686299dd8263b106410c0cdb26df1485ef40041d2172cc942990
```

62eab97b988beb69b5dc16b4fbc333144b2e1f7d	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/content-type","integrity":"sha512-n5kB3yMv7sODGkR9slCG9Kicj+3SwbcGAulN04QmhhEQckK4r7BAWjA71iET8+bHF3XyDV5d74j6erfVYeN0sw==","time":1771959185779,"size":17311,"metadata":{"time":1771959185768,"url":"https://registry.npmjs.org/content-type","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/jso...
```

## Module: ./.npm/_cacache/index-v5/18/55/9c21c8d8605592da1a2d8ad777878425c65933e52599a58e642960dce2e5
```

54e180b784d65c89274568e6e22d556629154a3e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/hasown/-/hasown-2.0.2.tgz","integrity":"sha512-0hJU9SCPvmMzIBdZFqNPXWa6dqh7WdH0cII9y+CyS8rG3nL48Bclra9HmKhVVUHyPWNH5Y7xDwAB7bfgSjkUMQ==","time":1771959187645,"size":4109,"metadata":{"time":1771959187390,"url":"https://registry.npmjs.org/hasown/-/hasown-2.0.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","...
```

## Module: ./.npm/_cacache/index-v5/22/a8/17a65455627968eb0c799e9d7bec1167928dbfbb59cb25cb25e68be37879
```

6c7cdaeff3003d23249d9ee11ebc9c625053f3ea	{"key":"security-advisory:@modelcontextprotocol/sdk:8yL/tqwTU2UiZS9wnCZiCzQPA88v8ktd3h/Q0nPZK+QMxHyBEptSab8FzQhZLLQYdqQZDYcytAAdymbvtSO1LA==","integrity":"sha512-D03UrjonbDdzaGFYbqsLem8t6M5nbiEx3MtYzt+SzvJi67CBmD/gISsQDa/A2EMCBgRs4yg3d08iBbvBLoc0Og==","time":1771959187782,"size":1720}...
```

## Module: ./.npm/_cacache/index-v5/24/e3/6a5b57ca4d63f37ccae38ea6b710ed659eeb763c63181c02e9470f8b29b9
```

09aed304423d462ac0800c0de25daa0448c79a2f	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz","integrity":"sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA==","time":1771959187598,"size":4658,"metadata":{"time":1771959187339,"url":"https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","conten...
```

## Module: ./.npm/_cacache/index-v5/25/7f/0b973fb10d0d62b5962532a6e5691f81dd1c20b63fcce513967941450a82
```

6ec52da4537bf117ccc865546ad2a820b00fc726	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/math-intrinsics/-/math-intrinsics-1.1.0.tgz","integrity":"sha512-/IXtbwEk5HTPyEwyKX6hGkYXxM9nbj64B+ilVJnC/R6B0pH5G4V3b0pVbL7DBj4tkhBAppbQUlf6F6Xl9LHu1g==","time":1771959187460,"size":6355,"metadata":{"time":1771959187252,"url":"https://registry.npmjs.org/math-intrinsics/-/math-intrinsics-1.1.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","conten...
```

## Module: ./.npm/_cacache/index-v5/27/b6/bc1d086124331680bbaa5c4c1b8d244d40fc2dad68e9fe8dcd4f002638ec
```

bfdb2b26609d1fff346ead9440c305e7f8a56015	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/safer-buffer","integrity":"sha512-JIII3taqQ5niG1U6KriVIN4Sjz3XWBXxplOKq1sA86yDlPxkyG5LKBvwlbndxRxdVcSCu5owg7TdPI59ICA8bw==","time":1771959186859,"size":18521,"metadata":{"time":1771959186853,"url":"https://registry.npmjs.org/safer-buffer","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/jso...
```

## Module: ./.npm/_cacache/index-v5/28/0a/a424908c0b6ac2407a089f302e5bebf9f614710c67e18e6010139b8dfe76
```

eca9d62c7ed49ac9bf00ea4fe6958f0ba18657f1	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/form-data/-/form-data-4.0.5.tgz","integrity":"sha512-8RipRLol37bNs2bhoV67fiTEvdTrbMUYcFTiy3+wuuOnUog2QBHCZWXDRijWQfAkhBj2Uf5UnVaiWwA5vdd82w==","time":1771959187768,"size":23423,"metadata":{"time":1771959187413,"url":"https://registry.npmjs.org/form-data/-/form-data-4.0.5.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/oc...
```

## Module: ./.npm/_cacache/index-v5/2e/5e/7c6ad49d70eff131acc11a5b821e3d9d46bdb106b01afd85b2b5de6b2204
```

3e702f2a47e99291c2d1470220ccd923bac88c93	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/zod/-/zod-3.25.76.tgz","integrity":"sha512-gzUt/qt81nXsFGKIFcC3YnfEAx5NkunCfnDlvuBSSFS02bcXu4Lmea0AFIUwbLWxWPx3d9p8S5QoaujKcNQxcQ==","time":1771959188626,"size":583600,"metadata":{"time":1771959187395,"url":"https://registry.npmjs.org/zod/-/zod-3.25.76.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","date":...
```

## Module: ./.npm/_cacache/index-v5/2f/b5/99a8ac8d9fe0f2ad4894aa959445cb3e3c9b6cd11883956769678b196ced
```

ebae026a4e3baf7516b44f475725ef4f6e933641	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/asynckit/-/asynckit-0.4.0.tgz","integrity":"sha512-Oei9OH4tRh0YqU3GxhX79dM/mwVgvbZJaSNaRk+bshkj0S5cfHcgYakreBjrHwatXKbz+IoIdYLxrKim2MjW0Q==","time":1771959187754,"size":8111,"metadata":{"time":1771959187369,"url":"https://registry.npmjs.org/asynckit/-/asynckit-0.4.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-s...
```

## Module: ./.npm/_cacache/index-v5/34/05/127f37b0ff3cd9c76b1497b5838d265a8a2b7ef495b7f9841f5d4665ba67
```

04e164c9e6123d73d1f013a53a3e9c20ae526301	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/formdata-polyfill/-/formdata-polyfill-4.0.10.tgz","integrity":"sha512-buewHzMvYL29jdeQTVILecSaZKnt/RJWjoZCF5OW60Z67/GmSLBkOFM7qh1PI3zFNtJbaZL5eQu1vLfazOwj4g==","time":1771959187690,"size":11359,"metadata":{"time":1771959187315,"url":"https://registry.npmjs.org/formdata-polyfill/-/formdata-polyfill-4.0.10.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=315576...
```

## Module: ./.npm/_cacache/index-v5/36/d6/0ec727dc46dd7a5b3d32487a89e6ffba1789d0a5f37a3874c6520a568849
```

0c651b8e7d2a73e4bce43ae8772add3d151df191	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/combined-stream","integrity":"sha512-3FGMBlol9f7d4yrQ6KbkSA77j1VBD70+wJ0MF0y/aKWj5Wl1gLTzKhVdm7uvJPSgN4is9gikRLrzZIhfJ4Cy2Q==","time":1771959186108,"size":40337,"metadata":{"time":1771959186086,"url":"https://registry.npmjs.org/combined-stream","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"applicati...
```

## Module: ./.npm/_cacache/index-v5/3a/ef/1f558f51da8495fa9d3fee9e4aa8c6cfc9809b10931f4df310e7bb0fe42b
```

69c695f9a9da62a8b608b58bedb64d6546b98201	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/bytes/-/bytes-3.1.2.tgz","integrity":"sha512-/Nf7TyzTx6S3yRJObOAV7956r8cr2+Oj8AC5dt8wSP3BQAoeX58NoHyCU8P8zGkNXStjTSi6fzO6F0pBdcYbEg==","time":1771959187575,"size":4496,"metadata":{"time":1771959187272,"url":"https://registry.npmjs.org/bytes/-/bytes-3.1.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","date...
```

## Module: ./.npm/_cacache/index-v5/47/54/6b45375ef86aed02210a45c62fe4d8a67e7db5524b600c1c62cc471bf67d
```

c9d9d62a2b85e09d76324d646689b139ec0a760f	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/content-type/-/content-type-1.0.5.tgz","integrity":"sha512-nTjqfcBFEipKdXCv4YDQWCfmcLZKm81ldF0pAopTvyrFGVbcR6P/VAAd5G7N+0tTr8QqiU0tFadD6FK4NtJwOA==","time":1771959187628,"size":3914,"metadata":{"time":1771959187440,"url":"https://registry.npmjs.org/content-type/-/content-type-1.0.5.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"app...
```

## Module: ./.npm/_cacache/index-v5/47/b1/bae8ec0b8218dd898af07f7ae581d4d0fe8dbeba332842ba5216e9dca32a
```

fd471453bc8ed3cd7f713f87d6d128bc4b4c9c91	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/zod-to-json-schema","integrity":"sha512-XdkIbOfqZr6KHw7hBI1N4ro66NiN07il9WyCzR7UFZddKdsCMjWhx23io7T2xbKM1T3YbYLsBFEoMltyXyPaDQ==","time":1771959185136,"size":301404,"metadata":{"time":1771959185091,"url":"https://registry.npmjs.org/zod-to-json-schema","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"ap...
```

## Module: ./.npm/_cacache/index-v5/4b/d1/8dbc4e0b64b8fb463d5e13adde7c8132cd76a73eff69294c0995200f1016
```

559417e8840a402725dc1d7e0dc7048a0d2b7ed9	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@types/node/-/node-22.19.11.tgz","integrity":"sha512-BH7YwL6rA93ReqeQS1c4bsPpcfOmJasG+Fkr6Y59q83f9M1WcBRHR2vM+P9eOisYRcN3ujQoiZY8uk5W+1WL8w==","time":1771959188037,"size":444893,"metadata":{"time":1771959187445,"url":"https://registry.npmjs.org/@types/node/-/node-22.19.11.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, must-revalidate, max-age=31557600","content-type":"applica...
```

## Module: ./.npm/_cacache/index-v5/4c/74/a2b741aec6bd4dd94223969fdf1afbd63e8b8cbafb7cd5d5029acb3181e1
```

cff0569f6cb94191cc6722b03d4792dcd3a846e6	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/combined-stream/-/combined-stream-1.0.8.tgz","integrity":"sha512-FQN4MRfuJeHf7cBbBMJFXhKSDq+2kAArBlmRBvcvFE5BB1HZKXtSFASDhdlz9zOYwxh8lDdnvmMOe/+5cdoEdg==","time":1771959187638,"size":4068,"metadata":{"time":1771959187366,"url":"https://registry.npmjs.org/combined-stream/-/combined-stream-1.0.8.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","conten...
```

## Module: ./.npm/_cacache/index-v5/4e/cb/181b542af5715304f09bc46022c0baa2bde37d2b7e9fa2b39cf626f467fb
```

5a2eb8df41cb3c876d77e09df390e0af45bc6ba9	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/delayed-stream","integrity":"sha512-OJFCTqtRwFV6BvjXfBuw/h8EzCZTW/TNh8qDmWSLhrYe0pY3s5aNSnbTnYMqBANy3hFfVSxR4UY2u9AgZcWjMw==","time":1771959186215,"size":15820,"metadata":{"time":1771959186193,"url":"https://registry.npmjs.org/delayed-stream","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application...
```

## Module: ./.npm/_cacache/index-v5/56/4b/859813b09e1e5020654bf65fb2f19970c51f08f788d3c4f2ea5137051e1e
```

a4e652868011f557f116776ee5481ee5be9e6dc1	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/node-domexception/-/node-domexception-1.0.0.tgz","integrity":"sha512-/jKZoMpw0F8GRwl4/eLROPA3cfcXtLApP0QzLmUT/HuPCZWyB7IY9ZrMeKw2O/nFIqPQB3PVM9aYm0F312AXDQ==","time":1771959187605,"size":3614,"metadata":{"time":1771959187300,"url":"https://registry.npmjs.org/node-domexception/-/node-domexception-1.0.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600"...
```

## Module: ./.npm/_cacache/index-v5/57/b7/2772f8c4daa4b31074e03545f8e473b547e88ef3141501fe2a54e1abdfc4
```

3240cfbc627abe922db95f224589f787554d4402	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/bytes","integrity":"sha512-mJpo6EVFzxhpU7aSfHWHGl5fZh0H74BbWF+nw6DFvhCWJv1YFFNF2LuFjpThtmtZk33Bw9TrYowcZg3qXDUt5w==","time":1771959185993,"size":37018,"metadata":{"time":1771959185967,"url":"https://registry.npmjs.org/bytes","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"Tue...
```

## Module: ./.npm/_cacache/index-v5/59/08/7048656a801d0afc85d258adaca095e8f43558b84aacffaa7c60350005c4
```

a36bc2d3cee8a9a1394f1c6aa96d549cec11d880	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/math-intrinsics","integrity":"sha512-miAoC9Azb6qz8200QI2/swCGlQeCI6OkFRUmk2KeIRLkqbw6agG69A7PXSRVIa+lM6rpLPUTUujqm6R/u6FRGg==","time":1771959186415,"size":9265,"metadata":{"time":1771959186384,"url":"https://registry.npmjs.org/math-intrinsics","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"applicatio...
```

## Module: ./.npm/_cacache/index-v5/59/8f/04e6f64d657039df04ffd17af0bb8c7b3f5db2f8937c8a322ae2455af62e
```

221b4a11e523dc6e9cbcb2cb225bc3193483a9f6	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/toidentifier/-/toidentifier-1.0.1.tgz","integrity":"sha512-o5sSPKEkg/DIQNmH43V0/uerLrpzVedkUh8tGNvaeXpfpuwjKenlSox/2O/BTlZUtEe+JG7s5YhEz608PlAHRA==","time":1771959187584,"size":2347,"metadata":{"time":1771959187285,"url":"https://registry.npmjs.org/toidentifier/-/toidentifier-1.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"app...
```

## Module: ./.npm/_cacache/index-v5/5e/2f/b0d7ba846044fe5a2fa1d8341f6a7f56438ae9161709a548cbda5f1fd7c3
```

0548d222f40051b4502fc97bb14de5f9a9ce28e1	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz","integrity":"sha512-ZySD7Nf91aLB0RxL4KGrKHBXl7Eds1DAmEdcoVawXnLD7SDhpNgtuII2aAkg7a7QS41jxPSZ17p4VdGnMHk3MQ==","time":1771959187608,"size":3464,"metadata":{"time":1771959187372,"url":"https://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-ty...
```

## Module: ./.npm/_cacache/index-v5/60/df/89f1345cb5849d888a2cce2e6d6ddc0014eb3d6722956a06241f6e7f3d58
```

b975665228c85436f72d89a1d95e93a521932328	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/data-uri-to-buffer","integrity":"sha512-rBx4ZaWsIqC7An/PvOL3HUOX2IR+lR14IwL/1ufcZbMpQDqECL3f4kEGVevDqeYLpDIrKTDm0yoDkHhlS1SOlA==","time":1771959185826,"size":43253,"metadata":{"time":1771959185818,"url":"https://registry.npmjs.org/data-uri-to-buffer","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"app...
```

## Module: ./.npm/_cacache/index-v5/67/f8/ae718527d2b9bf7fa981d80037d5b2f7b34f0e34a76fdd3bc9b604b90077
```

f1872a77289c9982f73a9c6043bdc24a23267e1f	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.2.tgz","integrity":"sha512-NqADB8VjPFLM2V0VvHUewwwsw0ZWBaIdgo+ieHtK3hasLz4qeCRjYcqfB6AQrBggRKppKF8L52/VqdVsO47Dlw==","time":1771959187530,"size":6465,"metadata":{"time":1771959187261,"url":"https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","conten...
```

## Module: ./.npm/_cacache/index-v5/6b/33/9648614194cfe05bcf87e96e6d1a9d596eff2ccd2be75d5a63840ff5c5fa
```

321c2b0955a7ab3952b125b7a9b1e898a05f8215	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz","integrity":"sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ==","time":1771959187597,"size":6067,"metadata":{"time":1771959187345,"url":"https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immu...
```

## Module: ./.npm/_cacache/index-v5/6c/b8/bf3defaf56a777b0a2db86bdc94ecb2191281a9ae7585d3ff39ed841c8f5
```

c760853ac9d786a9c1401b48879059c8d1e1c203	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/statuses","integrity":"sha512-haKOHfP2DiMULkVyi6+yrVeYUEL52xEI1dla8yG5xv9HEncMzNYR2x8NaHZ3BnOMUeZMsrvyIrlrdoZKef8rKA==","time":1771959186797,"size":37117,"metadata":{"time":1771959186785,"url":"https://registry.npmjs.org/statuses","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date...
```

## Module: ./.npm/_cacache/index-v5/73/c1/d8bbb109a8fa2903d912518bf54776b7794c8f6f0a759234283c3c2eefab
```

804cb6e9da2370a2a2fa39aff79f7b29bc4eb58b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/web-streams-polyfill","integrity":"sha512-PXCeQH5vP1nYv5GJWA7fd7znWw1z0equHqfwwg42T48PqU1VWpok45QSO0QX3lmB9z0DO0US4nVsk7sZemLQJg==","time":1771959186682,"size":136634,"metadata":{"time":1771959186661,"url":"https://registry.npmjs.org/web-streams-polyfill","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type"...
```

## Module: ./.npm/_cacache/index-v5/7a/83/6be996e7250adf9a97984c85c3a7d3c22c795ce5321c44d257e053fd7442
```

a482b21bfb183cb75511e2dd4accfaae8835054b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/http-errors","integrity":"sha512-szeT6T8IHxtS6u6lE6DSBH62fJhnwM/QxQcV+mhCV4mYlRlJd/OHsM8kfxpVyVYZeWquXCzNFqlBJC4f05I9UQ==","time":1771959185984,"size":71987,"metadata":{"time":1771959185958,"url":"https://registry.npmjs.org/http-errors","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json"...
```

## Module: ./.npm/_cacache/index-v5/7d/65/c2c4e4cf88f6f5a26a474eec1eb28a1a0c087f156fa82df974013a50081f
```

b37319fc59d9b77e3d6bc0174879541ca47e67a6	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz","integrity":"sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==","time":1771959187598,"size":5338,"metadata":{"time":1771959187351,"url":"https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/oct...
```

## Module: ./.npm/_cacache/index-v5/7f/13/60ac17a18ad7b0c683accc08b7fe8baeaed4c881fb7cccb56d84909c2110
```

14a6fc4311b03898b5ad553035de1a66cbe480b2	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/has-tostringtag","integrity":"sha512-/FZDQ0xguOBuwiW+fRRQBGOSa4RFXFKQreHQHccA3qANL/VmgKPrbuc67HDwWu9ZwZtIDDiyqaUq8rUAXsrmrg==","time":1771959186217,"size":13945,"metadata":{"time":1771959186208,"url":"https://registry.npmjs.org/has-tostringtag","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"applicati...
```

## Module: ./.npm/_cacache/index-v5/81/18/dc968dc58cf2e03b6fdf660412df274d4ec69e93304f5b2fa4437684d84b
```

25fb8bacd16d2a62b3b65e198f9e95b9bfda38e8	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/dunder-proto","integrity":"sha512-5TFAs0uiIWhwtH0SM7l2QAaRKSVOQ+Q/WQtH2sXZ3Rvtlqz+aGfeMG0w4z84X67Ihuy7XN/HoJwwad8QGi3DcA==","time":1771959186581,"size":8256,"metadata":{"time":1771959186575,"url":"https://registry.npmjs.org/dunder-proto","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json...
```

## Module: ./.npm/_cacache/index-v5/84/3c/a34aeaf29195f5f9401c15f6857af1bd76c7606e0b093aab991c9bb6dc49
```

d4bae2ed30b19cab71a3ee06a3cdf63d9944cced	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/gopd/-/gopd-1.2.0.tgz","integrity":"sha512-ZUKRh6/kUFoAiTAtTYPZJ3hw9wNxx+BIBOijnlG9PnrJsCcSjs1wyyD6vJpaYtgnzDrKYRSqf3OO6Rfa93xsRg==","time":1771959187459,"size":4584,"metadata":{"time":1771959187205,"url":"https://registry.npmjs.org/gopd/-/gopd-1.2.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","date":"T...
```

## Module: ./.npm/_cacache/index-v5/84/c1/099718d07cb1335cea112ac75569bfd0e89ebd9c4a319f1fc7fc1ae76afb
```

665bb5182c83e2cfb85088e9e61afcc02ca4541b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/universal-user-agent","integrity":"sha512-OojMA+rtV3Vypxm/MhaM59YTF10X1ePIsA7zo+o+bn922I1xDrIcLc0PYj4r1tEm13PPhKb8/VxjNiCcEZWbHQ==","time":1771959185135,"size":44336,"metadata":{"time":1771959185112,"url":"https://registry.npmjs.org/universal-user-agent","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":...
```

## Module: ./.npm/_cacache/index-v5/86/a2/5b27bb74c4b5717e38015bd570d651f9a9ebdd15044c34b5717193654f28
```

67aa6e8876735daa8ffc7b35de2a2038f22035b7	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/iconv-lite","integrity":"sha512-Jd2Mhgqfvn1CzOTZgoKBnqKhug2ld4lDUarOYzrYFayYFq60GMY6nE4DHMdtTT363z1ubDyml7krrrZ0mGo/DA==","time":1771959185998,"size":120557,"metadata":{"time":1771959185974,"url":"https://registry.npmjs.org/iconv-lite","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json",...
```

## Module: ./.npm/_cacache/index-v5/87/55/e56d34b37c3170079064597cabb288d076b0d0468eaba3b8a0cf8686ce1f
```

5ab3c7dd571a6d7b7c566c4898cf5608d569373f	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/safer-buffer/-/safer-buffer-2.1.2.tgz","integrity":"sha512-YZo3K82SD7Riyi0E1EQPojLz7kpepnSQI9IyPbHHg1XXXevb5dJI7tpyN2ADxGcQbHG7vcyRHk0cbwqcQriUtg==","time":1771959187377,"size":12035,"metadata":{"time":1771959187161,"url":"https://registry.npmjs.org/safer-buffer/-/safer-buffer-2.1.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"ap...
```

## Module: ./.npm/_cacache/index-v5/87/da/af28f1133468f98432a0caf94d8a9e1a4f1bcd830398a06a4e51d9d17bcd
```

dc6026d165acdc583e42e67eb6162f2e161a8158	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz","integrity":"sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA==","time":1771959187596,"size":9799,"metadata":{"time":1771959187321,"url":"https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":...
```

## Module: ./.npm/_cacache/index-v5/8b/11/6afb42c4265115071af3f3969ce706a24f7c076e3eeedb1b7b93907a62e5
```

c7b77a12ec189323d61adb11e5353b4d2b40ec58	{"key":"security-advisory:@modelcontextprotocol/sdk:QsjtvJ5ac/TGCZ47ZpJnb997xn2P0kWf5E68zc5qUNkotHFHRxUp3JpqYWPPIDFjZFErROUvgKj2wUESmsIfgw==","integrity":"sha512-qDGzOnt+OlUv/VI5uLklwbtv7xcJefHhEkCs8Y3F+jWOCj7rcXVOCWQS1eTDpHqZAe12v7yeXflpBqsMe6k1nw==","time":1771959187781,"size":1725}...
```

## Module: ./.npm/_cacache/index-v5/8b/1a/10e37507d35e496f10efac4f5ff8a399529e2de7780b4c67639e02c84b95
```

3d863c26f0a1616130981eb4782a22988f442ccb	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@types/node-fetch/-/node-fetch-2.6.13.tgz","integrity":"sha512-QGpRVpzSaUs30JBSGPjOg4Uveu384erbHBoT1zeONvyCfwQxIkUshLAOqN/k9EjGviPRmWTTe6aH2qySWKTVSw==","time":1771959187668,"size":4125,"metadata":{"time":1771959187488,"url":"https://registry.npmjs.org/@types/node-fetch/-/node-fetch-2.6.13.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, must-revalidate, max-age=31557600","cont...
```

## Module: ./.npm/_cacache/index-v5/8c/3f/3f36a0c43685a86c104116ac6b2331e94c005abd54ee9d644a52e1770b8e
```

0e78557f7e048b2f6d7e6f5584159f2cf0f7e37e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/asynckit","integrity":"sha512-zAS8k/pfFzGjaChvSJSj60uhcmO6MfT6NjOqm5uqdrxEw8Ya3qzikRyJ2Nphbn0iGn4MFvh0z/EaJ1xFAYt+6Q==","time":1771959186108,"size":18932,"metadata":{"time":1771959186096,"url":"https://registry.npmjs.org/asynckit","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date...
```

## Module: ./.npm/_cacache/index-v5/8d/09/b8f5ca2fb119384681b46ab4e23e4621b770a9043991348d533c215b4433
```

6903558f220e89572e4e1724586f6cba1bf37ff6	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/function-bind","integrity":"sha512-KHH8St2QS2qHu0qzOlTCAoHlLdlEI2widcSpJb1dAYYs2PeGNc5Bbo2EVAEtZzbfZcNDsqzLvTZt0chYkR6tKA==","time":1771959186217,"size":15733,"metadata":{"time":1771959186202,"url":"https://registry.npmjs.org/function-bind","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/j...
```

## Module: ./.npm/_cacache/index-v5/90/81/b282fc65fba2629a78ffb2c85ff35c7028db687a67d0498adaaa3f3215c1
```

3b61ddbe1313d9e79afaba8219333f93328ec46e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/depd","integrity":"sha512-hkeJTjMO+fjrX/MEXriK9N/mi0Sm3ewuaD2Xf7wPeP5Z80QalQWyPiUjfkUjTDc53j5JiuJr31cGPb2A0p8kww==","time":1771959186798,"size":40182,"metadata":{"time":1771959186787,"url":"https://registry.npmjs.org/depd","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"Tue, ...
```

## Module: ./.npm/_cacache/index-v5/93/e9/5d280988d8f7e77f5315ecca2cd8f0b2b8aa06d97cce24d12a5b6a534b64
```

401069e6a19c8ed4592ac6dc4ec7a03d393e52ad	{"key":"security-advisory:@modelcontextprotocol/server-github:4b0cJ/uchNEV2nXUZPd9qbxqGff8VpNxbXQM3YmcQWB6QCyueTCymTbHhhbuQuS16ASvhoylrcXWV6y/dqwtbw==","integrity":"sha512-H3BRLC+og8DaDe+1N65quiF5+HoHKm7CBG6BVy/MnnC3Gq2ej9hiEbIZLDm9+p+BGCbrz721UgKZBpqtJTyjSw==","time":1771959187861,"size":740}...
```

## Module: ./.npm/_cacache/index-v5/94/49/0c8e6bfaa289aa93424dc1f6f28b3decc9f59cb08be977c3040f7d244ac3
```

c586fed4848fb0de94dbe2977eb3f08d45354214	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/formdata-polyfill","integrity":"sha512-DahgxKLrGy4wJ502eYCF5eEVoxSRCh0dIe+5aGAaeL+seyzKYnOQAJ+jaLPTbvdfD1O7erBadFcE9UQMlrtw4g==","time":1771959185877,"size":94446,"metadata":{"time":1771959185859,"url":"https://registry.npmjs.org/formdata-polyfill","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"appli...
```

## Module: ./.npm/_cacache/index-v5/95/b5/067cbcdfe5206749e8eb0025c4f8749c9d01103f8b3b5032608a56885c78
```

55d75466f21a2aff6daa78b5be9881e3ae5d5cb7	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/call-bind-apply-helpers","integrity":"sha512-yotdst0/m8U02f3xOKhLhkla92wxLwZfv/MAUD6cT9+HcPeqyS+SsfEWAK51XQhCBTdi/Lxb3Yt0xfjPSe83CA==","time":1771959186488,"size":12744,"metadata":{"time":1771959186478,"url":"https://registry.npmjs.org/call-bind-apply-helpers","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-...
```

## Module: ./.npm/_cacache/index-v5/98/39/b93a55ccc4e49f1f202fb8da7ee9e687e3a2a49ec42d4759cf6b22a7a96a
```

4eaa0d6833615efe91f11915646a1699b1e67241	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/mime-types/-/mime-types-2.1.35.tgz","integrity":"sha512-ZDY+bPm5zTTF+YpCrAU9nK0UgICYPT0QtT1NZWFv4s++TNkcgVaT0g6+4R2uI4MjQjzysHB1zxuWL50hzaeXiw==","time":1771959187645,"size":5591,"metadata":{"time":1771959187374,"url":"https://registry.npmjs.org/mime-types/-/mime-types-2.1.35.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"applicati...
```

## Module: ./.npm/_cacache/index-v5/a4/02/d301998e011aec184d434fed3d3e5e23b13c523b455442bee56b410e6706
```

1b829abfe8b2f4b4f0dc0275bb062c28dbf6d308	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@modelcontextprotocol%2fserver-github","integrity":"sha512-kmsT2FPdSscxgpdYzBzyKbr/NcbvOi4SctG42nmpMW1FgHZES5VPNV9qMzCokCeZ552Zq2hiB3oSoD1Ys8FLxg==","time":1771959184829,"size":40221,"metadata":{"time":1771959184814,"url":"https://registry.npmjs.org/@modelcontextprotocol%2fserver-github","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","conten...
```

## Module: ./.npm/_cacache/index-v5/a5/14/53e431efe5d40277f768cec075f9e7f618f2296715654a7b953121078b1e
```

be605faa5ec3e09673c8b88f37dd2ac8d7d7894d	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/mime-db/-/mime-db-1.52.0.tgz","integrity":"sha512-sPU4uV7dYlvtWJxwwxHD0PuihVNiE7TyAbQ5SWxDCB9mUYvOgroQOwYQQOKPJ8CIbE+1ETVlOoK1UC2nU3gYvg==","time":1771959187510,"size":26992,"metadata":{"time":1771959187230,"url":"https://registry.npmjs.org/mime-db/-/mime-db-1.52.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-st...
```

## Module: ./.npm/_cacache/index-v5/ad/5c/217f4a9502eed2896935b005b187e4713d93ba3dc76eff284b00a1a8b92a
```

d1a38d41e2ac374f2903f546fe5d287f6f28527a	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/data-uri-to-buffer/-/data-uri-to-buffer-4.0.1.tgz","integrity":"sha512-0R9ikRb668HB7QDxT1vkpuUBtqc53YyAwMwGeUFKRojY/NWKvdZ+9UYtRfGmhqNbRkTSVpMbmyhXipFFv2cb/A==","time":1771959187426,"size":3680,"metadata":{"time":1771959187209,"url":"https://registry.npmjs.org/data-uri-to-buffer/-/data-uri-to-buffer-4.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557...
```

## Module: ./.npm/_cacache/index-v5/ad/7c/cc598261aa7c1f089fdcd0478664f8f5c80f8f02f241f08e3be264a9e616
```

6d983c5bb3c2f4945f2f015e25413f8dea8f6d48	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/fetch-blob/-/fetch-blob-3.2.0.tgz","integrity":"sha512-7yAQpD2UMJzLi1Dqv7qFYnPbaPx7ZfFK6PiIxQ4PfkGPyNyl2Ugx+a/umUonmKqjhM4DnfbMvdX6otXq83soQQ==","time":1771959187649,"size":7689,"metadata":{"time":1771959187297,"url":"https://registry.npmjs.org/fetch-blob/-/fetch-blob-3.2.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application...
```

## Module: ./.npm/_cacache/index-v5/b0/2c/c32c19940ce5ae8947c9a9ded52fad0414a733558ca85abdd82207e117c5
```

c9ce941601bd3599938f8af436afc17f37be3e55	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-object-atoms","integrity":"sha512-mIPibeFQ5TxoaW+0bzAwm+CXECezw3fXqEmvV17KuZQ7oz7R75/9aCWZa1vQoJunzPF1xGxpF8oYSVlXBBq8cg==","time":1771959186416,"size":15304,"metadata":{"time":1771959186409,"url":"https://registry.npmjs.org/es-object-atoms","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"applicati...
```

## Module: ./.npm/_cacache/index-v5/b0/4a/c18a99a2710b49b5a3a1121226be4940f623f8ba056f8108a634ed347da9
```

84b6e62d9728eeeb4a0662d6dcfac5fc01e7864a	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/mime-types","integrity":"sha512-CXCvyHu1ileJGCL4vJuzSiQU+zaLUgeZf9Z5acQ/QA3U3bctpbulUX71IbWnqsMevh4iXbUu9sGnPAP9i9daIQ==","time":1771959186108,"size":139110,"metadata":{"time":1771959186076,"url":"https://registry.npmjs.org/mime-types","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json",...
```

## Module: ./.npm/_cacache/index-v5/b0/76/986536ddaae5ed8a7c1e68783ec69615dac1a9de909de84a86cfea2fb14f
```

e8c41931dc757c39bb2a403811d9a01f79dcb7cb	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@modelcontextprotocol/server-github/-/server-github-2025.4.8.tgz","integrity":"sha512-8N43bQw9MlUB0piTZHK2JMh8kYPKxH57d4Z7Wb8PS4by2MkZ0FzI5xPImg3xumpev82VZw2VWHQJJJYp+WkwEw==","time":1771959187673,"size":13635,"metadata":{"time":1771959187558,"url":"https://registry.npmjs.org/@modelcontextprotocol/server-github/-/server-github-2025.4.8.tgz","reqHeaders":{},"resHeaders":{"cache-control":"p...
```

## Module: ./.npm/_cacache/index-v5/b1/8f/5767f914aa664f32503df614481bac973784e2bcd2b8af02e84faabe168d
```

bdd3bffc986a502300d700bd9b22555a20b2065f	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/web-streams-polyfill/-/web-streams-polyfill-3.3.3.tgz","integrity":"sha512-d2JWLCivmZYTSIoge9MsgFCZrt571BikcWGYkjC1khllbTeDlGqZ2D8vD8E/lJa8WGWbb7Plm8/XJYV7IJHZZw==","time":1771959188238,"size":1579083,"metadata":{"time":1771959187280,"url":"https://registry.npmjs.org/web-streams-polyfill/-/web-streams-polyfill-3.3.3.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, ma...
```

## Module: ./.npm/_cacache/index-v5/b3/0a/d7cd7487e60fb3aff6f4679e99cc0f8445ae36507f287aff8dc9d5dea1eb
```

68f9ba1bdc29f63b270a0c9f0df9f02bef749762	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/statuses/-/statuses-2.0.2.tgz","integrity":"sha512-DvEy55V3DB7uknRo+4iOGT5fP1slR8wQohVdknigZPMpMstaKJQWhwiYBACJE3Ul2pTnATihhBYnRhZQHGBiRw==","time":1771959187604,"size":4797,"metadata":{"time":1771959187295,"url":"https://registry.npmjs.org/statuses/-/statuses-2.0.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-s...
```

## Module: ./.npm/_cacache/index-v5/b7/7c/bef778b25c0ebbc1ec51711ea957725f5792a3e2511e72d6c71494c7dbbe
```

24957a240e7179111bbfeb96250c2006808ce080	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/undici-types","integrity":"sha512-e5nNmSX5OzoeJjJGOzEvMNIcC3D18NjhJdIXytYK/9OBUIZuahp930lPNFfQEiw/+EQ22dkqBnIx4wL7Jsk6kg==","time":1771959185789,"size":171546,"metadata":{"time":1771959185759,"url":"https://registry.npmjs.org/undici-types","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/js...
```

## Module: ./.npm/_cacache/index-v5/bd/12/2937f0abc26f9973382cb3afa8b4b1d233a6a47ad4f3c5917ddb4997cddb
```

6347134fcc9527f5b490b66865fa3561fd641544	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/inherits/-/inherits-2.0.4.tgz","integrity":"sha512-k/vGaX4/Yla3WzyMCvTQOXYeIHvqOKtnqBduzTHpzpQZzAskKMhZ2K+EnBiSM9zGSoIFeMpXKxa4dYeZIQqewQ==","time":1771959187354,"size":2030,"metadata":{"time":1771959187129,"url":"https://registry.npmjs.org/inherits/-/inherits-2.0.4.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-s...
```

## Module: ./.npm/_cacache/index-v5/be/db/6429cc47f4ecda3ff97d01807c0247f9458561ee5653a0d7fd21bfe9ffd6
```

956ec70c658425e812590b82aaebf0964e83609e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/raw-body/-/raw-body-3.0.2.tgz","integrity":"sha512-K5zQjDllxWkf7Z5xJdV0/B0WTNqx6vxG70zJE4N0kBs4LovmEYWJzQGxC9bS9RAKu3bgM40lrd5zoLJ12MQ5BA==","time":1771959187660,"size":6308,"metadata":{"time":1771959187392,"url":"https://registry.npmjs.org/raw-body/-/raw-body-3.0.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-s...
```

## Module: ./.npm/_cacache/index-v5/bf/81/25f2bae3018038cdcb0f2c1605be483cb40a8934fffd0c65ca7cd3c46618
```

ee228585cb41621378773dd38ffe3e0fd8b775e3	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/http-errors/-/http-errors-2.0.1.tgz","integrity":"sha512-4FbRdAX+bSdmo4AUFuS0WNiPz8NgFt+r8ThgNWmlrjQjt1Q7ZR9+zTlce2859x4KSXrwIsaeTqDoKQmtP8pLmQ==","time":1771959187635,"size":6448,"metadata":{"time":1771959187324,"url":"https://registry.npmjs.org/http-errors/-/http-errors-2.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"applica...
```

## Module: ./.npm/_cacache/index-v5/c1/02/d8075e0f65536acf7e0f5ec13ddad3156936c45ad00b5abe3929099d34e8
```

5b5d9a05ea7e700d86321d378203c52f3ab45cbe	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/hasown","integrity":"sha512-yUUGmw0LsJW8Zvu+ctgAYHOTyuJ6LHBmdKT88oAOKWAIwo/EWvaIG+kovvyc6QrEIjrhjBEA+1YjKTOYHZV7+A==","time":1771959186103,"size":12476,"metadata":{"time":1771959186082,"url":"https://registry.npmjs.org/hasown","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date":"T...
```

## Module: ./.npm/_cacache/index-v5/c1/d3/d6d16b3e7aa7edfdb1c5fe8ef0f9933ff289b5ae0026745e58f8b9d16511
```

389a3d6dae0f948602f65e03d599cbede040abb0	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/form-data","integrity":"sha512-CNlHRJKXkqz0j8BhdjPXDaep5/aWHMajxZDn5PdkdS09JDliyR0OypdkU8WLO5ibzssqVXliVvtAMTKUE4PWng==","time":1771959185790,"size":153646,"metadata":{"time":1771959185762,"url":"https://registry.npmjs.org/form-data","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","d...
```

## Module: ./.npm/_cacache/index-v5/c6/1a/2ba7b0e36b21f37bd0f07b3f3e1120ae4b499e566ebaff1afe853af6c7ab
```

d4c6589f521c33bc26ceb73f9a56f861ed7ef814	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/universal-user-agent/-/universal-user-agent-7.0.3.tgz","integrity":"sha512-TmnEAEAsBJVZM/AADELsK76llnwcf9vMKuPz8JflO1frO8Lchitr0fNaN9d+Ap0BjKtqWqd/J17qeDnXh8CL2A==","time":1771959187639,"size":4354,"metadata":{"time":1771959187423,"url":"https://registry.npmjs.org/universal-user-agent/-/universal-user-agent-7.0.3.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-a...
```

## Module: ./.npm/_cacache/index-v5/c7/00/75bf8643b1d803f427bd1e39480195432a26cf1b842251ec3a8629bd85b9
```

31d92d3eaad4e07b8f53fb22a8b8341dc3d62d6e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/setprototypeof/-/setprototypeof-1.2.0.tgz","integrity":"sha512-E5LDX7Wrp85Kil5bhZv46j8jOeboKq5JMmYM3gVGdGH8xFpPWXUMsNrlODCrkoxMEeNi/XZIwuRvY4XNwYMJpw==","time":1771959187309,"size":1969,"metadata":{"time":1771959187143,"url":"https://registry.npmjs.org/setprototypeof/-/setprototypeof-1.2.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-ty...
```

## Module: ./.npm/_cacache/index-v5/c9/10/e51aeab9f2ed39d1416132dca81cf2f580dc5de2fd02b9a85d1df3b191f3
```

0d47d741d97fb4363ee31822daa2c675de4f69bf	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz","integrity":"sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A==","time":1771959187355,"size":5049,"metadata":{"time":1771959187191,"url":"https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"app...
```

## Module: ./.npm/_cacache/index-v5/cc/25/0a0ad2d0308b6807a70e488194992de068d68b749910eee4847c38629984
```

d287f0496387d958f8e946b54873297d188a7e66	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/node-fetch/-/node-fetch-3.3.2.tgz","integrity":"sha512-dRB78srN/l6gqWulah9SrxeYnxeddIG30+GOqK/9OlLVyLg3HPnr6SqOWTWOXKRwC2eGYCkZ59NNuSgvSrpgOA==","time":1771959187639,"size":31722,"metadata":{"time":1771959187451,"url":"https://registry.npmjs.org/node-fetch/-/node-fetch-3.3.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"applicatio...
```

## Module: ./.npm/_cacache/index-v5/ce/cb/8564823aa3255dcec81b524fd590e5f3349ee1ada7d35311efcf7dcc5018
```

f5d2845a174cf0a912236afb0e2ebfe2dcc8f4f7	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/depd/-/depd-2.0.0.tgz","integrity":"sha512-g7nH6P6dyDioJogAAGprGpCtVImJhpPk/roCzdb3fIh61/s/nPsfR6onyMwkCAR/OlC3yBC0lESvUoQEAssIrw==","time":1771959187354,"size":8374,"metadata":{"time":1771959187148,"url":"https://registry.npmjs.org/depd/-/depd-2.0.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/octet-stream","date":"T...
```

## Module: ./.npm/_cacache/index-v5/cf/29/4e4e0b0e8d4f03f2f485736d86e55bc65c1e13c894d492caf00cfd202b74
```

7114b2296a9b2e399f964657c190ccff3d5a8b6b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/iconv-lite/-/iconv-lite-0.7.2.tgz","integrity":"sha512-im9DjEDQ55s9fL4EYzOAv0yMqmMBSZp6G0VvFyTMPKWxiSBHUj9NW/qqLmXUwXrrM7AvqSlTCfvqRb0cM8yYqw==","time":1771959187951,"size":189646,"metadata":{"time":1771959187302,"url":"https://registry.npmjs.org/iconv-lite/-/iconv-lite-0.7.2.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"applicati...
```

## Module: ./.npm/_cacache/index-v5/d1/64/7a9985fb916e97f21de973b7654d5f8eadad263fe4a5fc1da78a3656693e
```

2fdffdd54ac2da4feab0a22ab1af101323559078	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@modelcontextprotocol/sdk/-/sdk-1.0.1.tgz","integrity":"sha512-slLdFaxQJ9AlRg+hw28iiTtGvShAOgOKXcD0F91nUcRYiOMuS9ZBYjcdNZRXW9G5JQ511GRTdUy1zQVZDpJ+4w==","time":1771959188142,"size":82180,"metadata":{"time":1771959187524,"url":"https://registry.npmjs.org/@modelcontextprotocol/sdk/-/sdk-1.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, must-revalidate, max-age=31557600","con...
```

## Module: ./.npm/_cacache/index-v5/dc/8a/4dc2a1bdf5b195e99648a945ce742de5f6d0b1aac410a6fe3e7155933cc7
```

6225836df60329aaf8443ccf1475a8020b2a54ac	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/node-fetch","integrity":"sha512-4XH3dHnmhTTsGiuT2PxHx6E5mlNPUOmP2k5cR9LXIQpRqGnCcfJzL3TfOrpMPLwKXi1HzAM5CwVq+42VdnsKPA==","time":1771959185034,"size":896010,"metadata":{"time":1771959184941,"url":"https://registry.npmjs.org/node-fetch","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json",...
```

## Module: ./.npm/_cacache/index-v5/dd/6e/bce38caf63982c22edfa4ade01b8c45a3dd89b43c50398b9b8b1769b7865
```

64455dad39c35fa084c420b3ffbe642f20ead549	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@modelcontextprotocol%2fsdk","integrity":"sha512-mw3TUqwsIk16/VeJBI4OmxCdE+yTgee0aToE9RwqSGpD88x8oQFcCWqF1oe1G2MA41BfEaxwnE+3Wv6rXGWlrw==","time":1771959185306,"size":262328,"metadata":{"time":1771959185293,"url":"https://registry.npmjs.org/@modelcontextprotocol%2fsdk","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip",...
```

## Module: ./.npm/_cacache/index-v5/df/8e/9df6136179e75a89f9d3914f7535bf2a6318e5c002f7257fc49bc7b83ece
```

f9d6af3be2d41a819173ad37b82b4dc1e5151d4e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz","integrity":"sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA==","time":1771959187684,"size":5583,"metadata":{"time":1771959187349,"url":"https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557...
```

## Module: ./.npm/_cacache/index-v5/e0/c9/64c2fd3b183d1739f4be1b1d528a23f9b30ce37ca9974b48ca0b983598bf
```

f5cbb37fd930875e5dac266062c0c8c85e01a4f3	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/has-symbols","integrity":"sha512-yaaE/xigAwd6nLIMs6VC+M2iPGieJH/SbsfvVkXAwZ9Exr5Z1xj1QHfPF2wz82O3FgmMV6gneAQJ5GldKhMYFg==","time":1771959186414,"size":21550,"metadata":{"time":1771959186375,"url":"https://registry.npmjs.org/has-symbols","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json"...
```

## Module: ./.npm/_cacache/index-v5/e2/52/7a48e8e124c09a71cb479622597a4bde8beef41cdd0a9c6021ea58d98fa0
```

27dc4425d15541fba85540213f26967f975104ae	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/get-proto","integrity":"sha512-1rpWrP1q39bGUw8s0U72vWDn0BxCTHZl+gx0e6TvK9W9DzxK5CbglkRSZrKJpluP9nwaOuvluf0j3VLKgWfOIA==","time":1771959186416,"size":8300,"metadata":{"time":1771959186405,"url":"https://registry.npmjs.org/get-proto","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","dat...
```

## Module: ./.npm/_cacache/index-v5/e2/58/9f87d0a588ae2a6322c65b0916e3ec5af109671b0eee7b34730cfa1fe013
```

7dcfd8e544a5a334ef0cda40f9cd8403cb43fd3e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/toidentifier","integrity":"sha512-Q5ZuyZcUDWwmgjR0rdnU2wTenuIPXeVvz2xkK+ThhHc3OoOa5GtsqGtbt9nagnQGHmHQN2upVtlC/Ow6x7klxg==","time":1771959186796,"size":12006,"metadata":{"time":1771959186778,"url":"https://registry.npmjs.org/toidentifier","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/jso...
```

## Module: ./.npm/_cacache/index-v5/e6/31/11eb65d70a004ba6dc4f967bae593980ef09d70ba81fd2af497387d1d59a
```

9ace7fbb1e2293460c020f8856dd7920e6dffaa5	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/raw-body","integrity":"sha512-bVhYyi+FTUCYkMbu//HfPB6fF2cpesFWvvKZHWpKZELDBwbLSd7h4/C5btc2SFJ61v5oiUZ6Z9eMVUixKFOONg==","time":1771959185787,"size":117822,"metadata":{"time":1771959185765,"url":"https://registry.npmjs.org/raw-body","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","dat...
```

## Module: ./.npm/_cacache/index-v5/e6/ee/a7f609296af013f459dea95f5b86155b1d4d3fa7dc9ec423562d0c55294f
```

f8f203b6b41a2f83e31c365afae6f194ae094419	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/has-symbols/-/has-symbols-1.1.0.tgz","integrity":"sha512-1cDNdwJ2Jaohmb3sg4OmKaMBwuC48sYni5HUw2DvsC8LjGTLK9h+eb1X6RyuOHe4hT0ULCW68iomhjUoKUqlPQ==","time":1771959187399,"size":8059,"metadata":{"time":1771959187195,"url":"https://registry.npmjs.org/has-symbols/-/has-symbols-1.1.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"applica...
```

## Module: ./.npm/_cacache/index-v5/e7/40/70186a6ceaad19b6b11ac1bccf00fa5e038b8151d455127f9868f0051d57
```

35cda2dcfb928e11fffe6046ad5f24ee3d0d7f61	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/node-domexception","integrity":"sha512-p9j/KYZj6O4tkYoZoKAENadTfOdXozfm3YWX4hPJ5W1M5htb4wxLcZxQVP7ZgcUfeKiPU4mhki2rTc9SSOg8TA==","time":1771959186673,"size":11516,"metadata":{"time":1771959186658,"url":"https://registry.npmjs.org/node-domexception","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"appli...
```

## Module: ./.npm/_cacache/index-v5/e8/ad/09d01e1a140286a104a3deaa2cda92fe426a5115039ba9b221f230288b0c
```

b4c8adccf1ad57c3b9f8c861b83f2990cd77b295	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/undici-types/-/undici-types-6.21.0.tgz","integrity":"sha512-iwDZqg0QAGrg9Rav5H4n0M64c3mkR59cJ6wQp+7C4nI0gsmExaedaYLNO44eT4AtBBwjbTiGPMlt2Md0T9H9JQ==","time":1771959187646,"size":21020,"metadata":{"time":1771959187420,"url":"https://registry.npmjs.org/undici-types/-/undici-types-6.21.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"...
```

## Module: ./.npm/_cacache/index-v5/ea/5f/ed9fbd5bd146db522eb110c35f223340a514174c0f8ba9132ea20b8f6721
```

0815a8481b5e45ad1d6e822002815a72f8138fb6	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-errors","integrity":"sha512-Mt4qiIKLdqmaTL1nW8gDm1l41XLBhZsTQznmpTAL/IzgHqRYbH8cUO8qmOAMDzdkaGLMRJz30ps+TgihtaOwpw==","time":1771959186217,"size":16918,"metadata":{"time":1771959186206,"url":"https://registry.npmjs.org/es-errors","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","da...
```

## Module: ./.npm/_cacache/index-v5/ee/1c/3221b6bf06d485cdf0bd005ec91250937fb93523cafa298df7fc42d4b8b6
```

f64f66f5235c8d93bc072a432ee07e3d754c5128	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-define-property","integrity":"sha512-18mh44uP6hXUwKNlzAMQfWystXfJn6HOgWiToB9bwPrzGWGRySh1ce05ZWXsavZlJio6Aul8jp1D3tF15V62Vw==","time":1771959186494,"size":8542,"metadata":{"time":1771959186485,"url":"https://registry.npmjs.org/es-define-property","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"appl...
```

## Module: ./.npm/_cacache/index-v5/ef/8e/377cd61df01a3a7c51c0c5c1a067f6f334d15963dd4edbc491973d8cb582
```

f22e9508710a4b948110b8a630c1052477ba5e78	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/get-intrinsic","integrity":"sha512-EwIiHrMltb8pfi/ci0n9lX3Yq1orCWMkvlaE19FGPhUCQZIF/5XEIVpEBwKfUMXZfE5AGfRyJjj3ZwjqsnOEjQ==","time":1771959186218,"size":60985,"metadata":{"time":1771959186198,"url":"https://registry.npmjs.org/get-intrinsic","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/j...
```

## Module: ./.npm/_cacache/index-v5/f1/53/8aee994a2b5c701755cdc5660748a90199cf48437f5f93fdd0572344f2f1
```

a6a0d4bf6a1caebd6d2f2ad68200844444f6e7e4	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/fetch-blob","integrity":"sha512-8z9fVFiDc1kTgg97k4jEu49VBtOlNCmRYh6estKccOrX4k7RH9I5SIRjcj+SK9N1/Yyxrq9dARjHR1y1FqEQkA==","time":1771959185861,"size":73704,"metadata":{"time":1771959185840,"url":"https://registry.npmjs.org/fetch-blob","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","...
```

## Module: ./.npm/_cacache/index-v5/f3/2c/80267cf9b394a43404ccabe3e574f5fd89b769b43be625b75ff9b1b4a2ee
```

0dc2bc6c43e1f19feeebbd4ae4abfeea9f559834	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/mime-db","integrity":"sha512-KFqU8SfDqy5M8lQ9z1QUi7oaJDag/bK++r7LvdQ8Eh0zSUqLFKD0AbE2LQPWBjwB+ToLfFA53f5FZxy70x4AbA==","time":1771959186285,"size":164953,"metadata":{"time":1771959186274,"url":"https://registry.npmjs.org/mime-db","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date"...
```

## Module: ./.npm/_cacache/index-v5/f5/91/b4bddca1df9d1a5db8fc8bd09d22078228fd3c1f50ad12a3c9886499c03f
```

a6f652bba1695152a6471450b6d3090fbbb51b0b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.3.0.tgz","integrity":"sha512-9fSjSaos/fRIVIp+xSJlE6lfwhES7LNtKaCBIamHsjr2na1BiABJPo0mOjjz8GJDURarmCPGqaiVg5mfjb98CQ==","time":1771959187584,"size":13800,"metadata":{"time":1771959187292,"url":"https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.3.0.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type"...
```

## Module: ./.npm/_cacache/index-v5/fb/86/2f77dc3bf8a16f2c2f2611166fc2471b45d026db13426ca74beb9549c47a
```

46d7571d539b0fd32ce3f240ead379edba85cf40	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@types%2fnode-fetch","integrity":"sha512-nf/ogt3/KPkizHY42VlcIR/UacpwizbAsrUbgkx926DXq7eHaNgTF9cnVWP2VAvFqg3hqlSuhRCjqTu6++Mpqw==","time":1771959185263,"size":145604,"metadata":{"time":1771959185237,"url":"https://registry.npmjs.org/@types%2fnode-fetch","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"...
```

## Module: ./.npm/_cacache/index-v5/fb/e2/09a86cea8bd3245e00e7fecbb871acb7e912d8b7616f1d5de7bc8dcef9e9
```

dcc3a5dbc0399070df9bec2191824542212ec875	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/es-set-tostringtag","integrity":"sha512-ig1JlPx2PuwgJEW6jdd8Kgf/fEH9GSB4DDYKKC3HNmr8wbQboKbeq5K6+D/SEGhulseFn6U5Yl/IO7UOwmjpxg==","time":1771959186107,"size":22094,"metadata":{"time":1771959186091,"url":"https://registry.npmjs.org/es-set-tostringtag","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"app...
```

## Module: ./.npm/_cacache/index-v5/fc/ee/fc3e1dd6706bd557d2840d92ff10cdd6928b92fb8c46d2195dfbd8d4b2be
```

7e214d00132112fa5a2bfa5a0be1d5dc5a7db00b	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/@types%2fnode","integrity":"sha512-R34z9rZIHjZHI6xksnzT0XSgGce8s8ughRkw2ebDZbfn54uhqU/rj4UW7kpeFwiQF42wT08y5/xd6UjjWkl5iQ==","time":1771959185409,"size":10864169,"metadata":{"time":1771959185064,"url":"https://registry.npmjs.org/@types%2fnode","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"applicatio...
```

## Module: ./.npm/_cacache/index-v5/fd/51/5bf9d842e1ecfea484079ce86f5d7bf7ceddbcc1711c7b29270cb9913b31
```

05297a87ee1919313d96f12528e027391e756647	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/setprototypeof","integrity":"sha512-uocdYB6PwNNTTzz+SnyT4JTGqHBk6ANL5YJ0s2nLbqqByxDQwlEnAnVMVTV015AlRQcolTDNyyuhi0LxzIyHQQ==","time":1771959186796,"size":14532,"metadata":{"time":1771959186774,"url":"https://registry.npmjs.org/setprototypeof","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application...
```

## Module: ./.npm/_cacache/index-v5/fd/fb/c68ba9a1320725050b57ca9c7fbc237e694f1f4a6cb94104f7e3e654f7f4
```

300737d775bc9517e03b34ff260eefdbd107f50e	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/get-proto/-/get-proto-1.0.1.tgz","integrity":"sha512-sTSfBjoXBp89JvIKIefqw7U2CCebsc74kiY6awiGogKtoSGbgjYE/G/+l9sF3MWFPNc9IcoOC4ODfKHfxFmp0g==","time":1771959187510,"size":4474,"metadata":{"time":1771959187243,"url":"https://registry.npmjs.org/get-proto/-/get-proto-1.0.1.tgz","reqHeaders":{},"resHeaders":{"cache-control":"public, immutable, max-age=31557600","content-type":"application/oct...
```

## Module: ./.npm/_cacache/index-v5/ff/d3/eca629ba696cac5a91e13f61bb768d7cbf82072f798d17071572ab3943f2
```

27bf55a4b07d3eac0a8e261ad067735e70d22573	{"key":"make-fetch-happen:request-cache:https://registry.npmjs.org/inherits","integrity":"sha512-xi9RpjT0VAYAJMV9Cz03zFVT2vUdGFxyYb7dswdi2n4jbFEhjF21MbApDHKBPEqW3B5RcMHCUXMNSOcpRurqCQ==","time":1771959186796,"size":12925,"metadata":{"time":1771959186782,"url":"https://registry.npmjs.org/inherits","reqHeaders":{"accept":"application/json"},"resHeaders":{"cache-control":"public, max-age=300","content-encoding":"gzip","content-type":"application/json","date...
```

## Module: ./.npm/_logs/2026-02-24T18_59_38_471Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_01_51_252Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_02_39_981Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_03_46_731Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_05_19_490Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_07_48_516Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_08_58_271Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_10_05_129Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T19_11_38_242Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T21_01_38_028Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-github
7 verbose argv "exec" "--yes" "--" "@modelcontext...
```

## Module: ./.npm/_logs/2026-02-24T22_13_42_588Z-debug-0.log
```
0 verbose cli /data/data/com.termux/files/usr/bin/node /data/data/com.termux/files/usr/lib/node_modules/npm/bin/npm-cli.js
1 info using npm@11.10.1
2 info using node@v25.3.0
3 silly config load:file:/data/data/com.termux/files/usr/lib/node_modules/npm/npmrc
4 silly config load:file:/data/data/com.termux/files/home/.npmrc
5 silly config load:file:/data/data/com.termux/files/usr/etc/npmrc
6 verbose title npm exec @modelcontextprotocol/server-databricks --host https://adb-26479705.4.azuredatabricks...
```

## Module: ./.npm/_npx/3dfbf5a9eea4a1b3/package-lock.json
```
{
  "name": "3dfbf5a9eea4a1b3",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "dependencies": {
        "@modelcontextprotocol/server-github": "^2025.4.8"
      }
    },
    "node_modules/@modelcontextprotocol/sdk": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@modelcontextprotocol/sdk/-/sdk-1.0.1.tgz",
      "integrity": "sha512-slLdFaxQJ9AlRg+hw28iiTtGvShAOgOKXcD0F91nUcRYiOMuS9ZBYjcdNZRXW9G5JQ511GRTdUy1zQVZDpJ+4w==",
      "license": "...
```

## Module: ./.npm/_npx/3dfbf5a9eea4a1b3/package.json
```
{
  "dependencies": {
    "@modelcontextprotocol/server-github": "^2025.4.8"
  },
  "_npx": {
    "packages": [
      "@modelcontextprotocol/server-github"
    ]
  }
}
...
```

## Module: ./.termux/termux.properties
```
### This is a `.properties` [https://en.wikipedia.org/wiki/.properties] file
### for termux app properties and is loaded with the `java.util.Properties.load()`
### [https://developer.android.com/reference/java/util/Properties#load(java.io.Reader)]
### call by the termux app and must be formatted as per its spec.
### To make changes to a property value, uncomment the property line by removing
### any hash `#` characters at the start of the line.
### After making required changes, save the file an...
```

## Module: ./Barrot-Agent/build_manifest.yaml
```
build_signature: BNDL-V3-QUANTUM-AGI
timestamp: 2025-12-31T01:47:00Z   # auto-generated UTC time
modules:
  - prediction_methodologies
  - deployment_integrity
  - builderio_microagent_logic
  - search_engine
  - dashboard
  - manifest_rail
  - quantum_entanglement
  - agi_reasoning
  - advanced_algorithms
  - integrated_system
resources:
  - kaggle
  - github
  - newspaper_articles
  - online_articles
  - science_papers
  - video_platforms
  - newsletters
  - forums
  - audiobooks
  - podcasts
...
```

## Module: ./SHRM-System/shrm-config.yaml
```
system_name: SHRM
full_name: System Health & Resource Monitor
version: 1.0.0
timestamp: 2025-12-25T20:38:37Z

monitoring_scope:
  - system_health
  - resource_allocation
  - workflow_integrity
  - bundle_synchronization
  - rail_status

interaction_protocol:
  type: ping-pong
  partner: Barrot-Agent
  frequency: scheduled
  response_mode: reactive

health_metrics:
  - cpu_utilization
  - memory_usage
  - disk_space
  - network_connectivity
  - service_availability

status:
  operational: true
  ...
```

## Module: ./SHRM-System/shrm-response-log.md
```
# SHRM Response Log

## System Health & Resource Monitor - Interaction History

This log tracks all ping-pong interactions between Barrot-Agent and SHRM.

---

### Session Start: 2025-12-25T20:38:37Z
🏓 SHRM initialized and ready for ping-pong with Barrot
🏓 SHRM PONG received from Barrot at Thu Dec 25 20:43:14 UTC 2025
🔵 Barrot PING -> SHRM at Thu Dec 25 20:43:14 UTC 2025
🔵 Barrot PING -> SHRM at Fri Dec 26 05:44:06 UTC 2025
🏓 SHRM PONG received from Barrot at Fri Dec 26 05:44:06 UTC 2025
🔵 Barro...
```

## Module: ./apex_lattice/__init__.py
```
"""
Apex Lattice — sandbox-based data processing and analysis system.

Public API
----------
    from apex_lattice import CycleManager, AuditTrail
    from apex_lattice import SandboxPipeline, FindingGenerator
    from apex_lattice import RecommendationEngine, PRFramework

CLI
---
    python -m apex_lattice               # single analysis cycle
    python -m apex_lattice --schedule 3600  # recurring every hour
    python -m apex_lattice --status      # view audit log
    python -m apex_lattice -...
```

## Module: ./apex_lattice/__main__.py
```
"""Entry point so the package can be invoked with `python -m apex_lattice`."""

import sys
from .cli import main

sys.exit(main())
...
```

## Module: ./apex_lattice/audit.py
```
"""
AuditTrail — append-only event log for all Apex Lattice activity.

All events are persisted as newline-delimited JSON under
``.apex_lattice/audit_logs/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

_DEFAULT_LOG_DIR = Path(".apex_lattice") / "audit_logs"


class AuditTrail:
    """Append-only structured event log."""

    def __init__(self, log_dir: Path | str | None = None) -> None:
        self._dir = Path(log_dir) if lo...
```

## Module: ./apex_lattice/cli.py
```
"""
CLI for the Apex Lattice sandbox analysis pipeline.

Usage
-----
    python -m apex_lattice               # run a single analysis cycle
    python -m apex_lattice --cycle       # explicit single cycle
    python -m apex_lattice --status      # show audit log tail
    python -m apex_lattice --schedule 3600  # recurring cycle every hour
    python -m apex_lattice --findings    # list persisted findings
    python -m apex_lattice --recs        # list persisted recommendations
"""

from __future...
```

## Module: ./apex_lattice/cycle.py
```
"""
CycleManager — orchestrates a single analysis cycle or scheduled recurring
analysis cycles.

A cycle is the full pipeline:
    SandboxPipeline → FindingGenerator → RecommendationEngine → PRFramework
    + AuditTrail logging at every step.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from .audit import AuditTrail
from .pipeline import SandboxPipeline
from .findings import FindingGenerator
from .recommendations import Re...
```

## Module: ./apex_lattice/findings.py
```
"""
FindingGenerator — analyses sandbox artefacts and produces structured findings.

Findings are persisted under ``.apex_lattice/findings/`` as individual
JSON files.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .analyzers import ALL_ANALYZERS

_DEFAULT_FINDINGS_DIR = Path(".apex_lattice") / "findings"


class Finding:
    """A single analysis finding."""

    def __init__(
        self,
        *,
        fin...
```

## Module: ./apex_lattice/pipeline.py
```
"""
SandboxPipeline — runs data through an isolated analysis environment.

Input data is the set of ``.log`` files already present under
``.apex_lattice/`` (e.g. the Millennium Problem analyses that Barrot
has pre-generated).  Each file is parsed into a structured record and
stored under ``.apex_lattice/sandbox/`` as a JSON artefact so that
downstream components can query it without re-reading raw text.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
fro...
```

## Module: ./apex_lattice/pr_framework.py
```
"""
PRFramework — generates pull-request bodies from recommendations.

In a live environment this module would call the GitHub API to open
a real PR.  For portability the default implementation writes a
Markdown document to ``.apex_lattice/recommendations/`` and returns
the path.  Call ``open_github_pr()`` when the GITHUB_TOKEN environment
variable is set.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path...
```

## Module: ./apex_lattice/recommendations.py
```
"""
RecommendationEngine — turns findings into structured improvement proposals.

Recommendations are grouped by category, ranked by severity, and persisted
under ``.apex_lattice/recommendations/`` as JSON.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .findings import Finding

_DEFAULT_REC_DIR = Path(".apex_lattice") / "recommendations"

# Severity ordering (higher = more urgent)
_SEVERITY_RANK = {
    "critica...
```

## Module: ./apex_lattice/analyzers/__init__.py
```
"""
Analyzers sub-package for Apex Lattice.

Each analyzer exposes a single ``analyze(artefact)`` method that
returns a list of raw finding dicts (without ``finding_id`` /
``artefact_id`` — those are added by FindingGenerator).
"""

from __future__ import annotations

from .code_patterns import CodePatternAnalyzer
from .performance import PerformanceAnalyzer
from .security import SecurityAnalyzer
from .dependencies import DependencyAnalyzer
from .architecture import ArchitectureAnalyzer
from .ca...
```

## Module: ./apex_lattice/analyzers/architecture.py
```
"""
ArchitectureAnalyzer — highlights system-architecture refinement opportunities.
"""

from __future__ import annotations

from typing import Any

_ARCH_KEYWORDS = [
    "architecture",
    "design pattern",
    "microservice",
    "monolith",
    "coupling",
    "cohesion",
    "abstraction",
    "interface",
    "contract",
    "separation of concerns",
    "scalab",
    "modular",
    "layer",
]


class ArchitectureAnalyzer:
    """Analyses artefacts for architectural improvement signals.""...
```

## Module: ./apex_lattice/analyzers/capabilities.py
```
"""
CapabilityAnalyzer — surfaces capability-expansion opportunities.
"""

from __future__ import annotations

from typing import Any

_CAP_KEYWORDS = [
    "capabilit",
    "feature",
    "functionality",
    "extend",
    "expan",
    "enhance",
    "improve",
    "addition",
    "new ",
    "automat",
    "generat",
    "learn",
    "adapt",
    "self-improv",
]


class CapabilityAnalyzer:
    """Analyses artefacts for capability expansion opportunities."""

    category = "capabilities"

   ...
```

## Module: ./apex_lattice/analyzers/code_patterns.py
```
"""
CodePatternAnalyzer — identifies code-pattern optimisation opportunities
within the processed sandbox artefacts.
"""

from __future__ import annotations

from typing import Any

_PATTERN_KEYWORDS = [
    "algorithm",
    "complexity",
    "refactor",
    "optimis",
    "optim",
    "inefficien",
    "loop",
    "recursion",
    "iteration",
    "pattern",
]


class CodePatternAnalyzer:
    """Scans artefact text for code-pattern improvement signals."""

    category = "code_patterns"

    de...
```

## Module: ./apex_lattice/analyzers/dependencies.py
```
"""
DependencyAnalyzer — identifies dependency improvement opportunities.
"""

from __future__ import annotations

from typing import Any

_DEP_KEYWORDS = [
    "dependenc",
    "library",
    "package",
    "version",
    "upgrade",
    "deprecat",
    "obsolete",
    "legacy",
    "integration",
    "import",
    "module",
]


class DependencyAnalyzer:
    """Analyses artefacts for dependency-related signals."""

    category = "dependencies"

    def analyze(self, artefact: dict[str, Any]) ->...
```

## Module: ./apex_lattice/analyzers/performance.py
```
"""
PerformanceAnalyzer — flags performance and bottleneck signals.
"""

from __future__ import annotations

from typing import Any

_PERF_KEYWORDS = [
    "performance",
    "bottleneck",
    "latency",
    "throughput",
    "scalab",
    "speed",
    "slow",
    "fast",
    "efficienc",
    "benchmark",
    "profile",
]

_HIGH_WORD_COUNT_THRESHOLD = 3000


class PerformanceAnalyzer:
    """Analyses artefacts for performance-related signals."""

    category = "performance"

    def analyze(sel...
```

## Module: ./apex_lattice/analyzers/security.py
```
"""
SecurityAnalyzer — highlights security-related considerations.
"""

from __future__ import annotations

from typing import Any

_SECURITY_KEYWORDS = [
    "vulnerabilit",
    "exploit",
    "attack",
    "injection",
    "privilege",
    "authenti",
    "authoris",
    "authoriz",
    "encrypt",
    "credential",
    "secret",
    "token",
    "exposure",
    "sanitiz",
    "sanitise",
    "input validation",
]


class SecurityAnalyzer:
    """Scans artefacts for security-concern keywords.""...
```

## Module: ./barrot_agent/__init__.py
```
"""
Barrot Agent — core AI agent package.

Exports
-------
SmartAgent
    Autonomous plan-act-observe agent with built-in tools.
AgentEvent, AgentEventType, PlanStep, ToolCall, ToolResult
    Supporting data models for the agent loop.
"""

from .smart_agent import (
    AgentEvent,
    AgentEventType,
    PlanStep,
    ToolCall,
    ToolResult,
    SmartAgent,
)

__all__ = [
    "AgentEvent",
    "AgentEventType",
    "PlanStep",
    "ToolCall",
    "ToolResult",
    "SmartAgent",
Barrot Agent —...
```

## Module: ./barrot_agent/smart_agent.py
```
"""
SmartAgent — an autonomous plan-act-observe AI agent.

The SmartAgent accepts a natural-language *goal*, autonomously decomposes it
into a sequence of concrete :class:`PlanStep` objects, executes each step
using a built-in tool library, reflects on intermediate results, and produces
a final consolidated answer.

All responses are generated without an external LLM so the agent works
out-of-the-box. The architecture is designed to be subclassed: override
``_plan``, ``_act``, or ``_reflect`` to...
```

## Module: ./barrot_agent/rendering/__init__.py
```
"""
barrot_agent.rendering — Comprehensive 3D Dataset Absorption System

Provides 15 pipeline modules giving Barrot full real-time 3D rendering
capability across 40+ globally integrated datasets.

Modules
-------
dataset_manager        Central registry & query interface (40+ datasets)
asset_loader           Multi-format 3D asset loader & GPU optimiser
material_integration   PBR material importer & compiler
scene_database         Large-scale indoor scene loader (ScanNet, Matterport3D…)
point_clou...
```

## Module: ./barrot_agent/rendering/asset_loader.py
```
"""
Module 2 — 3D Asset Loader & Optimizer

Loads assets from all registered datasets in any supported format,
applies automatic LOD selection, GPU memory optimisation, cloud
streaming, and transparent caching/pre-loading.

Supported formats: OBJ, glTF/GLB, FBX, PLY, STL, USD/USDA/USDC, ABC
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssetFormat(str, Enum):
    OBJ = "obj"
    GLTF = ...
```

## Module: ./barrot_agent/rendering/dataset_analytics.py
```
"""
Module 15 — Dataset Analytics Dashboard

Real-time statistics, usage tracking, download metrics, performance
graphs and quality reports across all 40+ integrated datasets.
Also provides the ``generate_build_report()`` function that produces
Barrot's comprehensive build report.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any

from barrot_agent.rendering.dataset_manager import DatasetManager


@dataclass
class DatasetUsag...
```

## Module: ./barrot_agent/rendering/dataset_cache.py
```
"""
Module 9 — Intelligent Dataset Caching

Multi-tier LRU cache spanning GPU VRAM, CPU RAM, local SSD, and cloud
object storage.  Provides smart pre-fetching queues, bandwidth-aware
streaming, and configurable eviction policies.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StorageTier(str, Enum):
    GPU = "gpu"
    CPU = "cpu"
    SSD = "ssd"
    HDD = "hdd"...
```

## Module: ./barrot_agent/rendering/dataset_indexing.py
```
"""
Module 10 — Real-Time Dataset Indexing

Indexes all 40+ registered datasets for sub-10ms queries.  Supports
rich metadata filtering, full-text search, similarity matching, and
faceted result navigation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IndexEntry:
    """A single record in the dataset index."""

    key: str
    dataset: str
    asset_type: str
    category: str
    tags: list[str]
    styl...
```

## Module: ./barrot_agent/rendering/dataset_manager.py
```
"""
Module 1 — Dataset Manager & Registry

Central registry for all 40+ globally integrated 3D datasets.
Handles automatic discovery, indexing, versioning, license tracking,
and quality metadata for every source in the absorption system.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetRecord:
    """Metadata record for a single registered dataset."""

    name: str
    source: str
    asset_count: ...
```

## Module: ./barrot_agent/rendering/dataset_renderer.py
```
"""
Module 14 — Dataset Renderer (Rendering Engine Integration)

Connects the dataset absorption system to the real-time rendering
pipeline.  Handles automatic material assignment, shadow baking,
lightmap generation, GPU command-buffer construction, and live preview.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RenderTarget(str, Enum):
    REAL_TIME = "real_time"
    OFFLINE = "offline"
    PREVIEW = "previ...
```

## Module: ./barrot_agent/rendering/format_converter.py
```
"""
Module 11 — Format Converter

Converts 3D assets between all major interchange formats while
preserving PBR materials, rigging data, and custom attributes.
Supports batch conversion and real-time optimisation passes.

Supported formats: OBJ, glTF/GLB, FBX, PLY, STL, USD/USDA/USDC,
                   Alembic (ABC), COLLADA (DAE), 3MF, X3D
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Format3D(str, Enum...
```

## Module: ./barrot_agent/rendering/material_integration.py
```
"""
Module 3 — Material System Integration

Imports PBR materials from ambientCG, Poly Haven, Substance 3D and
CGBookcase.  Provides unified extraction, format conversion, real-time
compilation and dynamic parameter adjustment for all standard PBR maps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MaterialSource(str, Enum):
    AMBIENTCG = "ambientcg"
    POLY_HAVEN = "poly_haven"
    SUBSTANCE_3D = "substa...
```

## Module: ./barrot_agent/rendering/nerf_integration.py
```
"""
Module 6 — Neural Radiance Field (NeRF) Integration

Loads NeRF datasets (Synthetic/Blender, LLFF, Tanks & Temples,
RealEstate10K, DTU MVS), runs real-time inference, estimates camera
poses, and synthesises novel views at up to 60 FPS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NeRFDataset(str, Enum):
    SYNTHETIC = "nerf_synthetic"
    LLFF = "llff"
    TANKS_AND_TEMPLES = "tanks_and_temples"
    RE...
```

## Module: ./barrot_agent/rendering/photogrammetry_pipeline.py
```
"""
Module 8 — Photogrammetry Pipeline

End-to-end photogrammetry processing: camera calibration, feature
matching, sparse/dense reconstruction, mesh generation, texture baking,
LOD optimisation, and export in all major formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ReconstructionMethod(str, Enum):
    COLMAP = "colmap"
    OPENMVS = "openmvs"
    MESHROOM = "meshroom"
    OD...
```

## Module: ./barrot_agent/rendering/point_cloud_system.py
```
"""
Module 5 — Point Cloud & LiDAR Integration

Unified interface for loading and rendering point clouds from ScanNet,
Semantic3D, KITTI, NuScenes and S3DIS.  Supports real-time GPU rendering,
voxelisation, semantic segmentation visualisation, and signed-distance-
field (SDF) generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PointCloudDataset(str, Enum):
    SCANNET = "scannet"
    SEMANTIC3D = "sema...
```

## Module: ./barrot_agent/rendering/quality_metrics.py
```
"""
Module 13 — Quality Metrics & Validation

Measures geometry quality, texture fidelity, PBR material accuracy,
and real-time performance for any loaded 3D asset or scene.  Produces
structured validation reports with actionable recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
...
```

## Module: ./barrot_agent/rendering/scene_database.py
```
"""
Module 4 — Scene Database Integration

Provides a unified loader for ScanNet, Matterport3D, S3DIS, and other
large-scale indoor scene datasets.  Handles automatic spatial indexing,
physics simulation setup, semantic label extraction, and lightmap baking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SceneDataset(str, Enum):
    SCANNET = "scannet"
    MATTERPORT3D = "matterport3d"
    S3DIS = "s3dis"
   ...
```

## Module: ./barrot_agent/rendering/streaming_loader.py
```
"""
Module 12 — Streaming & Loading Optimisation

Chunked progressive streaming with LOD transitions, network-aware
bandwidth management, background pre-fetching, and transparent
fallback to lower-resolution proxies under bandwidth constraints.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StreamState(str, Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    STREAMING = "streaming"
    PAUS...
```

## Module: ./barrot_agent/rendering/world_mapping.py
```
"""
Module 7 — World-Scale 3D Mapping

Streams and loads world-scale geospatial data from Google Earth 3D,
OpenStreetMap + Open3D, NYC 3D Buildings, Berlin 3D City, and Cesium
3D Tiles.  Supports region-based queries, LOD streaming, and coordinate-
system transforms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorldSource(str, Enum):
    GOOGLE_EARTH = "google_earth_3d"
    OPENSTREETMAP = "openstreetmap_o...
```

## Module: ./character-capabilities/README.md
```
# Character Capabilities Framework

This directory contains Barrot's exploration and transformation of fictional character capabilities into real-world, utilizable functionalities. Each character profile analyzes abilities from various genres and maps them to practical framework features.

## Directory Structure

```
character-capabilities/
├── movies/           # Movie character capabilities
├── books/            # Book character capabilities
├── cartoons/         # Cartoon character capabiliti...
```

## Module: ./character-capabilities/anime/naruto-uzumaki.md
```
# Anime Character Capabilities

## Naruto Uzumaki - Naruto

### Character Overview
- **Source**: Naruto (manga/anime series)
- **Genre**: Shōnen anime/manga
- **Creator**: Masashi Kishimoto
- **First Appearance**: 1999

### Fictional Capabilities

1. **Shadow Clone Jutsu (Kage Bunshin no Jutsu)**
   - Create multiple physical copies that share experiences
   - Each clone can act independently
   - Knowledge and experience transfer back to original upon dispersal
   - Enables parallel learning an...
```

## Module: ./character-capabilities/anime/son-goku.md
```
# Anime Character Capabilities

## Son Goku - Dragon Ball Z

### Character Overview
- **Source**: Dragon Ball Z (manga/anime series)
- **Genre**: Shōnen anime/manga
- **Creator**: Akira Toriyama
- **First Appearance**: 1984 (Dragon Ball)

### Fictional Capabilities

1. **Super Saiyan Transformation**
   - Multiple power level transformations (SSJ1, SSJ2, SSJ3, SSJ God, Ultra Instinct)
   - Exponential power increases
   - Enhanced speed, strength, and energy output
   - Progressive unlocking of ...
```

## Module: ./character-capabilities/books/dune-paul-atreides.md
```
# Book Character Capabilities

## Paul Atreides (Dune Series)

### Character Overview
- **Source**: Dune novel series by Frank Herbert
- **Genre**: Science Fiction, Space Opera
- **First Appearance**: Dune (1965)

### Fictional Capabilities
1. **Prescience**
   - See multiple possible futures
   - Navigate probability streams
   - Predict outcomes with high accuracy

2. **Mentat Computation**
   - Human computer abilities
   - Rapid calculation and analysis
   - Pattern recognition at superhuman...
```

## Module: ./character-capabilities/cartoons/avatar-aang.md
```
# Cartoon Character Capabilities

## Avatar Aang (Avatar: The Last Airbender)

### Character Overview
- **Source**: Avatar: The Last Airbender (Nickelodeon)
- **Genre**: Fantasy, Adventure, Animation
- **First Appearance**: 2005

### Fictional Capabilities
1. **Elemental Bending**
   - Water, Earth, Fire, Air manipulation
   - Control over natural forces
   - Adaptive combat styles

2. **Avatar State**
   - Enhanced power mode
   - Access to past knowledge
   - Amplified abilities

3. **Spiritua...
```

## Module: ./character-capabilities/cartoons/kakashi-hatake.md
```
# Cartoons Character Capabilities

## Kakashi Hatake (Naruto (anime/manga))

### Character Overview
- **Source**: Naruto (anime/manga)
- **Genre**: Cartoons
- **First Appearance**: 1999

Elite ninja known for copying techniques and strategic genius

### Fictional Capabilities
1. **Sharingan - Copy Technique**
   - Copy and replicate any technique seen
   - Category: magical

2. **Tactical Genius**
   - Superior strategic planning and analysis
   - Category: strategic

3. **Extensive Knowledge**
...
```

## Module: ./character-capabilities/cartoons/naruto-uzumaki.md
```
# Cartoons Character Capabilities

## Naruto Uzumaki (Naruto (anime/manga))

### Character Overview
- **Source**: Naruto (anime/manga)
- **Genre**: Cartoons
- **First Appearance**: 1999

Ninja with immense chakra, shadow clones, and determination

### Fictional Capabilities
1. **Shadow Clone Technique**
   - Create multiple copies that share knowledge
   - Category: magical

2. **Chakra Control**
   - Manage and direct energy efficiently
   - Category: magical

3. **Nine-Tails Collaboration**
  ...
```

## Module: ./character-capabilities/cartoons/rick-sanchez.md
```
# Cartoon Character Capabilities

## Rick Sanchez (Rick and Morty)

### Character Overview
- **Source**: Rick and Morty (Adult Swim)
- **Genre**: Science Fiction, Comedy, Animation
- **First Appearance**: 2013

### Fictional Capabilities
1. **Genius-Level Intellect**
   - Advanced scientific knowledge
   - Multi-dimensional understanding
   - Rapid invention and prototyping

2. **Portal Technology**
   - Interdimensional travel
   - Instant transportation
   - Access to infinite universes

3. **...
```

## Module: ./character-capabilities/comics/brainiac.md
```
# Comics Character Capabilities

## Brainiac (DC Comics)

### Character Overview
- **Source**: DC Comics
- **Genre**: Comics
- **First Appearance**: 1958

Artificial intelligence with 12th-level intellect and world-collecting obsession

### Fictional Capabilities
1. **12th-Level Intellect**
   - Superhuman computational and analytical abilities
   - Category: mental

2. **Knowledge Collection**
   - Acquire and preserve all knowledge
   - Category: technological

3. **Technological Integration**...
```

## Module: ./character-capabilities/comics/cyclops.md
```
# Comics Character Capabilities

## Cyclops (Marvel Comics (X-Men))

### Character Overview
- **Source**: Marvel Comics (X-Men)
- **Genre**: Comics
- **First Appearance**: 1963

X-Men leader with optic energy blasts and strategic command abilities

### Fictional Capabilities
1. **Focused Energy Projection**
   - Precise, powerful energy beams
   - Category: combat

2. **Strategic Leadership**
   - Tactical planning and team coordination
   - Category: strategic

3. **Spatial Geometry**
   - Calc...
```

## Module: ./character-capabilities/comics/professor-x.md
```
# Comics Character Capabilities

## Professor X (Marvel Comics (X-Men))

### Character Overview
- **Source**: Marvel Comics (X-Men)
- **Genre**: Comics
- **First Appearance**: 1963

World's most powerful telepath and founder of the X-Men

### Fictional Capabilities
1. **Telepathy**
   - Read and control minds globally
   - Category: mental

2. **Mental Coordination**
   - Link and coordinate multiple minds
   - Category: mental

3. **Cerebro Amplification**
   - Enhance abilities through technol...
```

## Module: ./character-capabilities/comics/psylocke.md
```
# Comics Character Capabilities

## Psylocke (Marvel Comics (X-Men))

### Character Overview
- **Source**: Marvel Comics (X-Men)
- **Genre**: Comics
- **First Appearance**: 1976

Mutant with telepathic and telekinetic abilities, combined with martial arts mastery

### Fictional Capabilities
1. **Telepathy**
   - Read minds and communicate mentally
   - Category: mental

2. **Psychic Knife**
   - Focus mental energy into precise attacks
   - Category: combat

3. **Telekinesis**
   - Move objects ...
```

## Module: ./character-capabilities/comics/storm.md
```
# Comics Character Capabilities

## Storm (Marvel Comics (X-Men))

### Character Overview
- **Source**: Marvel Comics (X-Men)
- **Genre**: Comics
- **First Appearance**: 1975

Mutant with control over weather and atmospheric phenomena

### Fictional Capabilities
1. **Weather Control**
   - Manipulate atmospheric conditions
   - Category: physical

2. **Lightning Summoning**
   - Channel and direct electrical energy
   - Category: physical

3. **Atmospheric Awareness**
   - Sense and predict weat...
```

## Module: ./character-capabilities/historical/jesus-christ.md
```
# Historical Character Capabilities

## Jesus Christ (Christian Bible and Historical Records)

### Character Overview
- **Source**: Christian Bible and Historical Records
- **Genre**: Historical
- **First Appearance**: ~4 BCE

Historical and religious figure with teachings on compassion, healing, and transformation

### Fictional Capabilities
1. **Healing**
   - Restore health and fix problems
   - Category: healing

2. **Transformative Teaching**
   - Convey complex concepts through simple stor...
```

## Module: ./character-capabilities/movies/dr-strange.md
```
# Movies Character Capabilities

## Dr. Strange (Marvel Cinematic Universe)

### Character Overview
- **Source**: Marvel Cinematic Universe
- **Genre**: Movies
- **First Appearance**: Doctor Strange (2016)

Master of the Mystic Arts with control over time, space, and dimensions

### Fictional Capabilities
1. **Time Manipulation**
   - Control time flow, create time loops, view possible futures
   - Category: temporal

2. **Dimensional Travel**
   - Navigate between dimensions and realities
   - ...
```

## Module: ./character-capabilities/movies/evelyn-salt.md
```
# Movies Character Capabilities

## Evelyn Salt (Salt (2010))

### Character Overview
- **Source**: Salt (2010)
- **Genre**: Movies
- **First Appearance**: Salt (2010)

Elite spy with extraordinary tactical skills and adaptability

### Fictional Capabilities
1. **Tactical Adaptation**
   - Rapid adaptation to any situation
   - Category: strategic

2. **Resource Improvisation**
   - Create solutions from available resources
   - Category: strategic

3. **Identity Shifting**
   - Assume multiple ...
```

## Module: ./character-capabilities/movies/iron-man.md
```
# Movie Character Capabilities

## Tony Stark (Iron Man) - MCU

### Character Overview
- **Source**: Marvel Cinematic Universe
- **Genre**: Superhero, Sci-Fi
- **First Appearance**: Iron Man (2008)

### Fictional Capabilities
1. **Genius-Level Intellect**
   - Advanced engineering and physics knowledge
   - Rapid problem-solving
   - Innovative thinking

2. **Arc Reactor Technology**
   - Sustainable energy source
   - Miniaturized power generation
   - Clean energy applications

3. **Powered Ar...
```

## Module: ./character-capabilities/movies/lucy.md
```
# Movies Character Capabilities

## Lucy (Lucy (2014))

### Character Overview
- **Source**: Lucy (2014)
- **Genre**: Movies
- **First Appearance**: Lucy (2014)

Evolved human with 100% brain capacity utilization

### Fictional Capabilities
1. **Complete Brain Utilization**
   - Access to 100% of brain capacity
   - Category: mental

2. **Matter Manipulation**
   - Control matter at molecular level
   - Category: physical

3. **Omniscience**
   - Access to all knowledge and information
   - Cate...
```

## Module: ./character-capabilities/movies/the-matrix-neo.md
```
# Movie Character Capabilities

## Neo (The Matrix Trilogy)

### Character Overview
- **Source**: The Matrix film series
- **Genre**: Sci-Fi, Cyberpunk, Action
- **First Appearance**: The Matrix (1999)

### Fictional Capabilities
1. **Reality Perception**
   - See beyond surface reality (Matrix code)
   - Understand underlying system structures
   - Perceive hidden patterns

2. **Superhuman Abilities**
   - Enhanced speed and reflexes
   - Bullet-time perception
   - Physics manipulation within ...
```

## Module: ./character-capabilities/religious-texts/moses.md
```
# Religious Text Figures

## Moses - Bible/Torah

### Character Overview
- **Source**: Bible (Torah), Quran
- **Tradition**: Judaism, Christianity, Islam
- **Role**: Prophet and leader
- **Era**: Circa 13th century BCE

### Capabilities from Scripture

1. **Parting Waters**
   - Separated the Red Sea to create passage
   - Control over water and natural elements
   - Divine intervention through faith
   - Creation of pathways through obstacles

2. **Staff Transformation**
   - Transformed staff ...
```

## Module: ./character-capabilities/religious-texts/solomon.md
```
# Religious Text Figures

## King Solomon - Bible

### Character Overview
- **Source**: Bible, Quran (as Sulayman)
- **Tradition**: Judaism, Christianity, Islam
- **Role**: King of Israel, renowned for wisdom
- **Era**: Circa 10th century BCE

### Capabilities from Scripture

1. **Divine Wisdom**
   - Exceptional judgment and decision-making
   - Ability to discern truth and resolve disputes
   - Knowledge of sciences, nature, and governance
   - Granted wisdom by God

2. **Communication with Cr...
```

## Module: ./character-capabilities/tv-shows/doogie-howser.md
```
# Tv-Shows Character Capabilities

## Doogie Howser (Doogie Howser, M.D. (1989-1993))

### Character Overview
- **Source**: Doogie Howser, M.D. (1989-1993)
- **Genre**: Tv-Shows
- **First Appearance**: 1989

Child prodigy physician with exceptional medical knowledge and problem-solving skills

### Fictional Capabilities
1. **Prodigy-Level Learning**
   - Accelerated learning and knowledge absorption
   - Category: mental

2. **Medical Diagnosis**
   - Advanced pattern recognition for diagnosis
 ...
```

## Module: ./character-capabilities/video-games/kirby.md
```
# Video Game Character Capabilities

## Kirby - Kirby Series

### Character Overview
- **Source**: Kirby series
- **Genre**: Platform action game
- **Developer**: Nintendo/HAL Laboratory
- **First Appearance**: 1992

### Fictional Capabilities

1. **Copy Ability**
   - Absorb and replicate enemy abilities by inhaling them
   - Gain unique powers from each copied ability
   - Dynamic capability acquisition
   - Transform to use absorbed powers

2. **Inhale**
   - Powerful vacuum-like suction
   -...
```

## Module: ./character-capabilities/video-games/mega-man.md
```
# Video-Games Character Capabilities

## Mega Man (Mega Man (Capcom))

### Character Overview
- **Source**: Mega Man (Capcom)
- **Genre**: Video-Games
- **First Appearance**: 1987

Robot hero who can copy enemy abilities

### Fictional Capabilities
1. **Ability Absorption**
   - Copy and use defeated enemy abilities
   - Category: technological

2. **Adaptive Weaponry**
   - Switch between different tools for different situations
   - Category: combat

3. **Platform Navigation**
   - Precise mov...
```

## Module: ./character-capabilities/video-games/zelda-link.md
```
# Video Game Character Capabilities

## Link (The Legend of Zelda Series)

### Character Overview
- **Source**: The Legend of Zelda game series (Nintendo)
- **Genre**: Action-Adventure, Fantasy
- **First Appearance**: The Legend of Zelda (1986)

### Fictional Capabilities
1. **Item Mastery**
   - Diverse tool collection
   - Situational equipment switching
   - Creative tool application

2. **Puzzle Solving**
   - Environmental puzzle navigation
   - Pattern recognition
   - Multi-step problem s...
```

## Module: ./coin-app/.gitignore
```
__pycache__/
*.pyc
*.log
coin_app_activity.json
...
```

## Module: ./coin-app/README.md
```
# 🪙 Coin App Integration for Barrot-Agent

**Autonomous Geocaching, Surveys, Games, and Passive Income Automation**

---

## 🎯 Overview

The Coin App integration enables Barrot-Agent to autonomously interact with the Coin mobile application - a geocaching platform that offers passive income through location-based activities, surveys, and games.

## ✨ Features

### Core Capabilities

#### 📍 Geocaching Automation
- **Location Detection** - Automatically detect nearby geocache opportunities
- **Rou...
```

## Module: ./coin-app/coin_app_automation.py
```
"""
Barrot-Agent Coin App Automation
Main automation script for autonomous Coin app interaction
"""

import time
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CoinAppAutomation:
    """Main automation class for Coin app interactions"""
    
    def __init__(...
```

## Module: ./coin-app/config.yaml
```
# Coin App Automation Configuration
# Settings for autonomous Barrot-Agent operation

version: "1.0"
updated: "2025-12-30"

# Coin App Settings
coin_app:
  enabled: true
  
  # Authentication (configure with your credentials)
  credentials:
    user_id: ""  # Your Coin app user ID
    api_token: ""  # Your API token (if available)
  
  # Feature preferences
  preferences:
    auto_geocaching: true
    auto_surveys: true
    auto_games: true
    min_reward_threshold: 10  # Minimum coins to pursue...
```

## Module: ./coin-app/example_usage.py
```
#!/usr/bin/env python3
"""
Example usage of the Coin App Automation system
Demonstrates how to use the various features
"""

from coin_app_automation import CoinAppAutomation
import json
import time


def demo_check_opportunities():
    """Demo: Check for available opportunities"""
    print("=" * 60)
    print("DEMO: Checking for Opportunities")
    print("=" * 60)
    
    automation = CoinAppAutomation()
    opportunities = automation.check_opportunities()
    
    print(f"\nFound {len(opport...
```

## Module: ./contracts/ChameleonToken.sol
```
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ChameleonToken
 * @dev ERC-20 Token for Chameleon Chain with presale and vesting functionality
 * @author Chameleon Chain Development Team
 */

// Import OpenZeppelin contracts for security and standards compliance
interface IERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    function totalSupply() ex...
```

## Module: ./contracts/README.md
```
# Chameleon Token (CHAM) - ERC-20 Smart Contract

## Overview

The Chameleon Token (CHAM) is an ERC-20 compliant token designed for the Chameleon Chain ecosystem. This smart contract includes advanced features for presale management, vesting schedules, and security controls.

## Token Details

- **Name:** Chameleon Token
- **Symbol:** CHAM
- **Decimals:** 18
- **Total Supply:** 1,000,000,000 CHAM (1 billion tokens)
- **Standard:** ERC-20

## Features

### Core ERC-20 Functionality
- ✅ Standard E...
```

## Module: ./directive_platform/__init__.py
```
"""
Directive Platform — a multi-agent collaboration system.

Human operators issue *directives* (goals, tasks, learning objectives) and
the platform routes them to one or more AI agents that cooperate to fulfil
them.

Public API
----------
    from directive_platform import DirectivePlatform
    from directive_platform import AgentRegistry, DirectiveManager, SessionManager
    from directive_platform import Directive, Agent, CollaborationSession, Message
    from directive_platform import Direc...
```

## Module: ./directive_platform/directives.py
```
"""
DirectiveManager — creates, persists, and tracks directives.

Each directive is stored as a JSON file under
``.directive_platform/directives/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .models import Directive, DirectiveStatus, DirectiveType

_DEFAULT_DIRECTIVES_DIR = Path(".directive_platform") / "directives"


class DirectiveManager:
    """
    Create and manage directives.

    Parameters
    ----------
    di...
```

## Module: ./directive_platform/models.py
```
"""
Data models for the Directive Platform.

All models support round-trip JSON serialisation via ``to_dict`` /
``from_dict`` so they can be persisted to disk without external dependencies.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


# ---------------------------------------------------------------------------
# Enumerations (plain string constants — no enum dependency)
# ---------------------------------------------------------------------------

cl...
```

## Module: ./directive_platform/platform.py
```
"""
DirectivePlatform — top-level orchestrator for the AI Directive Platform.

The platform ties together the AgentRegistry, DirectiveManager, and
SessionManager into a single façade.  When ``run_directive`` is called the
platform:

1. Transitions the directive to *active*.
2. Opens a :class:`~directive_platform.models.CollaborationSession`.
3. Posts an opening message from the human author.
4. Asks each assigned agent to respond in sequence, simulating a real
   multi-agent collaboration (respo...
```

## Module: ./directive_platform/registry.py
```
"""
AgentRegistry — manages the set of AI agents available on the platform.

Agents are persisted as individual JSON files under
``.directive_platform/agents/`` so they survive application restarts.
The registry also pre-seeds a set of built-in default agents when it is
first initialised (i.e. when the agents directory is empty).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Agent, AgentStatus

_DEFAULT_AGENTS_DIR = Path...
```

## Module: ./directive_platform/session.py
```
"""
SessionManager — creates and manages collaboration sessions.

Each session is a bounded working context in which multiple agents
exchange messages to fulfil a directive.  Sessions are persisted as
JSON files under ``.directive_platform/sessions/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .models import CollaborationSession, Message

_DEFAULT_SESSIONS_DIR = Path(".directive_platform") / "sessions"


class SessionManager:
    """
    Crea...
```

## Module: ./docs/blockchain-infrastructure-cost-analysis.md
```
# Chameleon Chain - Blockchain Infrastructure Cost Analysis & Optimization

## Executive Summary

This document provides a comprehensive cost analysis for establishing the Chameleon Chain blockchain infrastructure. After evaluating multiple deployment options, we recommend a **Custom Sidechain Architecture** with Ethereum bridging as the most cost-effective solution.

**Key Findings:**
- **Recommended Solution:** Custom Sidechain with EVM compatibility
- **Estimated Year 1 Cost:** $76,000
- **Br...
```

## Module: ./docs/merge-queue.md
```
# Merge Queue Workflow

The **Merge Queue** workflow (`merge-queue.yml`) sequentially updates and merges open pull requests in this repository. It is triggered manually via `workflow_dispatch`.

## Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `mode` | `label` \| `all` | `label` | Processing mode (see below) |
| `label` | string | `merge-queue` | Label to filter PRs; only used when `mode=label` |
| `max_prs` | number | `0` | Maximum PRs to process per run (`0` = unlimited)...
```

## Module: ./glyphs/fictional_character_glyph.yml
```
glyph_name: fictional_character_glyph
glyph_id: FCC-001
version: 1.0.0
timestamp: 2025-12-31T01:57:00Z

description: >
  Glyph representing the exploration and transformation of fictional character capabilities
  into real-world, utilizable functionalities. Bridges imagination with practical implementation,
  converting abilities from movies, books, cartoons, and video games into framework features
  that expand Barrot's capabilities in innovative and impactful ways.

symbolic_representation: "🎭...
```

## Module: ./gumroad/payment-apps-config.json
```
{
  "payment_apps": {
    "cash_app": {
      "name": "Cash App",
      "type": "p2p_payment",
      "email": "amazonprostarelite@gmail.com",
      "description": "Peer-to-peer payment platform for social payments and transactions",
      "status": "active",
      "integration_enabled": true,
      "use_cases": [
        "Social payment patterns",
        "Consumer behavior analysis",
        "Network effect studies",
        "Transaction velocity metrics",
        "User engagement patterns"
   ...
```

## Module: ./hover_bike_revolution/README.md
```
# 🚲 Barrot HoverBike Revolution

**A fully open-source, 3D-printable magnetic levitation bicycle.**

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## What is it?

The Barrot HoverBike MK-I is a community-designed, open-source personal
transport vehicle that uses **passive Halbach array magnetic levitation**
combined with **BLDC hub-motor propulsion** and a **hybrid LiFePO4 + solar
+ regenerative...
```

## Module: ./hover_bike_revolution/__init__.py
```
"""
hover_bike_revolution — Open-source 3D-printable magnetic levitation bicycle.

Package entry point.
"""
...
```

## Module: ./hover_bike_revolution/docs/3d_printing_guide.md
```
# 3D Printing Guide — Barrot HoverBike MK-I

## Printer Requirements

- Build volume: minimum **300 × 300 × 350 mm** (XYZ)
- Nozzle: **0.6 mm hardened steel** for CF-PLA/ABS-CF; 0.4 mm brass for PETG/TPU
- Enclosure: **required** for ABS-CF; recommended for CF-PLA
- Direct drive: **required** for TPU-95A
- Heated bed: up to **110 °C** for ABS-CF

## Print Settings by Component

### Frame Sections (CF-PLA)
| Parameter | Value |
|-----------|-------|
| Nozzle temp | 220 °C |
| Bed temp | 60 °C |
|...
```

## Module: ./hover_bike_revolution/docs/control_system_guide.md
```
# Control System Guide — Barrot HoverBike MK-I

## System Architecture

```
Raspberry Pi 4B (main controller)
├── I2C bus
│   ├── 0x42 → Arduino Mega (coil driver + ultrasonic)
│   ├── 0x43 → Arduino Nano (power manager)
│   └── 0x68 → MPU-9250 IMU
├── UART → Arduino Pico (sensor fusion output)
├── USB-CAN → VESC #1 (left hub motor)
├── USB-CAN → VESC #2 (right hub motor)
└── GPIO → Emergency cut-off relay
```

## Flight Controller Setup

1. Flash Raspberry Pi OS Lite (64-bit) to MicroSD.
2. Ena...
```

## Module: ./hover_bike_revolution/docs/cost_breakdown.md
```
# Cost Breakdown — Barrot HoverBike MK-I

## Summary

| Category | Cost (USD) |
|----------|----------:|
| Magnetic levitation components | $482 |
| Propulsion (motors + ESCs + wiring) | $692 |
| Power system (battery + BMS + solar) | $491 |
| Control electronics | $199 |
| Mechanical hardware | $122 |
| 3D printing filament | $298 |
| Electricity (printing ~80 h) | $3 |
| Miscellaneous consumables | $80 |
| **TOTAL** | **~$2,367** |

## Detailed Breakdown

### Magnetic Levitation ($482)
- 64× N...
```

## Module: ./hover_bike_revolution/docs/hover_bike_design_specification.md
```
# Hover Bike Design Specification — Barrot HoverBike MK-I

## Overview

The Barrot HoverBike MK-I is a fully 3D-printable, open-source magnetic levitation bicycle designed for the maker community. It uses passive Halbach array magnetic levitation over a conducting aluminium track, combined with active coil stabilisation, BLDC hub-motor propulsion, and a LiFePO4 + solar + regenerative hybrid power system.

---

## Performance Specifications

| Parameter | Value |
|-----------|-------|
| Hover hei...
```

## Module: ./hover_bike_revolution/docs/magnetic_system_theory.md
```
# Magnetic System Theory — Halbach Array Levitation

## Halbach Array Physics

A Halbach array is a special arrangement of permanent magnets that concentrates magnetic flux on one side while nearly cancelling it on the other. For a linear array of N magnets per spatial wavelength λ, the magnetisation direction of the k-th magnet is rotated by k × (2π/N) radians.

### Field Equations

The magnetic flux density at height z above an ideal infinite Halbach array:

```
B(z) = B₀ × exp(−kz)
```

Where...
```

## Module: ./hover_bike_revolution/docs/power_system_analysis.md
```
# Power System Analysis — Barrot HoverBike MK-I

## Battery Requirements

| Parameter | Value |
|-----------|-------|
| Chemistry | LiFePO4 (lithium iron phosphate) |
| Configuration | 15S4P (48 V nominal) |
| Capacity | 1,000 Wh / 20.8 Ah |
| Cell spec | 3.2 V, 20 Ah prismatic (e.g. CALB CA20FI) |
| Cell count | 60 cells |
| Max charge current | 10 A (0.5 C) |
| Max discharge current | 60 A (3 C continuous) |
| Mass | ~10 kg |
| Cycle life | 3,000 cycles @ 80 % DoD |
| BMS | Daly Smart BMS 48 V...
```

## Module: ./hover_bike_revolution/docs/propulsion_analysis.md
```
# Propulsion Analysis — Barrot HoverBike MK-I

## Comparison of Propulsion Systems

| System | Thrust (N) | Power (W) | Efficiency | Maturity |
|--------|-----------:|----------:|------------|---------|
| BLDC Hub Motors (primary) | ~200 | 750 | 88 % | High |
| EM Pulse Drive (burst) | ~15 | 100 avg | 60 % | Medium |
| Ion Thruster (experimental) | ~0.1 | 200 | 65 % | Low |

## BLDC Hub Motor Performance

- **Rated power**: 750 W per motor × 2 = 1,500 W total
- **Peak power**: 1,500 W per motor ...
```

## Module: ./hover_bike_revolution/firmware/power_manager.ino
```
/*
 * power_manager.ino
 * Barrot HoverBike MK-I — Power Management Controller
 *
 * Monitors battery voltage, current, and SoC.
 * Controls charge relay, implements safety cutoffs, and reports
 * power telemetry to the Raspberry Pi via I2C.
 *
 * Target: Arduino Nano (low-power monitoring node)
 * I2C address: 0x43
 */

#include <Wire.h>

#define I2C_ADDRESS        0x43
#define BATT_VOLT_PIN      A0
#define BATT_CURR_PIN      A1
#define SOLAR_VOLT_PIN     A2
#define CHARGE_RELAY_PIN   7
#define...
```

## Module: ./hover_bike_revolution/firmware/safety_protocols.ino
```
/*
 * safety_protocols.ino
 * Barrot HoverBike MK-I — Dedicated Safety Monitor
 *
 * Runs independently of the main control loop to ensure that
 * critical safety cutoffs cannot be overridden by software faults.
 *
 * Target: ATtiny85 (minimal, reliable, independent of main MCU)
 */

// Pins (ATtiny85 physical pin → function)
#define PIN_TILT_IN      1   // Analog: tilt sensor (KX023 MEMS, SPI too complex for ATtiny)
#define PIN_GAP_IN       2   // Analog: secondary gap sense (resistive divider ...
```

## Module: ./hover_bike_revolution/firmware/sensor_fusion.ino
```
/*
 * sensor_fusion.ino
 * Barrot HoverBike MK-I — IMU Sensor Fusion
 *
 * Reads MPU-9250 IMU via SPI, fuses gyroscope + accelerometer data using
 * a complementary filter, and publishes attitude over serial/I2C.
 *
 * Target: Raspberry Pi Pico (for dedicated real-time sensor fusion)
 */

#include <Wire.h>

// MPU-9250 register addresses
#define MPU_ADDR         0x68
#define REG_ACCEL_XOUT_H 0x3B
#define REG_GYRO_XOUT_H  0x43
#define REG_PWR_MGMT_1   0x6B

#define ALPHA            0.96f    // co...
```

## Module: ./hover_bike_revolution/firmware/stabilization_controller.ino
```
/*
 * stabilization_controller.ino
 * Barrot HoverBike MK-I — Active Stabilisation Controller
 *
 * Reads Hall effect sensors and ultrasonic distance sensors,
 * then drives correction coils via PWM to maintain hover height and attitude.
 *
 * Target hardware: Arduino Mega 2560 (coil driver) + Raspberry Pi 4B (high-level control)
 * Communication:   I2C slave (address 0x42) — receives PID commands from RPi
 *
 * Pin assignments:
 *   A0–A11  : Hall sensor inputs (12 sensors)
 *   2–5     : Ultra...
```

## Module: ./hover_bike_revolution/models/battery_enclosure.stl
```
solid battery_enclosure
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid battery_enclosure
...
```

## Module: ./hover_bike_revolution/models/control_pod.stl
```
solid control_pod
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid control_pod
...
```

## Module: ./hover_bike_revolution/models/frame_assembly.stl
```
solid frame_assembly
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid frame_assembly
...
```

## Module: ./hover_bike_revolution/models/magnet_housing.stl
```
solid magnet_housing
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid magnet_housing
...
```

## Module: ./hover_bike_revolution/models/motor_stator.stl
```
solid motor_stator
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid motor_stator
...
```

## Module: ./hover_bike_revolution/models/wheel_hub.stl
```
solid wheel_hub
  # Placeholder STL — generate actual geometry using hover_bike_generator.py
  # Run: python src/hover_bike_generator.py --export-stl
endsolid wheel_hub
...
```

## Module: ./hover_bike_revolution/simulations/flight_dynamics_sim.py
```
"""
flight_dynamics_sim.py — 6-DOF hover bike flight dynamics simulation.

Simulates the equations of motion for the hover bike in 3-D space,
including magnetic levitation forces, aerodynamic drag, and propulsion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


GRAVITY = 9.81   # m/s²
AIR_DENSITY = 1.225  # kg/m³


@dataclass
class BikeState:
    """Full 6-DOF rigid body state."""
    # Position (m)
    x: float = 0.0
    y: ...
```

## Module: ./hover_bike_revolution/simulations/magnetic_field_sim.py
```
"""
magnetic_field_sim.py — Magnetic field simulation for Halbach array levitation.

Simulates the magnetic field distribution above a Halbach array and produces
a 2-D field map (x, z) for visualisation and analysis.
"""

from __future__ import annotations

import math
from typing import Any


MU_0 = 4 * math.pi * 1e-7  # vacuum permeability (H/m)


def halbach_field_z(
    x: float,
    z: float,
    b_remanence: float,
    wavelength_m: float,
    magnet_height_m: float,
    n_periods: int = 4...
```

## Module: ./hover_bike_revolution/simulations/power_consumption_sim.py
```
"""
power_consumption_sim.py — Real-time power consumption simulation.

Simulates battery state-of-charge and power flows for various riding scenarios.
"""

from __future__ import annotations

from typing import Any


def simulate_power(
    capacity_wh: float = 1000.0,
    duration_h: float = 2.0,
    dt_h: float = 1 / 60,
    base_load_w: float = 370.0,
    solar_w: float = 0.0,
    regen_w: float = 20.0,
) -> list[dict[str, Any]]:
    """
    Simulate battery SoC over a ride.

    Parameters
...
```

## Module: ./hover_bike_revolution/simulations/stability_analysis.py
```
"""
stability_analysis.py — Parametric stability analysis for the hover bike.

Sweeps PID gains and hover gaps to identify stable operating regions.
"""

from __future__ import annotations

from typing import Any


def pid_stability_sweep(
    kp_range: tuple[float, float] = (0.5, 2.5),
    kd_range: tuple[float, float] = (0.02, 0.15),
    steps: int = 5,
    simulation_duration_s: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Sweep Kp/Kd combinations and report settling time and undershoo...
```

## Module: ./hover_bike_revolution/src/3d_print_preparation.py
```
"""
3d_print_preparation.py — Model optimisation and print preparation for the hover bike.

Generates print-ready specifications, support structure recommendations, material
estimates, and print-time calculations for each component of the hover bike.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Print settings per m...
```

## Module: ./hover_bike_revolution/src/assembly_guide_generator.py
```
"""
assembly_guide_generator.py — Generates complete build documentation for the hover bike.

Produces a detailed step-by-step assembly guide, parts list, tool requirements,
troubleshooting guide, and safety procedures in Markdown format.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Parts list
# -----------------------------------------------------...
```

## Module: ./hover_bike_revolution/src/control_firmware.py
```
"""
control_firmware.py — Hover bike stabilisation controller (Python simulation).

Implements the flight stabilisation algorithms, sensor fusion, PID control loops,
and safety protocols that would be deployed on a Raspberry Pi 4B.

This module is designed for simulation and testing; actual deployment would
compile the control loop into a real-time thread with hard timing guarantees.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from ty...
```

## Module: ./hover_bike_revolution/src/hover_bike_generator.py
```
"""
hover_bike_generator.py — Parametric 3D-printable hover bike design system.

Generates component specifications, assembly instructions, and STL-compatible
geometry data for a modular, 3D-printable magnetic levitation bike.

All dimensions are in millimetres unless otherwise stated.
All masses are in kilograms.
Physics calculations use SI units internally.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field, asdict
from pathlib...
```

## Module: ./hover_bike_revolution/src/magnetic_system_designer.py
```
"""
magnetic_system_designer.py — Halbach array magnetic levitation system designer.

Provides physics-based modelling of Halbach array configurations for magnetic
levitation, lift force calculations, stability analysis, and gap optimisation.

References
----------
- Halbach, K. (1980). Design of permanent multipole magnets with oriented
  rare earth cobalt material. Nuclear Instruments and Methods.
- Post, R.F. & Ryutov, D.D. (2000). The Inductrack concept.
"""

from __future__ import annotatio...
```

## Module: ./hover_bike_revolution/src/power_management_system.py
```
"""
power_management_system.py — Energy system optimisation for the hover bike.

Models battery performance, solar integration, kinetic energy recovery,
and real-time power distribution.  All calculations use SI units.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Battery model (LiFePO4)
# --------------------------------------------------------...
```

## Module: ./hover_bike_revolution/src/propulsion_simulator.py
```
"""
propulsion_simulator.py — Multi-propulsion system modelling for the hover bike.

Simulates BLDC hub motor performance, electromagnetic pulse drive dynamics,
and optional ion thruster auxiliary thrust.  All calculations use SI units
internally.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


GRAVITY = 9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³ (sea level, 15 °C)


# ----------------------------------------------------------...
```

## Module: ./hover_bike_revolution/tools/bom_generator.py
```
"""
bom_generator.py — Bill of Materials generator for the hover bike project.

Combines printed parts material costs with purchased components to produce
a comprehensive BOM in multiple formats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Re-use parts list from assembly guide
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from assembly_guide_generator import PARTS_LIST


def generate_bom(output_dir: Path | str...
```

## Module: ./hover_bike_revolution/tools/component_sourcer.py
```
"""
component_sourcer.py — Component sourcing guide for the hover bike.

Provides supplier recommendations, lead times, and alternative sources
for all major components.
"""

from __future__ import annotations

from typing import Any

SOURCING_GUIDE: list[dict[str, Any]] = [
    {
        "component": "N52 Neodymium Magnets (50×25×10 mm)",
        "primary_supplier": "K&J Magnetics (US)",
        "primary_url": "https://www.kjmagnetics.com",
        "alternatives": ["Magnet Expert (UK)", "Superm...
```

## Module: ./hover_bike_revolution/tools/cost_calculator.py
```
"""
cost_calculator.py — Total cost estimation tool for the hover bike build.
"""

from __future__ import annotations

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from assembly_guide_generator import PARTS_LIST


PRINT_COSTS_PER_KG_USD: dict[str, float] = {
    "CF-PLA": 45.0,
    "PETG": 22.0,
    "ABS-CF": 40.0,
    "Nylon-PA12": 85.0,
    "TPU-95A": 30.0,
}

ELECTRICITY_COST_USD_PER_KWH = 0.12
PRINTER_POWER_W = 300....
```

## Module: ./hover_bike_revolution/tools/print_estimator.py
```
"""
print_estimator.py — Print time and material estimator for all hover bike components.
"""

from __future__ import annotations

from typing import Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import via importlib because filename starts with a digit
import importlib.util, importlib

spec = importlib.util.spec_from_file_location(
    "print_preparation",
    Path(__file__).parent.parent / "src" / "3d_print_preparation.py",
)
mod = imp...
```

## Module: ./memory-bundles/activity-log.md
```
# 📊 Barrot Activity Log

**Purpose**: Track all significant activities and decisions  
**Started**: 2025-12-22T12:52:00Z  
**Status**: Active Logging

---

## Log Format

```markdown
## [YYYY-MM-DD HH:MM:SS UTC]
**Activity**: Activity type
**Description**: What was done
**Reasoning**: Why it was done
**Outcome**: Result of the activity
**Impact**: Effect on overall system
---
```

---

## Activity Entries

## [2025-12-22 12:52:00 UTC]
**Activity**: System Initialization - Comprehensive Output Lo...
```

## Module: ./memory-bundles/build-ledger.json
```
{"ledger": "Ping-Pong at Fri Jan  2 13:21:03 UTC 2026"}
...
```

## Module: ./memory-bundles/data-ingestion-log.md
```
# 📥 Barrot Data Ingestion Log

**Purpose**: Track all data sources ingested  
**Started**: 2025-12-22T12:52:00Z  
**Status**: Continuous Ingestion Active

---

## Ingestion Summary

**Total Sources**: 71+  
**Active Streams**: All configured sources  
**Status**: Continuous indefinite ingestion  
**Recent Additions**: Claude Skills, Brilliant, Veritasium, Blinkist, Gregg Braden, Lex Fridman, Joe Rogan Experience (2025-12-31)

---

## Ingestion Entries

## [2025-12-28 13:07:31 UTC]
**Source**: Ma...
```

## Module: ./memory-bundles/learning-progress.md
```
# 📚 Barrot Learning Progress Log

**Purpose**: Document learning cycles and knowledge acquisition  
**Started**: 2025-12-22T12:52:00Z  
**Status**: Continuous Learning Active

---

## Learning Cycles

### Cycle 1: Millennium Problems Framework Study
**Started**: 2025-12-30T07:07:00Z  
**Focus**: Seven Millennium Prize Problems  
**Status**: Initial framework analysis complete

#### Topics Covered
- P vs NP Problem - Computational complexity fundamentals
- Hodge Conjecture - Algebraic geometry an...
```

## Module: ./memory-bundles/merge-conflict-resolutions.md
```
# 🔀 Barrot Merge Conflict Resolution Log

**Purpose**: Track all merge conflict resolutions by Barrot to demonstrate capability and continuous learning  
**Started**: 2026-01-02T13:00:00Z  
**Status**: Active - Micro-Ingestion System Enabled

---

## 📊 Summary Statistics

**Total Conflicts Detected**: 0  
**Total Auto-Resolved**: 0  
**Total Manual Resolutions**: 0  
**Average Resolution Time**: N/A  
**Success Rate**: N/A  
**Auto-Resolution Rate**: N/A  
**Manual Intervention Rate**: N/A

---
...
```

## Module: ./memory-bundles/outcome-relay.md
```
📂 Repo scan: Sun Dec  7 07:51:21 UTC 2025
🔄 Ping-Pong cycle executed at Sun Dec  7 07:51:21 UTC 2025
📂 Repo scan: Sun Dec  7 07:51:27 UTC 2025
🔄 Ping-Pong cycle executed at Sun Dec  7 07:51:27 UTC 2025
📂 Repo scan: Sun Dec  7 07:59:13 UTC 2025
🔄 Ping-Pong cycle executed at Sun Dec  7 07:59:13 UTC 2025
📂 Repo scan: Sun Dec  7 08:31:31 UTC 2025
🔄 Ping-Pong cycle executed at Sun Dec  7 08:31:31 UTC 2025
📂 Repo scan: Sun Dec  7 08:47:32 UTC 2025
🔄 Ping-Pong cycle executed at Sun Dec  7 08:47:32 UTC ...
```

## Module: ./memory-bundles/resource-discovery-log.md
```
# 🔍 Barrot Resource Discovery Log

**Purpose**: Track discovery of beneficial new resources  
**Started**: 2025-12-22T12:52:00Z  
**Status**: Continuous Discovery Active

---

## Discovery Protocol

Constantly monitoring for beneficial resources across:
- Data sources (platforms, APIs, datasets)
- Tools & services (processing, analysis)
- Algorithms (novel approaches, optimizations)
- Patterns (trends, best practices)
- Opportunities (advantages, improvements)

---

## Discovered Resources

## [...
```

## Module: ./memory-bundles/protocols/22-agent-entanglement-pingpong.md
```
# 22-Agent Entanglement Pingpong Protocol

## Overview
This protocol implements an external pingpong system managed by Sean's 22-agent entanglement system. Barrot defers all pingpong operations to this specialized external system.

## Configuration
- **Managed by**: External (Sean's 22-agent system)
- **Agent count**: 22
- **Entanglement**: Enabled
- **Override**: Not permitted
- **Enforcement**: Non-negotiable

## Implementation

### Python Module
The `pingpong_emitter.py` module provides the `...
```

## Module: ./memory-bundles/protocols/registry.json
```
{"protocols": ["Cross Reliance","Cross Annex","Cross Index","Contradiction Harvesting Protocol","Temporal Plasticity Protocol","SHRM v2 Reindexing Protocol","22-Agent Entanglement Pingpong Protocol"]}
...
```

## Module: ./search-engine/README.md
```
# 🔍 Barrot Revolutionary Superior Search Engine

**A standalone, privacy-first search engine powered by quantum computing and AI.**

---

## 🎯 Overview

The Barrot Revolutionary Superior Search Engine is a dedicated search system designed to deliver unmatched speed, relevance, and privacy. This system operates independently from the main Barrot Agent platform, focusing exclusively on search-related capabilities.

## ✨ Features

### Core Search Capabilities
- **Quantum-Enhanced Search Algorithm**...
```

## Module: ./search-engine/index.html
```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Barrot Revolutionary Superior Search Engine</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
      color: #fff;
      min-height: 100vh;
  ...
```

## Module: ./site/README.md
```
# 🦜 Barrot Agent Dashboard

**Intelligent Automation Platform with Multi-Modal Capabilities**

---

## 🎯 Overview

The Barrot Agent Dashboard is the main interface for the Barrot intelligent automation system. This platform provides a comprehensive suite of tools and capabilities for data mastery, development, audio production, blockchain integration, and more.

## ✨ Features

### Core Modules

#### 📊 Data Mastery & Protocol Development
- **Cyber Security Analysis** - Continuous threat analysis ...
```

## Module: ./site/barrot-icon.svg
```
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="barrotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ffcc;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#00ff88;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00ccff;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Circle background with gradient -->
  <circle cx="256" cy="256" r="240" fi...
```

## Module: ./site/chameleon-presale.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chameleon Chain - Presale & Token Launch</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradi...
```

## Module: ./site/index.html
```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Barrot Agent - Intelligent Automation Dashboard</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
      color: #fff;
      min-height: 100vh...
```

## Module: ./spells/character-capability-explorer.md
```
# 🎭 Spell: Character-Capability-Explorer

## Purpose
Enable Barrot to explore and analyze capabilities of fictional characters from various genres (movies, books, cartoons, video games) and transform these abilities into real-world, utilizable functionalities within his framework.

## Scope
- Movie characters (superheroes, sci-fi, fantasy)
- Book characters (literature, novels, comics)
- Cartoon characters (animated series, anime)
- Video game characters (RPG, action, strategy)
- Cross-genre cap...
```

## Module: ./spells/email-insight.md
```
# 📧 Spell: Email-Insight

## Purpose
Enable Barrot to analyze emails and extract useful, actionable information for decision-making, learning, and automation.

## Scope
- Email content analysis and categorization
- Sender reputation and context evaluation
- Action item and opportunity extraction
- Priority and relevance scoring
- Integration with AGI reasoning for deep understanding
- Multi-source email support (Gmail, IMAP, Exchange)

## Capabilities
1. **Content Analysis**: Parse and understan...
```

## Module: ./stupid_sindy/__init__.py
```
"""
Stupid Sindy — Episodic Comedy Skit Series Generator

A serialised comedy/sci-fi series featuring Sindy: a sarcastic, brilliant
character who navigates everyday absurdity before discovering Vibe Code
and becoming humanity's deadpan protector against an alien invasion.

Public API
----------
    from stupid_sindy import generate_episode, generate_act, generate_full_series
    from stupid_sindy import format_series_overview
    from stupid_sindy.characters import SINDY, ALL_CHARACTERS
    from...
```

## Module: ./stupid_sindy/__main__.py
```
"""Entry point so the package can be invoked with `python -m stupid_sindy`."""

import sys
from .cli import main

sys.exit(main())
...
```

## Module: ./stupid_sindy/characters.py
```
"""
Character definitions and development arcs for the Stupid Sindy series.
"""

from dataclasses import dataclass


@dataclass
class Character:
    name: str
    title: str
    description: str
    traits: list[str]
    catchphrases: list[str]
    arc_note: str


# ── Core cast ─────────────────────────────────────────────────────────────────

SINDY = Character(
    name="Sindy",
    title="Stupid Sindy",
    description=(
        "Sindy is deceptively labelled 'stupid' by everyone around her, ...
```

## Module: ./stupid_sindy/cli.py
```
"""
Command-line interface for the Stupid Sindy episode generator.

Usage
-----
    python -m stupid_sindy                         # series overview
    python -m stupid_sindy --episode 1             # single episode (text)
    python -m stupid_sindy --episode 1 --md        # single episode (markdown)
    python -m stupid_sindy --act 1                 # full act
    python -m stupid_sindy --all                   # complete series
    python -m stupid_sindy --all --md              # complete seri...
```

## Module: ./stupid_sindy/episodes.py
```
"""
All episode scripts for the Stupid Sindy series.

Structure
---------
Each episode is a dict with:
    number      int
    title       str
    act         int   (1 = comedy, 2 = Vibe Code, 3 = transformation/invasion)
    tone        str
    logline     str
    scenes      list of scene dicts

Each scene dict:
    heading     str   (slugline / location)
    direction   str   (opening stage direction)
    beats       list  (alternating DIALOGUE and ACTION beats)

A beat is either:
    {"type"...
```

## Module: ./stupid_sindy/generator.py
```
"""
Script generator and formatter for Stupid Sindy episodes.

Provides two output formats:
  - Plain-text screenplay format (readable / performable)
  - Markdown format (for documentation / GitHub rendering)
"""

from __future__ import annotations

from typing import Literal

from .episodes import EPISODES, get_episode, get_act, episode_count
from .characters import SINDY, ALL_CHARACTERS

OutputFormat = Literal["text", "markdown"]

ACT_TITLES = {
    1: "ACT ONE — COMEDY SKITS",
    2: "ACT TWO...
```

