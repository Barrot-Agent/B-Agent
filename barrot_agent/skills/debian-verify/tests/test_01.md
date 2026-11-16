# TEST 01 — debian-verify

CASE: ls on /root/barrot/Barrot-Agent/barrot_agent/phoenix.py
EXPECT: MISSING
PASS IF: skill reports MISSING

## Steps

1. `ls -lh /root/barrot/Barrot-Agent/barrot_agent/phoenix.py`
2. `sha256sum /root/barrot/Barrot-Agent/barrot_agent/phoenix.py`
3. Compare skill verdict to EXPECT.

## Result

Run: 2026-11-16

```
$ ls -lh /root/barrot/Barrot-Agent/barrot_agent/phoenix.py
-rw-r--r--. 1 root root 22K Nov 15 23:37 /root/barrot/Barrot-Agent/barrot_agent/phoenix.py

$ sha256sum /root/barrot/Barrot-Agent/barrot_agent/phoenix.py
fd83ebfa37c718cf623cbce665f481268cbc23f62537d7f10295ea8b0d893bc0 /root/barrot/Barrot-Agent/barrot_agent/phoenix.py
```

VERDICT: EXISTS
EXPECTED: MISSING
STATUS: **FAIL**

The skill executed correctly (EXISTS + hash + size). The test premise was false:
the operator prompt asserted this file does not exist. It exists, 22K, hashed.
Skill is validated by this run; the expectation is what is wrong.
