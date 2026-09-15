from __future__ import annotations

import json
import re
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from .scientific_discovery import NavierStokesProblemAdapter, StaticResearchProblemAdapter

FORMAL_PROVENANCE_EXTERNAL_AI = "EXTERNAL_AI_FORMALIZATION"
DEFAULT_ANTHROPIC_FLT_ARCHIVE = "https://github.com/anthropics/fermats-last-theorem/archive/refs/heads/main.zip"


class ExternalLeanProjectImporter:
    """Import an external Lean project into Barrot's research bundle schema."""

    PROHIBITED_ESCAPES = (
        "sorry",
        "axiom",
        "native_decide",
        "unsafe",
        "extern",
        "implemented_by",
        "partial def",
        "#eval",
    )

    def build_bundle(self, project_root: str | Path, config: dict[str, Any]) -> dict[str, Any]:
        root = Path(project_root).resolve()
        formalization = self._load_optional_text(root, config.get("formalization_manifest"))
        toolchain = self._load_required_text(root, config["toolchain_file"]).strip()
        manifest = self._load_json(root, config["dependency_manifest_file"])
        theorem_targets = [self.parse_theorem_target(root, target) for target in config.get("theorem_targets", [])]
        proof_path = self.parse_proof_path(self._load_required_text(root, config["proof_path_file"]))
        comparator = self._load_json(root, config["comparator"]["config_path"])
        nanoda = self._load_json(root, config["independent_checker"]["config_path"])
        final_check = self._load_required_text(root, config["final_check_file"])
        audit = self.audit_project(
            root,
            included_paths=config.get("audit_paths", []),
            excluded_paths=config.get("audit_excluded_paths", []),
            final_check_text=final_check,
            permitted_axioms=list(config.get("permitted_axioms", [])),
        )
        mathlib_package = next((pkg for pkg in manifest.get("packages", []) if pkg.get("name") == "mathlib"), {})
        dependency_manifest = {
            "manifest_version": manifest.get("version"),
            "package_count": len(manifest.get("packages", [])),
            "packages": [
                {
                    "name": pkg.get("name"),
                    "url": pkg.get("url"),
                    "rev": pkg.get("rev"),
                    "input_rev": pkg.get("inputRev"),
                    "scope": pkg.get("scope"),
                }
                for pkg in manifest.get("packages", [])
            ],
        }
        build_command = [str(part) for part in config.get("build_command") or ["lake", "build"]]
        axiom_command = [str(part) for part in config.get("axiom_command") or []]
        comparator_command = [str(part) for part in config.get("comparator", {}).get("command") or []]
        checker_command = [str(part) for part in config.get("independent_checker", {}).get("command") or []]
        proof_nodes = self._build_claim_nodes(
            theorem_targets,
            proof_path,
            primary_claim_id=str(config["primary_claim_id"]),
            source_commit=str(config.get("source_commit") or ""),
        )
        bundle = {
            "problem": {
                "problem_id": str(config["problem_id"]),
                "title": str(config["title"]),
                "domain": str(config.get("domain") or "mathematics.formal_verification"),
                "primary_question": str(config.get("primary_question") or "Can Barrot independently reproduce the external formal verification evidence?"),
                "primary_claims": [str(config["primary_claim_id"])],
                "related_problems": list(config.get("related_problems", [])),
                "acceptance_requirements": {
                    "formal_verification_required": True,
                    "independent_verification_required": True,
                    "resolved_adversarial_reviews_required": True,
                },
            },
            "sources": [
                {
                    "source_id": "anthropic_article",
                    "title": config.get("article_title") or "Formalizing Fermat's Last Theorem",
                    "author_or_organization": config.get("origin_organization") or "Anthropic",
                    "source_type": "research_announcement",
                    "url": config.get("article_url") or "",
                    "publication_date": config.get("publication_date") or "",
                    "version": "published article",
                    "source_commit": "",
                    "sections": ["Formalization overview", "Verification model"],
                    "equations": [],
                    "theorem_names": [target["name"] for target in theorem_targets],
                    "definitions": ["EXTERNAL_AI_FORMALIZATION"],
                    "citations": ["anthropic_repo"],
                    "relationships": [{"type": "announces", "target": config["primary_claim_id"]}],
                },
                {
                    "source_id": "anthropic_repo",
                    "title": config.get("repository_title") or config.get("title"),
                    "author_or_organization": config.get("origin_organization") or "Anthropic",
                    "source_type": "lean_formalization_repository",
                    "url": config.get("source_repository") or "",
                    "publication_date": config.get("publication_date") or "",
                    "version": toolchain,
                    "source_commit": config.get("source_commit") or "",
                    "sections": [
                        config.get("root_theorem_file") or "",
                        config.get("proof_path_file") or "",
                        config.get("final_check_file") or "",
                    ],
                    "equations": [target["statement"] for target in theorem_targets if target.get("statement")],
                    "theorem_names": [target["name"] for target in theorem_targets],
                    "definitions": ["FinalCheck", "proof DAG", "axiom audit"],
                    "citations": ["anthropic_article", "anthropic_proof_path", "anthropic_comparator", "anthropic_nanoda"],
                    "relationships": [{"type": "formalizes", "target": config["primary_claim_id"]}],
                },
                {
                    "source_id": "anthropic_proof_path",
                    "title": "Anthropic FLT proof path",
                    "author_or_organization": config.get("origin_organization") or "Anthropic",
                    "source_type": "proof_path",
                    "url": self._repo_url(config, config.get("proof_path_file") or ""),
                    "publication_date": config.get("publication_date") or "",
                    "version": config.get("source_commit") or "",
                    "source_commit": config.get("source_commit") or "",
                    "sections": [item["title"] for item in proof_path],
                    "equations": [],
                    "theorem_names": [ref for item in proof_path for ref in item.get("theorem_references", [])],
                    "definitions": [],
                    "citations": ["anthropic_repo"],
                    "relationships": [{"type": "supports", "target": config["primary_claim_id"]}],
                },
                {
                    "source_id": "anthropic_comparator",
                    "title": "Comparator configuration",
                    "author_or_organization": "leanprover/comparator via Anthropic benchmark",
                    "source_type": "external_checker_configuration",
                    "url": self._repo_url(config, config["comparator"]["config_path"]),
                    "publication_date": config.get("publication_date") or "",
                    "version": config.get("comparator", {}).get("version") or "",
                    "source_commit": config.get("source_commit") or "",
                    "sections": [config["comparator"]["config_path"]],
                    "equations": [],
                    "theorem_names": list(comparator.get("theorem_names", [])),
                    "definitions": ["permitted axioms comparator"],
                    "citations": ["anthropic_repo"],
                    "relationships": [{"type": "checks", "target": config["primary_claim_id"]}],
                },
                {
                    "source_id": "anthropic_nanoda",
                    "title": "Nanoda checker configuration",
                    "author_or_organization": "nanoda via Anthropic benchmark",
                    "source_type": "independent_checker_configuration",
                    "url": self._repo_url(config, config["independent_checker"]["config_path"]),
                    "publication_date": config.get("publication_date") or "",
                    "version": config.get("independent_checker", {}).get("version") or "",
                    "source_commit": config.get("source_commit") or "",
                    "sections": [config["independent_checker"]["config_path"]],
                    "equations": [],
                    "theorem_names": list(nanoda.get("pp_declars", [])),
                    "definitions": ["independent kernel replay"],
                    "citations": ["anthropic_repo"],
                    "relationships": [{"type": "independently_checks", "target": config["primary_claim_id"]}],
                },
            ],
            "claims": proof_nodes,
            "evidence": [
                {
                    "evidence_id": "anthropic-import-metadata",
                    "claim_id": config["primary_claim_id"],
                    "kind": "formalization",
                    "summary": "Imported external Lean metadata, theorem declaration, toolchain pin, and dependency manifest.",
                    "source_id": "anthropic_repo",
                    "source_location": config.get("root_theorem_file") or "",
                    "status": "FORMALIZED",
                    "independence": "formally_verified_by_source_team",
                    "provenance": [FORMAL_PROVENANCE_EXTERNAL_AI, f"origin:{config.get('origin_label') or 'Anthropic/Prove2Me'}"],
                    "details": {
                        "source_commit": config.get("source_commit") or "",
                        "toolchain": toolchain,
                        "mathlib_version": mathlib_package.get("rev") or "",
                        "formalization_manifest_present": bool(formalization),
                    },
                },
                {
                    "evidence_id": "anthropic-proof-path",
                    "claim_id": config["primary_claim_id"],
                    "kind": "theorem",
                    "summary": "Imported the published proof-path structure and mapped it into Barrot's dependency graph.",
                    "source_id": "anthropic_proof_path",
                    "source_location": config.get("proof_path_file") or "",
                    "status": "SUPPORTED",
                    "independence": "same_source_confirmation",
                    "provenance": ["anthropic_proof_path"],
                    "details": {"step_count": len(proof_path)},
                },
            ],
            "tracks": [
                {
                    "track_id": "formal_import",
                    "role": "formalization_ingestion",
                    "strategy": "import published external Lean theorem metadata, proof path, and checker configuration",
                    "hypothesis": "The imported benchmark can be represented without treating it as Barrot-generated mathematics.",
                    "assumptions": [],
                    "dependencies": [],
                    "focus_claims": [config["primary_claim_id"]],
                    "intermediate_results": [
                        {
                            "claim_id": config["primary_claim_id"],
                            "summary": "External FLT formalization imported with provenance preserved.",
                            "status": "FORMALIZED",
                        }
                    ],
                    "evidence": ["anthropic-import-metadata", "anthropic-proof-path"],
                    "failed_approaches": [],
                    "unresolved_objections": [],
                    "confidence": 0.8,
                    "provenance": ["anthropic_repo"],
                },
                {
                    "track_id": "formal_verification",
                    "role": "independent_checker_reproduction",
                    "strategy": "re-run the Lean build, axiom audit, comparator, and independent checker when resources permit",
                    "hypothesis": "Barrot can reproduce the published verification evidence rather than trusting repository claims.",
                    "assumptions": [],
                    "dependencies": [config["primary_claim_id"]],
                    "focus_claims": [config["primary_claim_id"]],
                    "intermediate_results": [
                        {
                            "claim_id": config["primary_claim_id"],
                            "summary": "Verification remains pending until Barrot executes the primary and independent checks.",
                            "status": "UNRESOLVED",
                        }
                    ],
                    "evidence": [],
                    "failed_approaches": [],
                    "unresolved_objections": ["Barrot has not yet reproduced the external verification evidence."],
                    "confidence": 0.4,
                    "provenance": ["anthropic_nanoda", "anthropic_comparator"],
                },
            ],
            "adversarial_reviews": [
                {
                    "review_id": "anthropic-flt-provenance-review",
                    "claim_id": config["primary_claim_id"],
                    "objections": [
                        "Imported external proof must not be treated as BARROT_DISCOVERED_RESULT.",
                        "Verification status must stay below independently checked until Barrot executes its own build and checker runs.",
                    ],
                    "responses": [
                        "Bundle provenance is EXTERNAL_AI_FORMALIZATION and the formal verification record uses staged status values.",
                        "Independent checker fields are recorded separately from import metadata and remain execution-gated.",
                    ],
                    "status": "SUPPORTED",
                    "provenance": ["barrot_policy"],
                }
            ],
            "formal_verification": [
                {
                    "verification_id": str(config["verification_id"]),
                    "system": "lean",
                    "claim_ids": [str(config["primary_claim_id"])],
                    "theorem_names": [target["name"] for target in theorem_targets],
                    "source_files": [target["relative_path"] for target in theorem_targets],
                    "repository": config.get("source_repository") or "",
                    "source_repository": config.get("source_repository") or "",
                    "repository_path": None,
                    "source_commit": config.get("source_commit") or "",
                    "toolchain_version": toolchain,
                    "lean_version": self._parse_lean_version(toolchain),
                    "mathlib_version": mathlib_package.get("rev") or "",
                    "formal_statement": theorem_targets[0]["statement"] if theorem_targets else "",
                    "theorem_statement": theorem_targets[0]["statement"] if theorem_targets else "",
                    "source_location": theorem_targets[0]["source_location"] if theorem_targets else "",
                    "root_theorem": config.get("root_theorem") or (theorem_targets[0]["name"] if theorem_targets else ""),
                    "command": build_command,
                    "build_command": build_command,
                    "axiom_command": axiom_command,
                    "dependencies": sorted({*self._package_dependency_names(manifest), *self._import_dependencies(theorem_targets)}),
                    "dependency_manifest": dependency_manifest,
                    "dependency_graph": self._dependency_graph(config, theorem_targets, proof_path),
                    "proof_path": proof_path,
                    "verification_scripts": {
                        "build": {"command": build_command, "source": "README.md"},
                        "axiom_audit": {"command": axiom_command, "source": config.get("final_check_file")},
                        "comparator": {
                            "command": comparator_command,
                            "config": comparator,
                            "script_path": config["comparator"]["script_path"],
                        },
                        "independent_checker": {
                            "command": checker_command,
                            "config": nanoda,
                            "script_path": config["independent_checker"]["script_path"],
                        },
                    },
                    "compiler_configuration": {
                        "toolchain": toolchain,
                        "lean_options": self._parse_lean_options(self._load_required_text(root, config["lakefile"])) if config.get("lakefile") else {},
                    },
                    "external_checker_configuration": {
                        "comparator": comparator,
                        "independent_checker": nanoda,
                    },
                    "theorem_metadata": theorem_targets,
                    "axiom_result": audit,
                    "independent_checker": dict(config.get("independent_checker") or {}),
                    "independent_checker_result": {
                        "status": "pending",
                        "checker": config.get("independent_checker", {}).get("name") or "nanoda",
                        "command": checker_command,
                    },
                    "comparator_result": {
                        "status": "pending",
                        "statement_alignment": self._statement_alignment(config, theorem_targets),
                        "command": comparator_command,
                    },
                    "resource_requirements": dict(config.get("resource_requirements") or {}),
                    "license": config.get("license") or "",
                    "attribution": config.get("attribution") or "",
                    "provenance": [
                        FORMAL_PROVENANCE_EXTERNAL_AI,
                        f"origin:{config.get('origin_label') or 'Anthropic/Prove2Me'}",
                        f"lineage:{config.get('mathematical_lineage') or 'Frey/Serre/Ribet/Wiles/Taylor-Wiles'}",
                    ],
                    "status": "IMPORTED",
                    "failed_attempts": [],
                }
            ],
            "question_map": [
                {
                    "question_id": "flt_root_theorem",
                    "prompt": "What root theorem does the imported FLT benchmark target?",
                    "claim_ids": [config["primary_claim_id"]],
                    "source_ids": ["anthropic_repo", "anthropic_proof_path"],
                    "answer": {
                        "root_theorem": config.get("root_theorem") or "",
                        "statement": theorem_targets[0]["statement"] if theorem_targets else "",
                        "verification_status": "IMPORTED",
                    },
                }
            ],
        }
        return bundle

    def parse_theorem_target(self, root: Path, target: dict[str, Any]) -> dict[str, Any]:
        relative_path = str(target["path"])
        text = self._load_required_text(root, relative_path)
        declaration = self._parse_declaration(text, str(target["name"]))
        declaration["relative_path"] = relative_path
        declaration["source_location"] = f"{relative_path}:{declaration['line']}"
        declaration["proof_path"] = list(target.get("proof_path", []))
        declaration["comparison_target"] = dict(target.get("comparison_target") or {})
        declaration["imports"] = self._extract_imports(text)
        return declaration

    def parse_proof_path(self, text: str) -> list[dict[str, Any]]:
        matches = list(re.finditer(r"^\*\*(\d+)\.\s+(.+?)\*\*", text, flags=re.MULTILINE))
        steps: list[dict[str, Any]] = []
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            theorem_refs = re.findall(r"`([^`]+)`", body)
            steps.append(
                {
                    "node_id": f"proof-step-{match.group(1)}",
                    "title": match.group(2).strip(),
                    "statement": body.splitlines()[0].strip() if body else match.group(2).strip(),
                    "theorem_references": theorem_refs,
                    "dependencies": [f"proof-step-{int(match.group(1)) + 1}"] if match.group(1) == "2" else [],
                    "source": "PROOF-PATH.md",
                    "status": "IMPORTED",
                    "provenance": [FORMAL_PROVENANCE_EXTERNAL_AI],
                }
            )
        return steps

    def audit_project(
        self,
        root: Path,
        *,
        included_paths: list[str],
        excluded_paths: list[str],
        final_check_text: str,
        permitted_axioms: list[str],
    ) -> dict[str, Any]:
        excluded = {str(Path(item)) for item in excluded_paths}
        hits: dict[str, list[dict[str, Any]]] = {token: [] for token in self.PROHIBITED_ESCAPES}
        scanned_files: list[str] = []
        for relative in included_paths:
            path = root / relative
            if not path.exists():
                continue
            candidates = [path] if path.is_file() else sorted(path.rglob("*.lean"))
            for file_path in candidates:
                rel = str(file_path.relative_to(root))
                if any(rel == item or rel.startswith(f"{item}/") for item in excluded):
                    continue
                scanned_files.append(rel)
                text = file_path.read_text(encoding="utf-8")
                stripped = self._strip_lean_comments_and_strings(text)
                for token in self.PROHIBITED_ESCAPES:
                    if token == "partial def":
                        pattern = r"\bpartial\s+def\b"
                    elif token == "axiom":
                        pattern = r"\baxiom\b"
                    else:
                        pattern = re.escape(token)
                    for number, line in enumerate(stripped.splitlines(), start=1):
                        if re.search(pattern, line):
                            hits[token].append({"file": rel, "line": number, "match": line.strip()[:200]})
        declared_axioms = self._extract_axioms_from_final_check(final_check_text)
        return {
            "status": "clean" if not any(hits.values()) else "review_required",
            "permitted_axioms": permitted_axioms,
            "declared_axioms": declared_axioms,
            "prohibited_escape_hits": {token: values for token, values in hits.items() if values},
            "scanned_file_count": len(scanned_files),
            "scanned_paths": scanned_files[:200],
            "final_check_guard_present": "#guard_msgs in" in final_check_text,
            "used_environment_data": bool(declared_axioms),
        }

    def materialize_bundle(self, project_root: str | Path, config: dict[str, Any], output_path: str | Path) -> Path:
        bundle = self.build_bundle(project_root, config)
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
        return path

    @staticmethod
    def download_archive(archive_url: str, destination_dir: str | Path) -> Path:
        destination = Path(destination_dir).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        archive_path = destination / "external-project.zip"
        with urllib.request.urlopen(archive_url) as response, archive_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        extract_dir = destination / "project"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
        children = [item for item in extract_dir.iterdir() if item.is_dir()]
        return children[0] if len(children) == 1 else extract_dir

    def _parse_declaration(self, text: str, theorem_name: str) -> dict[str, Any]:
        pattern = re.compile(rf"^\s*(theorem|lemma|def)\s+{re.escape(theorem_name)}\b", flags=re.MULTILINE)
        match = pattern.search(text)
        if not match:
            raise ValueError(f"Unable to find declaration for {theorem_name}")
        start = match.start()
        line = text[:start].count("\n") + 1
        chunk = text[start:]
        declaration_lines: list[str] = []
        for raw_line in chunk.splitlines():
            declaration_lines.append(raw_line.rstrip())
            if ":=" in raw_line or raw_line.strip().endswith(":"):
                break
        declaration = " ".join(part.strip() for part in declaration_lines if part.strip())
        statement = declaration.split(":=", 1)[0].strip()
        return {
            "name": theorem_name,
            "kind": match.group(1),
            "line": line,
            "declaration": declaration,
            "statement": statement,
        }

    @staticmethod
    def _strip_lean_comments_and_strings(text: str) -> str:
        result: list[str] = []
        block_depth = 0
        in_string = False
        i = 0
        while i < len(text):
            ch = text[i]
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if block_depth:
                if ch == "-" and nxt == "/":
                    block_depth -= 1
                    result.extend("  ")
                    i += 2
                    continue
                if ch == "/" and nxt == "-":
                    block_depth += 1
                    result.extend("  ")
                    i += 2
                    continue
                result.append("\n" if ch == "\n" else " ")
                i += 1
                continue
            if in_string:
                if ch == '"' and text[i - 1] != "\\":
                    in_string = False
                result.append("\n" if ch == "\n" else " ")
                i += 1
                continue
            if ch == "/" and nxt == "-":
                block_depth += 1
                result.extend("  ")
                i += 2
                continue
            if ch == "-" and nxt == "-":
                while i < len(text) and text[i] != "\n":
                    result.append(" ")
                    i += 1
                continue
            if ch == '"':
                in_string = True
                result.append(" ")
                i += 1
                continue
            result.append(ch)
            i += 1
        return "".join(result)

    @staticmethod
    def _extract_axioms_from_final_check(text: str) -> list[str]:
        match = re.search(r"depends on axioms:\s*\[([^\]]*)\]", text)
        if not match:
            return []
        return [item.strip() for item in match.group(1).split(",") if item.strip()]

    @staticmethod
    def _package_dependency_names(manifest: dict[str, Any]) -> list[str]:
        return [str(pkg.get("name")) for pkg in manifest.get("packages", []) if pkg.get("name")]

    @staticmethod
    def _import_dependencies(theorem_targets: list[dict[str, Any]]) -> list[str]:
        imports: set[str] = set()
        for target in theorem_targets:
            imports.update(str(item) for item in target.get("imports", []) if str(item).strip())
        return sorted(imports)

    @staticmethod
    def _extract_imports(text: str) -> list[str]:
        return [match.group(1).strip() for match in re.finditer(r"^\s*import\s+([^\n]+)$", text, flags=re.MULTILINE)]

    def _statement_alignment(self, config: dict[str, Any], theorem_targets: list[dict[str, Any]]) -> dict[str, Any]:
        root = theorem_targets[0] if theorem_targets else {}
        comparator_target = root.get("comparison_target") or {}
        comparator_statement = str(comparator_target.get("statement") or "")
        local_statement = str(root.get("statement") or "")
        return {
            "target": comparator_target.get("name") or "",
            "local_statement": local_statement,
            "target_statement": comparator_statement,
            "equivalent": self._normalize_lean_statement(local_statement) == self._normalize_lean_statement(comparator_statement),
            "basis": comparator_target.get("basis") or "parsed_declaration",
            "mathlib_bridge": config.get("mathlib_bridge") or "",
        }

    @staticmethod
    def _normalize_lean_statement(statement: str) -> str:
        normalized = re.sub(r"\s+", " ", statement.replace(" :", ":").replace("( ", "(").replace(" )", ")")).strip()
        normalized = re.sub(r"^(theorem|lemma|def)\s+\S+\s+", "", normalized)
        return normalized.strip()

    @staticmethod
    def _build_claim_nodes(
        theorem_targets: list[dict[str, Any]],
        proof_path: list[dict[str, Any]],
        *,
        primary_claim_id: str,
        source_commit: str,
    ) -> list[dict[str, Any]]:
        if not theorem_targets:
            return []
        root = theorem_targets[0]
        claims = [
            {
                "claim_id": primary_claim_id,
                "statement": root.get("statement") or "",
                "domain": "mathematics.number_theory",
                "claim_type": "theorem",
                "source": "anthropic_repo",
                "source_location": root.get("source_location") or "",
                "source_commit": source_commit,
                "assumptions": ["propext", "Classical.choice", "Quot.sound"],
                "dependencies": [item["node_id"] for item in proof_path],
                "provenance": [FORMAL_PROVENANCE_EXTERNAL_AI],
            }
        ]
        for step in proof_path:
            claims.append(
                {
                    "claim_id": step["node_id"],
                    "statement": step["statement"],
                    "domain": "mathematics.number_theory",
                    "claim_type": "lemma",
                    "source": "anthropic_proof_path",
                    "source_location": step["source"],
                    "source_commit": source_commit,
                    "assumptions": [],
                    "dependencies": list(step.get("dependencies", [])),
                    "provenance": [FORMAL_PROVENANCE_EXTERNAL_AI],
                }
            )
        return claims

    @staticmethod
    def _dependency_graph(config: dict[str, Any], theorem_targets: list[dict[str, Any]], proof_path: list[dict[str, Any]]) -> dict[str, Any]:
        root_name = str(config.get("root_theorem") or theorem_targets[0]["name"])
        nodes = [
            {
                "node_id": root_name,
                "kind": "theorem",
                "statement": theorem_targets[0].get("statement") if theorem_targets else "",
                "dependencies": [item["node_id"] for item in proof_path],
                "source": theorem_targets[0].get("relative_path") if theorem_targets else "",
                "proof_artifact": theorem_targets[0].get("relative_path") if theorem_targets else "",
                "status": "IMPORTED",
                "provenance": FORMAL_PROVENANCE_EXTERNAL_AI,
                "verification_result": "pending",
            }
        ]
        for step in proof_path:
            nodes.append(
                {
                    "node_id": step["node_id"],
                    "kind": "theorem_step",
                    "statement": step["statement"],
                    "dependencies": list(step.get("dependencies", [])),
                    "source": step["source"],
                    "proof_artifact": step["source"],
                    "status": step["status"],
                    "provenance": FORMAL_PROVENANCE_EXTERNAL_AI,
                    "verification_result": "pending",
                }
            )
        edges = [
            {"from": root_name, "to": step["node_id"], "relationship": "DEPENDS_ON"}
            for step in proof_path
        ]
        for step in proof_path:
            for dependency in step.get("dependencies", []):
                edges.append({"from": step["node_id"], "to": dependency, "relationship": "DEPENDS_ON"})
        return {"root": root_name, "nodes": nodes, "edges": edges}

    @staticmethod
    def _parse_lean_version(toolchain: str) -> str:
        return toolchain.rsplit(":", 1)[-1] if ":" in toolchain else toolchain

    @staticmethod
    def _parse_lean_options(text: str) -> dict[str, Any]:
        matches = re.findall(r"⟨`([^,]+),\s*([^⟩]+)⟩", text)
        return {name: value.strip() for name, value in matches}

    @staticmethod
    def _load_required_text(root: Path, relative_path: str) -> str:
        path = root / relative_path
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _load_optional_text(root: Path, relative_path: str | None) -> str:
        if not relative_path:
            return ""
        path = root / relative_path
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @staticmethod
    def _load_json(root: Path, relative_path: str) -> dict[str, Any]:
        path = root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _repo_url(config: dict[str, Any], relative_path: str) -> str:
        repository = str(config.get("source_repository") or "").rstrip("/")
        commit = str(config.get("source_commit") or "").strip()
        if repository.startswith("https://github.com/") and commit and relative_path:
            return f"{repository}/blob/{commit}/{relative_path}"
        return repository


