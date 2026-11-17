# Track 1 - Cymatics

Date: 2026-11-17
Layer key: [L1] established, measured, citable. [L2] applied engineering practice.
[L3] speculative, carries its own falsifier, supports nothing above it.

## Transmutation

ORIGINAL: "Start Track 1: Cymatics."
GAP: (1) no target output, so "learn" could mean read or produce an artifact;
(2) no test, so nothing would separate knowing from reciting;
(3) no boundary, so the popular version of cymatics would contaminate the physics.
[FILLED GAP] I assumed the deliverable is one tested, layer-tagged page plus a
runnable prediction check, not a reading list.
TRANSMUTED: "Produce a layer-tagged cymatics page with definition, mechanism, real
experiment, production example, what it is not, and falsifier; reverse-engineer
Chladni patterns as frequency-to-mode mapping; predict a case first, then test it
numerically; log to Flight Recorder."

## 1. Definition

[L1] Cymatics is the study of visible standing-wave patterns on a driven surface:
a plate, membrane, or fluid boundary is excited at a frequency, and the resulting
displacement field has regions of zero motion (nodes) and maximum motion
(antinodes). Loose grains on the surface collect where the surface is still.

[L1] The pattern is a mode shape, not an image of the sound. Sound is pressure in
a medium; the pattern is the boundary value problem of the driven object.

## 2. Math and mechanism

[L1] A square membrane with fixed edges obeys

    u_tt = c^2 (u_xx + u_yy),  u = 0 on the boundary

with modes u_mn = sin(m*pi*x) sin(n*pi*y) and frequencies

    f_mn proportional to sqrt(m^2 + n^2).

[L1] A real metal plate is not a membrane. It is a stiff plate governed by the
biharmonic equation, where frequency scales roughly with thickness and with
1/(plate size)^2, and the mode ratios are not sqrt(m^2+n^2). The structure is the
same: discrete modes, nodal lines, and a pattern set by which mode the drive
excites.

[L1] Circular membranes use Bessel functions J_m; modes have nodal circles and
nodal diameters. The number of nodal diameters is 2m for the m-th family.

[L1] A drive at frequency f excites the modes near f. That is Fourier in practice:
the driver's spectrum selects among available modes, it does not invent one.

## 3. Real experiment

[L1] Chladni, 1787: a metal plate, a violin bow or a driven point, and fine sand.
The plate is bowed until a clear tone appears; the sand migrates off the moving
regions and settles on the nodal lines. Repeatable, cheap, and the origin of the
field. Change the bowing point and the plate locks to a different mode at a
different pitch.

[L1] Modern version: replace the bow with a signal generator and a shaker, sweep
frequency, and photograph each pattern. This is the setup in every cymatics demo
that is not selling something.

## 4. Production example

[L2] Modal analysis. The same eigenproblem is solved by finite element software
before a part is built. Designers move modes away from drive frequencies or add
damping, because a resonance at an operating frequency turns vibration into
fatigue and noise. Speaker cones, turbine blades, brackets and violin plates are
all treated this way. The cymatics photograph is a low-cost modal survey.

[L2] Ultrasonic particle levitation holds droplets at the pressure nodes of a
standing wave. Typical drivers in air are in the tens of kHz; the exact value is
vendor and geometry dependent and is not verified here.

[L2] Ultrasonic cleaning is adjacent but not cymatics: it works through cavitation
bubble collapse, not through nodal patterns. Listing it as cymatics is a category
error.

## 5. What it is NOT

[L1] Not a function of frequency alone. The pattern is the eigenfunction of a
specific object: geometry, edge conditions, thickness, material. Same frequency,
different plate, different pattern.

[L1] Not evidence for healing frequencies, water memory, DNA repair, or sacred
geometry. Those claims require a mechanism and a controlled trial; a sand pattern
on a plate supplies neither.

[L1] Not an image of sound in the air. Nothing in the plate photographs the
acoustic field around it.

## 6. Falsifier

[L1] If the pattern were set by frequency alone, two plates of different size and
thickness driven at the same frequency would show the same nodal lines. They do
not. Any claim that cymatics encodes information in frequency independent of the
object is refuted by that comparison.

## 7. Reverse-engineered example: frequency to pattern

Claim under test: the pattern order follows the eigenproblem, so the sequence of
frequencies is predictable before measuring.

Predictions written before the run, in scripts/cymatics_mode_check.py: ratios to
the first mode of 1.5811, 1.5811, 2.0000, 2.2361; and nodal line counts per axis.

Run: 60x60 finite-difference Laplacian, lowest 10 eigenpairs, 2.87 s.

    mode     measured ratio   predicted   error
    (1,1)    1.0000           1.0000       0.00%
    (1,2)    1.5807           1.5811       0.03%
    (2,1)    1.5807           1.5811       0.03%
    (2,2)    1.9993           2.0000       0.04%
    (1,3)    2.2343           2.2361       0.08%
    (3,1)    2.2343           2.2361       0.08%
    (2,3)    2.5477           2.5495       0.07%
    (3,2)    2.5477           2.5495       0.07%
    (1,4)    2.9109           2.9155       0.16%
    (4,1)    2.9109           2.9155       0.16%

Verdict: ratios pass, worst error 0.16 percent. The frequency ordering is the
eigenproblem, not a mystery.

Partial failure, reported rather than buried: I also predicted nodal counts per
axis for every mode. That held only for (2,2), the one non-degenerate mode in the
set. For degenerate pairs like (1,2) and (2,1) the solver returns a mixture of the
pair, so the nodal lines rotate and the per-axis counts stop matching. This is not
a solver artifact to hide: the same thing happens on a real plate, where the
bowing point decides which combination of a degenerate pair appears. Same
frequency, two patterns. That is the mechanism behind section 5's first line.

Tests: tests/test_cymatics_modes.py, 4 passed.

## 8. Layer 3 - speculative, labelled

[L3] Hypothesis: the "node" is a general organising principle, so any system with
a standing wave (a market, an organisation, a schedule) has regions of high
activity and still points where pressure collects.

Why it is L3 and not L2: the wave equation has a measurable field with units. An
organisation does not, and the mapping has no conserved quantity behind it.

Falsifier for this hypothesis: produce one prediction about a non-physical system
from the standing-wave analogy that could not have been made without it, then test
it. If the prediction is indistinguishable from the obvious, the analogy is
decoration, not a model.

## 9. Open, not verified here

- The real plate equation and its mode ratios (biharmonic, clamped vs free edge).
  My test is a membrane, deliberately, because it is analytically checkable.
- Threshold behaviour of fine powder versus coarse sand. Coarse grains migrate to
  nodes; very fine powder can behave differently. Not tested.
- One physical plate experiment with measured frequency and photographed pattern.
  That is the next gate before this becomes a skill.
