#!/usr/bin/env python3
"""
Barrot Databricks Job Entry Point
"""
import os
import sys
print("Barrot Databricks bundle is LIVE")
print(f"GitHub commit: {os.environ.get('GITHUB_SHA', 'local')}")
print(f"Databricks runtime: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'unknown')}")
print("Job complete.")
