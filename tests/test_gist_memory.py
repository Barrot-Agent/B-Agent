"""Tests for the extractive gist-memory compressor.

Runs with the stdlib test runner (``python -m unittest``) and under pytest.
No network, no model, no GPU.
"""

from __future__ import annotations

import json
import unittest

from barrot_agent.gist_memory import (
    GistMemory,
    compress_documents,
)

DOCS = [
    "My sister Priya was born on 12 May 1990. She is a doctor in Cork.",
    "Sean lives in Dublin and has a family history of type 2 diabetes. He avoids sugar.",
    "The Hound of the Baskervilles features Dr. Roylott, the villain from The Speckled Band.",
]


class CompressionTests(unittest.TestCase):
    def test_empty_documents(self):
        result = compress_documents([], "anything")
        self.assertEqual(result.tokens, [])
        self.assertEqual(result.documents, 0)

    def test_blank_documents(self):
        result = compress_documents(["", "   \n "], "anything")
        self.assertEqual(result.tokens, [])

    def test_query_selects_the_relevant_clause(self):
        result = compress_documents(DOCS, "When was my sister born?")
        self.assertTrue(result.tokens)
        self.assertIn("Priya", result.tokens[0].text)
        self.assertIn("1990", result.tokens[0].text)

    def test_extractive_only(self):
        result = compress_documents(DOCS, "Which villain appears?")
        self.assertTrue(result.tokens)
        for token in result.tokens:
            self.assertTrue(
                any(token.text in doc or token.source_sentence in doc for doc in DOCS),
                msg=f"non-extractive token: {token.text!r}",
            )

    def test_word_budget_is_enforced(self):
        result = compress_documents(
            DOCS, "sister born doctor Dublin", num_memories=2, words_per_token=4
        )
        self.assertLessEqual(len(result.tokens), 2)
        self.assertLessEqual(result.words, 8)

    def test_context_clause_keeps_names(self):
        result = compress_documents(DOCS, "Which villain appears?")
        joined = " ".join(token.text for token in result.tokens)
        self.assertIn("Roylott", joined)

    def test_expand_returns_verbatim_source(self):
        result = compress_documents(DOCS, "When was my sister born?")
        source = result.expand(0)
        self.assertTrue(any(source in doc for doc in DOCS))
        self.assertEqual(result.expand(result.tokens[0]), source)

    def test_deterministic(self):
        first = compress_documents(DOCS, "family history of diabetes")
        second = compress_documents(DOCS, "family history of diabetes")
        self.assertEqual(first.as_dict(), second.as_dict())

    def test_duplicate_lines_do_not_fill_the_budget(self):
        docs = ["Priya was born on 12 May 1990."] * 10
        result = compress_documents(docs, "When was Priya born?")
        self.assertEqual(len(result.tokens), 1)

    def test_empty_query_still_produces_facts(self):
        result = compress_documents(DOCS, "")
        self.assertTrue(result.tokens)
        self.assertTrue(result.carries_exact_facts)

    def test_compression_ratio_is_reported(self):
        result = compress_documents(DOCS, "sister born")
        self.assertGreaterEqual(result.compression_ratio, 1.0)

    def test_json_roundtrip(self):
        result = compress_documents(DOCS, "sister born")
        payload = json.dumps(result.as_dict())
        loaded = json.loads(payload)
        self.assertEqual(loaded["query"], "sister born")
        self.assertEqual(len(loaded["tokens"]), len(result.tokens))
        self.assertIn("gist_words", loaded["stats"])

    def test_prompt_has_anti_invention_rule(self):
        result = compress_documents(DOCS, "sister born")
        prompt = result.to_prompt()
        self.assertIn("Use only these phrases", prompt)
        self.assertIn("instead of guessing", prompt)

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            GistMemory(num_memories=0)
        with self.assertRaises(ValueError):
            GistMemory(words_per_token=0)


if __name__ == "__main__":
    unittest.main()
