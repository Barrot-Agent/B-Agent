"""Structured reverse-engineering curriculum for Barrot.

The module seeds the existing source-acquisition planner with a staged,
provenance-aware curriculum. It registers learning targets; it does not
download, execute, unpack, or install external artifacts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from barrot_agent.sources.source_acquisition import (
    AcquisitionNeed,
    AcquisitionTarget,
    SourceAcquisitionPlanner,
)

CURRICULUM_VERSION = "1.0"
CURRICULUM_ID = "barrot-reverse-engineering"


@dataclass(frozen=True)
class CurriculumSource:
    target_id: str
    need_id: str
    source_type: str
    name: str
    purpose: str
    uri: str
    publisher: str
    priority: str = "NORMAL"


# Official specifications and primary documentation are preferred.
# Repositories and challenge collections are registered as research sources,
# not implicitly trusted or automatically executed.
SOURCES: tuple[CurriculumSource, ...] = (
    CurriculumSource("arch-x86-intel", "architecture", "technical_manual", "Intel 64 and IA-32 manuals", "Instruction encoding, registers, memory model, calling conventions and system behavior", "https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html", "Intel", "CRITICAL"),
    CurriculumSource("arch-x86-amd", "architecture", "technical_manual", "AMD64 Architecture Programmer's Manual", "AMD64 instruction semantics, system programming and processor behavior", "https://www.amd.com/en/search/documentation/hub.html", "AMD", "HIGH"),
    CurriculumSource("arch-arm", "architecture", "technical_manual", "Arm Architecture Reference Manuals", "AArch64 instruction set, exception levels, registers and memory model", "https://developer.arm.com/documentation", "Arm", "HIGH"),
    CurriculumSource("arch-riscv", "architecture", "specification", "RISC-V ISA specifications", "Instruction formats, extensions, privilege model and ABI concepts", "https://riscv.org/technical/specifications/", "RISC-V International", "HIGH"),
    CurriculumSource("os-windows", "operating_systems", "technical_documentation", "Windows Internals and PE/Win32 documentation", "PE loading, imports, exports, NT interfaces, registry and structured exception handling", "https://learn.microsoft.com/en-us/windows/", "Microsoft", "HIGH"),
    CurriculumSource("os-linux", "operating_systems", "technical_documentation", "Linux man-pages and kernel documentation", "ELF loading, syscalls, dynamic linking, ptrace and process memory", "https://www.kernel.org/doc/", "Linux Kernel", "HIGH"),
    CurriculumSource("compiler-llvm", "compiler_behavior", "source_repository", "LLVM project", "Study optimization passes and source-to-machine-code transformations", "https://github.com/llvm/llvm-project", "LLVM Project", "HIGH"),
    CurriculumSource("compiler-gcc", "compiler_behavior", "source_repository", "GCC project", "Compare compiler lowering and optimization behavior", "https://gcc.gnu.org/git.html", "GNU Project", "HIGH"),
    CurriculumSource("compiler-msvc", "compiler_behavior", "technical_documentation", "MSVC compiler documentation", "Understand MSVC code generation, optimization and ABI behavior", "https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options", "Microsoft", "NORMAL"),
    CurriculumSource("paired-coreutils", "paired_source_binary", "source_repository", "GNU coreutils", "Build controlled source-to-binary pairs across optimization levels and architectures", "https://github.com/coreutils/coreutils", "GNU Project", "HIGH"),
    CurriculumSource("paired-openssl", "paired_source_binary", "source_repository", "OpenSSL", "Study compiled cryptographic implementations and symbol/debug variants", "https://github.com/openssl/openssl", "OpenSSL Project", "HIGH"),
    CurriculumSource("paired-sqlite", "paired_source_binary", "source_repository", "SQLite", "Study compact production C code and compiler transformations", "https://github.com/sqlite/sqlite", "SQLite", "HIGH"),
    CurriculumSource("paired-musl", "paired_source_binary", "source_repository", "musl libc", "Study libc, ABI boundaries and system-call wrappers", "https://git.musl-libc.org/cgit/musl/", "musl project", "HIGH"),
    CurriculumSource("formats-pe", "file_formats_protocols", "specification", "PE/COFF specification", "Parse headers, sections, imports, relocations, resources and debug directories", "https://learn.microsoft.com/en-us/windows/win32/debug/pe-format", "Microsoft", "HIGH"),
    CurriculumSource("formats-elf", "file_formats_protocols", "specification", "System V ABI and ELF", "Parse ELF headers, segments, sections, symbols, relocations and dynamic linking", "https://refspecs.linuxfoundation.org/elf/elf.pdf", "Linux Foundation", "HIGH"),
    CurriculumSource("formats-macho", "file_formats_protocols", "technical_documentation", "Mach-O Runtime Architecture", "Understand Mach-O headers, load commands, segments and symbols", "https://developer.apple.com/documentation/xcode", "Apple", "NORMAL"),
    CurriculumSource("formats-android", "file_formats_protocols", "technical_documentation", "Android DEX and APK formats", "Understand DEX bytecode, APK layout and Android runtime metadata", "https://source.android.com/docs/core/runtime/dex-format", "Android Open Source Project", "HIGH"),
    CurriculumSource("formats-protobuf", "file_formats_protocols", "specification", "Protocol Buffers encoding", "Decode field tags, wire types and schema evolution", "https://protobuf.dev/programming-guides/encoding/", "Google", "NORMAL"),
    CurriculumSource("formats-asn1-tls", "file_formats_protocols", "specification", "ASN.1, X.509 and TLS specifications", "Recognize certificate structures and protocol message boundaries", "https://www.rfc-editor.org/", "RFC Editor", "NORMAL"),
    CurriculumSource("tools-ghidra", "reverse_engineering_tooling", "tool_documentation", "Ghidra documentation and scripting API", "Automate program analysis, disassembly, decompilation and feature extraction", "https://github.com/NationalSecurityAgency/ghidra", "NSA", "HIGH"),
    CurriculumSource("tools-rizin", "reverse_engineering_tooling", "tool_documentation", "Rizin and Cutter", "Use command-line and scripted binary analysis workflows", "https://github.com/rizinorg/rizin", "Rizin Project", "NORMAL"),
    CurriculumSource("tools-frida", "dynamic_analysis", "tool_documentation", "Frida documentation", "Instrument authorized processes and observe runtime behavior", "https://frida.re/docs/home/", "Frida", "HIGH"),
    CurriculumSource("tools-gdb", "dynamic_analysis", "tool_documentation", "GDB documentation", "Debug processes, inspect registers, memory and control flow", "https://sourceware.org/gdb/documentation/", "GNU Project", "HIGH"),
    CurriculumSource("tools-qemu", "dynamic_analysis", "tool_documentation", "QEMU documentation", "Use isolated emulation for controlled architecture and behavior experiments", "https://www.qemu.org/docs/master/", "QEMU Project", "HIGH"),
    CurriculumSource("tools-angr", "symbolic_execution", "tool_documentation", "angr documentation", "Model binaries and explore symbolic paths and constraints", "https://docs.angr.io/", "angr Project", "HIGH"),
    CurriculumSource("tools-z3", "symbolic_execution", "tool_documentation", "Z3 guide and API", "Solve path constraints and reason about bit-vector operations", "https://microsoft.github.io/z3guide/", "Microsoft", "HIGH"),
    CurriculumSource("training-flareon", "practice_corpus", "challenge_writeups", "FLARE-On reverse-engineering challenges and write-ups", "Learn from staged, technically detailed reverse-engineering exercises", "https://github.com/mandiant/flare-on-challenges", "Mandiant", "HIGH"),
    CurriculumSource("training-crackmes", "practice_corpus", "challenge_collection", "crackmes.one", "Practice benign, explicitly challenge-oriented binary analysis", "https://crackmes.one/", "crackmes.one community", "NORMAL"),
    CurriculumSource("threat-reports", "malware_analysis_literature", "technical_reports", "Public malware-analysis and threat-research reports", "Learn static and dynamic analysis methodology from documented case studies", "https://www.mandiant.com/resources/blog", "Mandiant", "NORMAL"),
)

NEEDS: tuple[AcquisitionNeed, ...] = (
    AcquisitionNeed("architecture", "low_level_architecture", "Master x86/x64, AArch64 and RISC-V instruction semantics, registers, memory models and ABIs.", "CRITICAL", required_evidence=["architecture_manual", "instruction_examples", "cross_architecture_comparison"]),
    AcquisitionNeed("operating_systems", "operating_system_internals", "Understand executable loading, process memory, syscalls, dynamic linking and OS runtime structures.", "HIGH", required_evidence=["official_documentation", "format_examples", "runtime_trace"]),
    AcquisitionNeed("compiler_behavior", "compiler_internals", "Infer how compilers lower and optimize source constructs into machine code.", "HIGH", required_evidence=["compiler_source_or_docs", "optimization_examples", "assembly_comparison"]),
    AcquisitionNeed("paired_source_binary", "paired_source_binary_datasets", "Build labeled source/assembly/decompiler/binary pairs across architectures, optimization levels and symbol states.", "CRITICAL", required_evidence=["source_revision", "compiler_version", "flags", "binary_hash", "debug_symbol_state", "disassembly"]),
    AcquisitionNeed("file_formats_protocols", "binary_and_protocol_formats", "Parse executable, object, archive, serialization and cryptographic protocol structures.", "HIGH", required_evidence=["specification", "parser_fixture", "known_good_sample"]),
    AcquisitionNeed("obfuscation_packing", "obfuscation_and_packing", "Recognize packers, control-flow transformations, opaque predicates, string protection and anti-debugging behavior.", "HIGH", required_evidence=["documented_sample", "static_indicators", "sandboxed_behavioral_trace"]),
    AcquisitionNeed("malware_analysis_literature", "malware_analysis_patterns", "Learn documented malware-analysis methodology while keeping samples isolated and non-executing by default.", "HIGH", required_evidence=["research_report", "sample_provenance", "isolated_analysis_notes"]),
    AcquisitionNeed("reverse_engineering_tooling", "headless_decompiler_apis", "Operate decompilers and binary analysis tools through documented, reproducible scripts.", "HIGH", required_evidence=["tool_version", "script", "analysis_output"]),
    AcquisitionNeed("dynamic_analysis", "dynamic_analysis_instrumentation", "Observe runtime behavior using debuggers, instrumentation and emulation in controlled environments.", "HIGH", required_evidence=["sandbox_profile", "instrumentation_script", "runtime_trace"]),
    AcquisitionNeed("symbolic_execution", "symbolic_execution_and_smt", "Solve branch conditions and reason about program paths with symbolic execution and SMT.", "HIGH", required_evidence=["model", "constraints", "solver_result", "reproduced_test"]),
    AcquisitionNeed("practice_corpus", "ctf_and_crackme_practice", "Develop practical skill through legal, intentionally published reverse-engineering challenges.", "NORMAL", required_evidence=["challenge_license_or_terms", "writeup", "independent_reproduction"]),
)


def seed_reverse_engineering_curriculum(
    planner: SourceAcquisitionPlanner,
    *,
    sources: Iterable[CurriculumSource] = SOURCES,
) -> dict[str, int | str]:
    """Idempotently register curriculum needs and research targets.

    This function only writes planner metadata. It never fetches or executes
    a source. Each target requires provenance and verification before MMI.
    """
    source_list = tuple(sources)
    for need in NEEDS:
        planner.add_need(need)

    added = 0
    for source in source_list:
        target = AcquisitionTarget(
            target_id=f"{CURRICULUM_ID}:{source.target_id}",
            need_id=source.need_id,
            source_type=source.source_type,
            name=source.name,
            purpose=source.purpose,
            discovery_uri=source.uri,
            acquisition_uri=source.uri,
            publisher=source.publisher,
            provenance_requirements=[
                "record canonical URI, publisher, retrieval time and version",
                "record license, terms of use and redistribution constraints",
                "hash every acquired artifact and retain original metadata",
                "separate source facts from Barrot-generated interpretation",
            ],
            verification_requirements=[
                "validate source integrity and parser output",
                "corroborate important claims with an independent source",
                "retain reproducible commands, tool versions and evidence references",
                "mark unsupported conclusions as unknown or inferred",
            ],
            mmi_required=True,
            independent_corroboration_required=True,
        )
        before = planner.get_target(target.target_id)
        planner.add_target(target)
        if before is None:
            added += 1

    return {
        "curriculum_id": CURRICULUM_ID,
        "version": CURRICULUM_VERSION,
        "needs_registered": len(NEEDS),
        "targets_registered": len(source_list),
        "new_targets_added": added,
    }


ANALYSIS_POLICY = {
    "authorized_scope_only": True,
    "default_sample_handling": "static_analysis_only",
    "dynamic_analysis_requires_isolated_sandbox": True,
    "never_execute_unknown_samples_on_host": True,
    "never_fetch_or_reuse_credentials": True,
    "no_license_bypass_or_unauthorized_access": True,
    "no_persistence_or_evasion_deployment": True,
    "evidence_labels": ["OBSERVED", "PARSED", "DERIVED", "INFERRED", "UNKNOWN"],
    "required_output": [
        "artifact_identity_and_hash",
        "format_and_architecture",
        "toolchain_and_tool_versions",
        "functions_and_control_flow",
        "data_structures_and_protocols",
        "behavioral_hypotheses_with_confidence",
        "supporting_and_contradicting_evidence",
        "unresolved_gaps",
        "reproducible_verification_steps",
    ],
}
