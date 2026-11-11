"""Contract test for scripts/mmi_compiler.parse_liquidity.

Written before transmuting the module (transmute rule 6). Scoped-runnable:
imports via scripts/ path shim so it works standalone and under transmute.py.
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import mmi_compiler  # noqa: E402


def run_on(content: str):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    buf = io.StringIO()
    with redirect_stdout(buf):
        mmi_compiler.parse_liquidity(path)
    return buf.getvalue().strip()


class TestParseLiquidity(unittest.TestCase):
    def test_normal_bids(self):
        out = run_on('x "bid" y "10.5"\nx "bid" y "20.5"\n')
        self.assertIn("STRIKE_READY", out)
        self.assertIn("15.5000", out)

    def test_empty_file_is_null_liquidity(self):
        out = run_on("")
        self.assertIn("NULL_LIQUIDITY", out)

    def test_missing_file_is_error_signal(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            mmi_compiler.parse_liquidity("/nonexistent/path/xyz.txt")
        self.assertIn("SIGNAL: ERROR", buf.getvalue().strip())

    def test_malformed_float_discards_run(self):
        # Baseline contract: any malformed bid aborts the whole signal.
        out = run_on('x "bid" y "10.5"\nx "bid" y "not_a_number"\n')
        self.assertIn("SIGNAL: ERROR", out)

    def test_short_bid_line_is_error(self):
        # "bid" line with fewer than 4 quoted fields aborts the whole run.
        out = run_on('x "bid" y\n')
        self.assertIn("SIGNAL: ERROR", out)

    def test_no_bid_lines_is_null_liquidity(self):
        out = run_on('x "ask" y "10.5"\n')
        self.assertIn("NULL_LIQUIDITY", out)


if __name__ == "__main__":
    unittest.main()
