# Barrot repository intelligence and synchronization

## Selected engine

Barrot integrates [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), an MIT-licensed local code-intelligence MCP server. Its graph connects source symbols, imports, calls, documentation, configuration, CI workflows, and supported deployment infrastructure.

The integration is an external optional executable, not vendored source code and not a new Python runtime dependency. Initial compatibility target: upstream release v0.12.1. Re-evaluate the upstream release, checksum, provenance, and license before changing the pin.

GitNexus was evaluated but not selected: its upstream repository is licensed PolyForm Noncommercial 1.0.0. Do not use it in Barrot without a separate commercial license.

## Install and configure

Install the official Codebase Memory executable separately. Verify the selected release archive against its published SHA-256 checksum and SLSA provenance before placing the executable on the Barrot runtime PATH.

Barrot does not run the upstream install script, edit another coding agent's MCP configuration, install hooks, or silently update the executable. Set BARROT_CODEBASE_MEMORY_BIN if the executable is not named codebase-memory-mcp or is outside PATH.

If the executable is absent, the adapter returns an explicit installation error. It does not download or execute an installer automatically.

## Barrot interface

The MCP adapter exposes a deliberately bounded tool set:

- index_repository: index only the configured repository root.
- sync_repository: fetch origin's default branch into remote-tracking metadata, then refresh the local graph.
- list_projects, index_status, and check_index_coverage: inspect index inventory and freshness.
- search_graph, search_code, trace_path, detect_changes, query_graph, and compare_graphs: investigate structure and change impact.
- get_graph_schema, get_architecture, get_file_outline, and get_code_snippet: inspect the graph and source structure.

The adapter does not expose project deletion or arbitrary upstream tools. Indexing uses persistence=false by default, so it does not create or commit a shared graph artifact inside B-Agent. The external graph cache remains outside the source tree.

## Synchronization contract

sync_repository performs only:

1. Read the current branch, HEAD SHA, working-tree status, and origin URL.
2. Run git fetch --no-tags origin <default-branch>.
3. Compare HEAD with the fetched remote-tracking ref.
4. Refresh the Codebase Memory index for the current checkout.
5. Return the exact local and remote SHAs, ahead/behind counts, dirty status, fetch result, and indexing result.

It never runs git pull, checkout, reset, merge, push, or branch deletion. It never overwrites local work. A result is marked synchronized=true only when the current branch is the configured default branch, the working tree is clean, HEAD exactly matches the fetched remote SHA, and indexing succeeds. Otherwise Barrot reports the mismatch and leaves the checkout untouched.

This first integration synchronizes the current checkout and its local knowledge graph. It does not yet create separate indexes for every open pull-request branch. PR/worktree indexing is a later extension that must preserve the same no-overwrite and exact-SHA rules.\n\nRefresh is on demand: Barrot invokes the upstream CLI for each sync request. This first adapter does not keep a persistent MCP session open, so Codebase Memory's session-owned auto-watch is not active yet. Continuous background watching and separate open-PR indexes are explicit follow-on work, not capabilities claimed by this release.

## Privacy and operational boundary

Codebase Memory performs source indexing locally. Its upstream security policy documents a best-effort GitHub release-metadata update check for initialized MCP sessions; Barrot uses the documented CLI interface for these calls and does not transmit source files to a hosted analysis service.

The indexer can read repository files, so run it only in a workspace Barrot is authorized to inspect. Keep the executable version pinned and independently verified. No repository source write, GitHub push, deployment, or PR merge is part of this integration.