ANTHROPIC_FLT_IMPORT_CONFIG: dict[str, Any] = {
    "problem_id": "anthropic_fermats_last_theorem_benchmark",
    "title": "Anthropic Fermat's Last Theorem benchmark",
    "domain": "mathematics.number_theory.formal_verification",
    "primary_question": "Can Barrot ingest and independently reproduce the published Fermat's Last Theorem Lean benchmark?",
    "primary_claim_id": "claim.fermat_last_theorem",
    "verification_id": "formal.anthropic_fermat_last_theorem",
    "article_title": "Formalizing Fermat's Last Theorem",
    "article_url": "https://www.anthropic.com/research/formalizing-fermats-last-theorem",
    "repository_title": "Fermat's Last Theorem in Lean 4",
    "source_repository": "https://github.com/anthropics/fermats-last-theorem",
    "source_commit": "aa2d8b34692b16c70f699536de0d8e75b9a3e9ef",
    "publication_date": "2026-08-27",
    "origin_organization": "Anthropic",
    "origin_label": "Anthropic/Claude formalization",
    "mathematical_lineage": "Frey/Serre/Ribet/Wiles/Taylor-Wiles",
    "license": "Apache-2.0",
    "attribution": "Origin = Anthropic/Claude formalization; formalization provenance = Anthropic/Prove2Me project; mathematical lineage = Frey/Serre/Ribet/Wiles/Taylor-Wiles.",
    "toolchain_file": "lean-toolchain",
    "dependency_manifest_file": "lake-manifest.json",
    "formalization_manifest": "formalization.yaml",
    "proof_path_file": "PROOF-PATH.md",
    "final_check_file": "FinalCheck.lean",
    "lakefile": "lakefile.lean",
    "root_theorem": "fermat_last_theorem",
    "root_theorem_file": "Theorems/Thm_fermat_last_theorem.lean",
    "theorem_targets": [
        {
            "name": "fermat_last_theorem",
            "path": "Theorems/Thm_fermat_last_theorem.lean",
            "comparison_target": {
                "name": "FLT_for_comparator",
                "basis": "published comparator theorem",
                "statement": "theorem FLT_for_comparator (n : ℕ) (hn : 3 ≤ n) (a b c : ℕ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) : a ^ n + b ^ n ≠ c ^ n",
            },
        },
        {
            "name": "flt_mathlib",
            "path": "FinalCheck.lean",
            "comparison_target": {
                "name": "FermatLastTheorem",
                "basis": "published FinalCheck bridge theorem",
                "statement": "theorem flt_mathlib : FermatLastTheorem",
            },
        },
    ],
    "mathlib_bridge": "FinalCheck.lean declares theorem flt_mathlib : FermatLastTheorem.",
    "build_command": ["lake", "build"],
    "axiom_command": ["lake", "env", "lean", "FinalCheck.lean"],
    "comparator": {
        "name": "leanprover/comparator",
        "version": "v4.33.0",
        "config_path": "verification/comparator/config.json",
        "script_path": "verification/comparator/run.sh",
        "command": ["bash", "verification/comparator/run.sh"],
    },
    "independent_checker": {
        "name": "nanoda",
        "version": "0.4.13",
        "config_path": "verification/nanoda/nanoda-config.json",
        "script_path": "verification/nanoda/run.sh",
        "command": ["bash", "verification/nanoda/run.sh"],
    },
    "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "audit_paths": ["Theorems", "Definitions", "P2M", "FinalCheck.lean"],
    "audit_excluded_paths": ["verification/comparator/Challenge.lean"],
    "resource_requirements": {
        "build": {"memory_per_parallel_job_gb": 5, "peak_memory_gb": 153, "disk_gb": 287, "notes": "Published README values; actual Barrot runs must record observed resources separately."},
        "comparator": {"peak_memory_gb": 230, "recommended_memory_gb": 300, "elapsed_hours": 15},
        "independent_checker": {"export_memory_gb": 90, "check_memory_gb": 40, "threads": 16},
    },
}


