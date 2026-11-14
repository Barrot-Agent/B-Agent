from pathlib import Path


def test_global_state_manifest_liquid_tokens_are_guarded_by_raw_blocks():
    manifest = Path(__file__).resolve().parents[1] / "GLOBAL_STATE_MANIFEST.md"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    in_raw = False
    raw_blocks = 0

    for number, line in enumerate(lines, start=1):
        marker = line.strip()
        if marker == "{% raw %}":
            assert not in_raw, f"nested raw block at line {number}"
            in_raw = True
            raw_blocks += 1
            continue
        if marker == "{% endraw %}":
            assert in_raw, f"unmatched endraw at line {number}"
            in_raw = False
            continue
        if any(token in line for token in ("{{", "}}", "{%", "%}")):
            assert in_raw, f"unprotected Liquid token at line {number}"

    assert not in_raw, "unterminated Liquid raw block"
    assert raw_blocks == 2
