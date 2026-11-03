from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dump_brain_corpus_workflow_is_inert_and_has_no_data_credentials():
    workflow = (ROOT / ".github" / "workflows" / "dump-brain-corpus.yml").read_text(encoding="utf-8")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "workflow_dispatch" in workflow
    assert "DATABRICKS_TOKEN" not in workflow
    assert "workspace.barrot.brain" not in workflow
    assert "git push" not in workflow
    assert "scripts/dump_brain_corpus.py" not in workflow


def test_dump_brain_corpus_script_is_inert_without_network_or_file_writes(tmp_path, monkeypatch, capsys):
    path = ROOT / "scripts" / "dump_brain_corpus.py"
    spec = spec_from_file_location("disabled_dump_brain_corpus", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.chdir(tmp_path)

    assert module.main() == 2
    output = capsys.readouterr().out
    assert "DISABLED" in output
    assert "No Databricks credentials were read" in output
    assert list(tmp_path.iterdir()) == []


def test_public_brain_corpus_dumps_are_absent_from_current_tree():
    assert not (ROOT / "brain_corpus" / "dump.json").exists()
    assert not (ROOT / "brain_corpus" / "dump.md").exists()


def test_unclassified_brain_corpus_entries_are_preserved_by_containment():
    expected = {
        "polymath_biology_epigenetics_and_environmental_gene_contr.json",
        "polymath_chemistry_complete_chemistry_and_periodic_table_ma.json",
        "polymath_cinematography_complete_visual_language_mastery.json",
        "polymath_dance_universal_dance_mastery.json",
        "polymath_languages_universal_language_acquisition.json",
        "polymath_martial_arts_complete_combat_system_mastery.json",
        "polymath_mathematics_complete_mathematical_mastery.json",
        "polymath_music_and_audio_production_complete_audio_architecture.json",
        "polymath_philosophy_epistemology_and_philosophy_of_science.json",
        "polymath_physics_complete_physics_mastery.json",
        "polymath_sciences_universal_science_mastery.json",
        "polymath_synthesis_unlimited_cross-domain_synthesis_engine.json",
        "polymath_vocal_science_vocal_cartography_and_extended_technique.json",
        "topics.txt",
    }
    actual = {path.name for path in (ROOT / "brain_corpus").iterdir()}
    assert actual == expected