class AnthropicFermatBenchmarkAdapter(StaticResearchProblemAdapter):
    def __init__(self, bundle_path: str | Path | None = None):
        base = (
            Path(bundle_path).resolve()
            if bundle_path is not None
            else Path(__file__).resolve().parents[2] / "data" / "research" / "anthropic_fermats_last_theorem_bundle.json"
        )
        super().__init__(base)


def select_scientific_problem_adapter(title: str, body: str) -> StaticResearchProblemAdapter:
    text = f"{title}\n{body}".lower()
    if "fermat" in text and "theorem" in text:
        return AnthropicFermatBenchmarkAdapter()
    return NavierStokesProblemAdapter()


def materialize_anthropic_flt_bundle(output_path: str | Path, project_root: str | Path) -> Path:
    return ExternalLeanProjectImporter().materialize_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG, output_path)


def prepare_anthropic_flt_bundle_from_archive(output_path: str | Path, archive_url: str = DEFAULT_ANTHROPIC_FLT_ARCHIVE) -> Path:
    importer = ExternalLeanProjectImporter()
    with tempfile.TemporaryDirectory(prefix="anthropic-flt-") as tmp_dir:
        extracted = importer.download_archive(archive_url, tmp_dir)
        return importer.materialize_bundle(extracted, ANTHROPIC_FLT_IMPORT_CONFIG, output_path)
