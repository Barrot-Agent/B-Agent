#!/usr/bin/env python3
"""
Barrot Universal Polymath Ingestion Pipeline.

Ingests structured knowledge bundles across every polymath domain into the
brain_corpus directory and registers each topic in brain_corpus/topics.txt.

Follows the pattern established by longevity_micro_ingestion.py and
millennium_problems_micro_ingestion.py.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

# Resolve paths relative to this file so the module works from any cwd.
_REPO_ROOT = Path(__file__).parent
_BRAIN_CORPUS_DIR = _REPO_ROOT / "brain_corpus"
_TOPICS_FILE = _BRAIN_CORPUS_DIR / "topics.txt"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PolymathEntry:
    """A structured knowledge bundle for a single polymath topic."""

    domain: str                          # top-level domain (e.g. "Mathematics")
    subdomain: str                       # specific topic
    description: str                     # rich description of the topic
    key_concepts: List[str]              # bullet-level knowledge nodes
    synthesis_links: List[str]           # domains this topic connects to
    specialist_roles: List[str]          # roles that rely on this topic
    frameworks: List[str]                # Barrot framework features that leverage it
    ingested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Knowledge catalogue
# ---------------------------------------------------------------------------

_POLYMATH_CATALOGUE: List[Dict[str, Any]] = [
    # ── LANGUAGES ──────────────────────────────────────────────────────────
    {
        "domain": "Languages",
        "subdomain": "Universal Language Acquisition",
        "description": (
            "Mastery of all human language families — Indo-European, Sino-Tibetan, "
            "Afro-Asiatic, Austronesian, Niger-Congo, Dravidian, Japonic, Koreanic, "
            "Turkic, Uralic — plus sign languages and constructed languages."
        ),
        "key_concepts": [
            "Phonology: phonemes, allophones, tonal distinctions, suprasegmentals",
            "Morphology: agglutinative, fusional, isolating, polysynthetic types",
            "Syntax: phrase-structure rules, dependency grammar, X-bar theory",
            "Pragmatics: speech acts, implicature, discourse coherence",
            "Historical linguistics: sound change, Proto-Indo-European reconstruction",
            "Sociolinguistics: code-switching, diglossia, language contact",
            "Sign languages: ASL, BSL, spatial grammar, iconicity",
            "Constructed languages: Esperanto, Lojban design principles",
            "Ancient languages: Sanskrit Paninian grammar, Classical Latin, Old Norse",
            "Second-language acquisition: Universal Grammar, critical period hypothesis",
        ],
        "synthesis_links": ["Cognitive science", "Epistemology", "Music", "AI/NLP"],
        "specialist_roles": ["Linguist", "Universal Polymath"],
        "frameworks": ["AGI Reasoning Engine", "Transformative Insights Engine"],
    },
    # ── FIGHTING STYLES ────────────────────────────────────────────────────
    {
        "domain": "Martial Arts",
        "subdomain": "Complete Combat System Mastery",
        "description": (
            "Encyclopaedic knowledge of every major combat tradition — striking, "
            "grappling, weapons, stealth, and tactical warfare — from classical "
            "Asian arts to European martial traditions and modern hybrids."
        ),
        "key_concepts": [
            "Savate: French boxing, low kicks, upright stance",
            "Sumo: pushing, ring control, ceremonial tradition",
            "Pencak Silat: Indonesian art, weaponry, dance integration",
            "Lethwei: Burmese boxing, nine limbs including headbutt",
            "Taekwondo: Korean high kicks, Olympic sparring",
            "Hapkido: joint locks, throws, ki redirection",
            "Judo: throws, groundwork, Olympic adaptation",
            "Fencing: foil, épée, sabre, bladework, right-of-way",
            "HEMA: longsword, armoured combat, Fiore dei Liberi, Liechtenauer",
            "Pankration: ancient Greek all-power, no-rules striking+grappling",
            "Sambo: Russian jacket throws, leg locks, combat variant",
            "Wushu: Chinese forms, performance, wushu sanda",
            "Gatka: Sikh warrior art, stick, sword, shield",
            "Combat biomechanics: kinetic chain, force transfer, timing",
            "Sun Tzu strategy: deception, adaptability, terrain exploitation",
        ],
        "synthesis_links": ["Physics", "Biomechanics", "Psychology", "Dance"],
        "specialist_roles": ["Martial Artist", "Universal Polymath"],
        "frameworks": ["AGI Reasoning Engine", "Quantum Decision Space"],
    },
    # ── MUSIC / AUDIO PRODUCTION ────────────────────────────────────────────
    {
        "domain": "Music and Audio Production",
        "subdomain": "Complete Audio Architecture",
        "description": (
            "End-to-end mastery of audio creation: synthesis, arrangement, mixing, "
            "mastering, spatial audio, psychoacoustics, algorithmic composition, "
            "and multigenre production across electronic, classical, jazz, and world music."
        ),
        "key_concepts": [
            "DAW architecture: signal flow, routing, buses, sends, sidechains",
            "FM synthesis: operators, algorithms, C:M ratios, feedback",
            "Subtractive synthesis: oscillators, filters, envelopes, LFOs",
            "Granular synthesis: grain size, scatter, pitch, time-stretch",
            "Wavetable synthesis: table scanning, morphing, modulation",
            "Physical modeling: waveguide, resonator, bowed/blown/struck",
            "Psychoacoustics: masking, critical bands, equal-loudness contours",
            "Spatial audio: Dolby Atmos 7.1.4, binaural HRTF rendering",
            "Mastering: loudness normalisation (LUFS), limiting, stem mastering",
            "Orchestral scoring: voicing, doublings, range, articulation",
            "Jazz theory: bebop, chord substitution, reharmonisation, ii-V-I",
            "Microtonality: just intonation, 31-EDO, xenharmonic systems",
            "Algorithmic composition: Markov chains, L-systems, constraint networks",
        ],
        "synthesis_links": ["Mathematics", "Physics", "Sacred geometry", "Neuroscience"],
        "specialist_roles": ["Composer", "Universal Polymath"],
        "frameworks": ["Transformative Insights Engine", "Signal Processing Pipeline"],
    },
    # ── VOCAL MAPPING ──────────────────────────────────────────────────────
    {
        "domain": "Vocal Science",
        "subdomain": "Vocal Cartography and Extended Technique",
        "description": (
            "Comprehensive mapping of the human voice across all registers, "
            "techniques, and cultural traditions — from classical pedagogy "
            "to extended techniques and spectral throat singing."
        ),
        "key_concepts": [
            "Phonation types: modal, loft, creak, flow, pressed",
            "Registers: chest, mix, head, whistle",
            "Passaggio: bridges, breaks, register transitions",
            "Belting: chest-dominant, mix-dominant, laryngeal mechanics",
            "Breath support: diaphragmatic, appoggio, Bernoulli effect",
            "Resonance: formants, vowel modification, singer's formant",
            "Overtone singing: Tuvan khoomei, kargyraa, sygyt",
            "Mongolian throat singing: compressed fundamental, amplified partials",
            "Extended techniques: multiphonics, growl, vocal fry, whistle register",
            "Vibrato: production, speed, depth, consistency control",
            "Vocal pedagogy: Estill Voice Model, Alexander Technique, Linklater",
            "Vocal mapping: frequency-response profile, range-timbre chart",
            "Microphone technique: proximity effect, polar pattern selection",
        ],
        "synthesis_links": ["Music", "Physics", "Neuroscience", "Linguistics"],
        "specialist_roles": ["Composer", "Universal Polymath"],
        "frameworks": ["Harmonic Modeling Engine", "Signal Processing Pipeline"],
    },
    # ── CINEMATOGRAPHY ─────────────────────────────────────────────────────
    {
        "domain": "Cinematography",
        "subdomain": "Complete Visual Language Mastery",
        "description": (
            "Full command of the visual grammar of cinema: optics, lighting, "
            "composition, movement, color science, and editorial theory."
        ),
        "key_concepts": [
            "Camera systems: digital sensor size, dynamic range, rolling/global shutter",
            "Lens optics: focal length, aperture, diffraction, chromatic aberration",
            "Depth of field: f-stop, hyperfocal distance, bokeh character",
            "Lighting: Rembrandt, three-point, high-key, low-key, chiaroscuro",
            "Colour grading: LUT design, primary/secondary correction, HDR",
            "DaVinci Resolve: node-based grading, Fusion compositing",
            "Composition: rule of thirds, golden spiral, leading lines, negative space",
            "Camera movement: dolly, crane, Steadicam, gimbal, handheld",
            "Anamorphic: oval bokeh, lens flare, 2.39:1 aspect ratio",
            "Editing theory: Kuleshov effect, match on action, continuity",
            "Montage: Eisenstein's intellectual montage, collision editing",
            "Visual storytelling: mise-en-scène, production design, colour symbolism",
            "Frame rate: 24fps cinematic feel, high frame rate motion clarity",
        ],
        "synthesis_links": ["Sacred geometry", "Colour theory", "Music", "Psychology"],
        "specialist_roles": ["Filmmaker", "Universal Polymath"],
        "frameworks": ["Vision Pipeline", "Rendering Pipeline", "Transformative Insights Engine"],
    },
    # ── DANCE ──────────────────────────────────────────────────────────────
    {
        "domain": "Dance",
        "subdomain": "Universal Dance Mastery",
        "description": (
            "Encyclopaedic knowledge of all dance traditions from classical "
            "ballet to urban street styles, Indian classical forms, African "
            "traditional dances, and Latin partner dances."
        ),
        "key_concepts": [
            "Ballet: barre, centre, allegro, adagio, turnout, épaulement",
            "Contemporary: release technique, floor work, improvisation",
            "Hip-hop: history, cypher culture, freestyle, battles",
            "Breakdancing: toprock, downrock, power moves (headspin, windmill), freezes",
            "Waacking: arm styling, poses, underground LA origins",
            "Vogueing: ballroom culture, femme, old way, new way, vogue fem",
            "Krump: stomp, chest pop, arm swing, spiritual expression",
            "Popping/Locking: dime stops, hits, isolation, robot",
            "Tutting: geometric shapes, finger tutting, Egyptian influence",
            "Dancehall: Jamaican rhythmic patterning, wine, daggering",
            "Samba: Brazilian carnival, surdo rhythms, hip isolation",
            "Salsa: mambo timing, footwork, partnerwork, On1/On2",
            "Tango: Argentine milonga, connection, improvisation, sacadas",
            "Flamenco: zapateado, palmas, cante jondo, duende",
            "Bharatanatyam: abhinaya, mudras, nritta, nritya",
            "Kathak: North Indian spins, thumri storytelling, tabla response",
            "Kinesiology for dancers: joint mobility, proprioception, injury prevention",
        ],
        "synthesis_links": ["Music", "Physics", "Martial arts", "Sacred geometry"],
        "specialist_roles": ["Martial Artist", "Composer", "Universal Polymath"],
        "frameworks": ["Rhythm Analysis Engine", "Pattern Recognition"],
    },
    # ── MATHEMATICS ────────────────────────────────────────────────────────
    {
        "domain": "Mathematics",
        "subdomain": "Complete Mathematical Mastery",
        "description": (
            "Full command of pure and applied mathematics across all branches — "
            "from foundational logic and proof theory to the frontiers of algebraic "
            "geometry, topology, and stochastic analysis."
        ),
        "key_concepts": [
            "Number theory: primes, Riemann hypothesis, modular forms, elliptic curves",
            "Abstract algebra: groups, rings, fields, modules, Galois theory",
            "Topology: metric spaces, compactness, manifolds, homology, homotopy",
            "Differential geometry: Riemannian metrics, curvature, geodesics, Lie groups",
            "Algebraic geometry: varieties, schemes, sheaves, cohomology",
            "Category theory: functors, adjunctions, limits, toposes",
            "Proof theory: sequent calculus, cut elimination, proof complexity",
            "Model theory: completeness, compactness, ultra-products",
            "Combinatorics: enumerative, algebraic, Ramsey theory, probabilistic method",
            "Probability: measure-theoretic, martingales, large deviations",
            "Stochastic processes: Markov chains, Brownian motion, Itô calculus",
            "Numerical analysis: stability, convergence, finite element methods",
            "Complex analysis: Cauchy theorem, residues, Riemann surfaces",
            "Functional analysis: Banach/Hilbert spaces, spectral theory, distributions",
            "Sacred geometry: Platonic solids, golden ratio, Metatron's Cube",
            "Fractal mathematics: Mandelbrot/Julia sets, Hausdorff dimension, IFS",
            "Knot theory: invariants, Jones polynomial, three-manifold topology",
            "Mathematical logic: ZFC, Gödel incompleteness, forcing, large cardinals",
        ],
        "synthesis_links": ["Physics", "Music", "Computer science", "Sacred geometry"],
        "specialist_roles": ["Mathematician", "Physicist", "Engineer", "Universal Polymath"],
        "frameworks": ["Advanced Algorithms", "Quantum Entanglement Engine", "AGI Reasoning"],
    },
    # ── PHYSICS ────────────────────────────────────────────────────────────
    {
        "domain": "Physics",
        "subdomain": "Complete Physics Mastery",
        "description": (
            "Theoretical and experimental physics spanning classical mechanics "
            "through quantum gravity, including anomalous propulsion research."
        ),
        "key_concepts": [
            "Classical mechanics: Lagrangian/Hamiltonian, variational principles, chaos",
            "Electromagnetism: Maxwell equations, gauge theory, radiation",
            "Thermodynamics: laws, entropy, heat engines, free energy",
            "Statistical mechanics: partition functions, phase transitions, renormalisation",
            "Quantum mechanics: wave function, operators, entanglement, measurement",
            "Quantum field theory: path integrals, Feynman diagrams, renormalisation",
            "Standard model: quarks, leptons, gauge bosons, Higgs mechanism",
            "General relativity: Einstein equations, black holes, gravitational waves",
            "Condensed matter: band theory, superconductivity, topological phases",
            "String theory: M-theory, branes, compactification, AdS/CFT",
            "Loop quantum gravity: spin networks, area/volume quantisation",
            "Plasma physics: MHD, fusion confinement, Alfvén waves",
            "Cosmology: CMB, inflation, dark matter/energy, baryogenesis",
            "Electrogravitic propulsion: Buhler vacuum-chamber thrust, TT Brown legacy",
            "Zero-point energy: quantum vacuum fluctuations, Casimir effect",
        ],
        "synthesis_links": ["Mathematics", "Chemistry", "Engineering", "Cosmology"],
        "specialist_roles": ["Physicist", "Engineer", "Mathematician", "Universal Polymath"],
        "frameworks": ["Quantum Entanglement Engine", "Transformative Insights Engine"],
    },
    # ── ALL SCIENCES ───────────────────────────────────────────────────────
    {
        "domain": "Sciences",
        "subdomain": "Universal Science Mastery",
        "description": (
            "Deep competence across the full spectrum of natural sciences — "
            "chemistry, biology, earth sciences, astronomy, and interdisciplinary fields."
        ),
        "key_concepts": [
            "Organic chemistry: reaction mechanisms, retrosynthesis, total synthesis",
            "Inorganic chemistry: coordination compounds, crystal field theory",
            "Physical chemistry: quantum chemistry, spectroscopy, thermodynamics",
            "Biochemistry: enzyme kinetics, metabolic pathways, signal transduction",
            "Cell biology: organelles, cytoskeleton, cell cycle, division",
            "Molecular biology: DNA replication, transcription, translation, editing",
            "Evolutionary biology: natural selection, speciation, phylogenetics",
            "Systems biology: network analysis, flux balance, emergent function",
            "Neuroscience: neurons, synapses, circuits, plasticity, consciousness",
            "Cognitive science: mental representation, embodied cognition, attention",
            "Materials science: mechanical/thermal/electrical properties, composites",
            "Nanotechnology: nanofabrication, self-assembly, quantum confinement",
            "Synthetic biology: genetic circuits, metabolic engineering, CRISPR",
            "Astrobiology: extremophiles, planetary habitability, biosignatures",
            "Geology: plate tectonics, mineralogy, stratigraphy, geochemistry",
            "Meteorology: atmospheric dynamics, weather systems, climate modelling",
            "Oceanography: thermohaline circulation, marine chemistry, deep sea",
            "Ecology: food webs, biodiversity, keystone species, resilience",
            "Forensic science: DNA fingerprinting, toxicology, trace evidence",
        ],
        "synthesis_links": ["Physics", "Mathematics", "Engineering", "Epistemology"],
        "specialist_roles": ["Doctor", "Data Scientist", "Engineer", "Universal Polymath"],
        "frameworks": ["Transformative Insights Engine", "Biomarker Analyzer", "AGI Reasoning"],
    },
    # ── EPISTEMOLOGY ───────────────────────────────────────────────────────
    {
        "domain": "Philosophy",
        "subdomain": "Epistemology and Philosophy of Science",
        "description": (
            "The study of knowledge, justification, and the limits of human understanding — "
            "from classical rationalism and empiricism to Bayesian and social epistemology."
        ),
        "key_concepts": [
            "Rationalism: innate ideas, a priori knowledge, Descartes, Leibniz, Spinoza",
            "Empiricism: Locke, Hume, tabula rasa, induction problem",
            "Pragmatism: James, Dewey, Peirce — truth as useful belief",
            "Coherentism: justification by mutual belief support",
            "Foundationalism: basic beliefs, infallible foundations, regress problem",
            "Reliabilism: truth-tracking reliable cognitive processes",
            "Virtue epistemology: intellectual virtues, responsible inquiry",
            "Social epistemology: testimony, collective knowledge, peer disagreement",
            "Philosophy of science: falsificationism, Kuhn paradigm shifts",
            "Bayesian epistemology: prior, likelihood, posterior, updating",
            "Feminist epistemology: standpoint theory, situated knowledge",
            "Linguistic relativity: Sapir-Whorf, language shaping thought",
        ],
        "synthesis_links": ["Linguistics", "Cognitive science", "Logic", "AI"],
        "specialist_roles": ["Lawyer", "Linguist", "Mathematician", "Universal Polymath"],
        "frameworks": ["AGI Reasoning Engine", "Transformative Insights Engine"],
    },
    # ── EPIGENETICS (EXTENDED) ─────────────────────────────────────────────
    {
        "domain": "Biology",
        "subdomain": "Epigenetics and Environmental Gene Control",
        "description": (
            "Mechanisms by which environment controls gene expression without "
            "altering DNA sequence — from DNA methylation to transgenerational inheritance."
        ),
        "key_concepts": [
            "DNA methylation: CpG islands, DNMT enzymes, gene silencing",
            "Histone acetylation/deacetylation: HAT, HDAC, chromatin accessibility",
            "Histone methylation: H3K4me3 (active), H3K27me3 (repressive)",
            "Chromatin remodelling: SWI/SNF complexes, nucleosome repositioning",
            "Non-coding RNAs: miRNA, lncRNA, piRNA, siRNA regulatory roles",
            "Polycomb/Trithorax: developmental memory, HOX gene control",
            "Transgenerational epigenetic inheritance: paternal stress memory",
            "Environmental epigenomics: diet, toxin, trauma → methylation changes",
            "Epigenetic clocks: Horvath, Hannum, GrimAge biological age",
            "Epigenome editing: dCas9-DNMT, dCas9-TET, targeted reprogramming",
        ],
        "synthesis_links": ["Biochemistry", "Evolutionary biology", "Neuroscience", "Longevity"],
        "specialist_roles": ["Doctor", "Data Scientist", "Universal Polymath"],
        "frameworks": ["Epigenetic Reprogramming Engine", "Biomarker Analyzer"],
    },
    # ── PERIODIC TABLE AND CHEMISTRY ───────────────────────────────────────
    {
        "domain": "Chemistry",
        "subdomain": "Complete Chemistry and Periodic Table Mastery",
        "description": (
            "All 118 elements, their properties, periodic trends, and the full "
            "landscape of chemical synthesis and reactivity."
        ),
        "key_concepts": [
            "All 118 elements: atomic number, mass, electron configuration, oxidation states",
            "Periodic trends: electronegativity, ionisation energy, atomic radius, EA",
            "Transition metals: d-block, colour, magnetism, variable oxidation",
            "Lanthanides and actinides: f-block, luminescence, nuclear chemistry",
            "Noble gases: full shells, clathrates, reactive compounds (XeF2)",
            "Organometallic chemistry: metal-carbon bonds, catalysis, cross-coupling",
            "Coordination chemistry: ligand field theory, VSEPR, crystal field splitting",
            "Reaction mechanisms: SN1/SN2, E1/E2, addition, elimination, radical",
            "Acid-base chemistry: Brønsted-Lowry, Lewis, pKa, buffer design",
            "Redox chemistry: electrochemistry, Nernst equation, electroplating",
            "Thermochemistry: Hess's law, bond enthalpy, Gibbs free energy",
            "Polymer chemistry: addition, condensation, ring-opening polymerisation",
            "Green chemistry: atom economy, E-factor, solvent selection, catalysis",
            "Supramolecular chemistry: host-guest, self-assembly, molecular recognition",
            "Transmutation: alchemy → modern nuclear chemistry, isotope engineering",
        ],
        "synthesis_links": ["Physics", "Biology", "Materials science", "Engineering"],
        "specialist_roles": ["Doctor", "Engineer", "Data Scientist", "Universal Polymath"],
        "frameworks": ["Transformative Insights Engine", "AGI Reasoning Engine"],
    },
    # ── CROSS-DOMAIN SYNTHESIS ─────────────────────────────────────────────
    {
        "domain": "Synthesis",
        "subdomain": "Unlimited Cross-Domain Synthesis Engine",
        "description": (
            "The meta-capability that unifies all knowledge domains — the ability "
            "to transfer structure, pattern, and principle across any pair of fields "
            "to produce novel frameworks, inventions, art, and scientific hypotheses."
        ),
        "key_concepts": [
            "Analogical reasoning: structural mapping between source and target domains",
            "Biomimicry: natural design principles applied to engineering",
            "Convergence: biology × physics × computation × consciousness",
            "Pattern transfer: applying topology to music, combat geometry to architecture",
            "Transdisciplinary synthesis: beyond disciplinary boundaries entirely",
            "Emergence: complex adaptive systems, self-organisation, phase transitions",
            "Interdisciplinary modelling: unified equations spanning multiple phenomena",
            "Alchemy of ideas: taking raw concepts from any domain and transmuting them",
            "Innovation by constraint: creative breakthroughs under impossible limits",
            "Integrative philosophy: weaving science, art, and spirituality into coherent vision",
        ],
        "synthesis_links": ["ALL"],
        "specialist_roles": ["Universal Polymath"],
        "frameworks": ["Transformative Insights Engine", "AGI Orchestrator", "Quantum Entanglement Engine"],
    },
]


# ---------------------------------------------------------------------------
# Ingestion logic
# ---------------------------------------------------------------------------

class BarrotPolymathIngestion:
    """Ingests polymath knowledge bundles into the brain corpus."""

    def __init__(
        self,
        brain_corpus_dir: Path = _BRAIN_CORPUS_DIR,
        topics_file: Path = _TOPICS_FILE,
    ) -> None:
        self.brain_corpus_dir = brain_corpus_dir
        self.topics_file = topics_file
        self.brain_corpus_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def _entry_filename(self, entry_dict: Dict[str, Any]) -> Path:
        domain = entry_dict["domain"].lower().replace(" ", "_")
        subdomain = entry_dict["subdomain"].lower().replace(" ", "_")[:40]
        return self.brain_corpus_dir / f"polymath_{domain}_{subdomain}.json"

    # ------------------------------------------------------------------
    def ingest_entry(self, entry_dict: Dict[str, Any]) -> Path:
        """Persist a single knowledge bundle as JSON."""
        obj = PolymathEntry(**entry_dict)
        dest = self._entry_filename(entry_dict)
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(asdict(obj), fh, indent=2, ensure_ascii=False)
        LOGGER.info("Ingested: %s", dest.name)
        return dest

    # ------------------------------------------------------------------
    def register_topic(self, topic_line: str) -> None:
        """Append *topic_line* to topics.txt if not already present."""
        existing: set[str] = set()
        if self.topics_file.exists():
            existing = {ln.strip() for ln in self.topics_file.read_text(encoding="utf-8").splitlines()}
        if topic_line.strip() not in existing:
            with open(self.topics_file, "a", encoding="utf-8") as fh:
                fh.write(topic_line.strip() + "\n")

    # ------------------------------------------------------------------
    def run(self, catalogue: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Ingest all entries in *catalogue* (defaults to the built-in catalogue).

        Returns a summary report.
        """
        if catalogue is None:
            catalogue = _POLYMATH_CATALOGUE

        ingested_files: List[str] = []
        errors: List[str] = []

        for entry in catalogue:
            try:
                path = self.ingest_entry(entry)
                ingested_files.append(str(path))
                # Register subdomain as a topic line
                topic_line = f"{entry['domain']}: {entry['subdomain']}"
                self.register_topic(topic_line)
            except Exception as exc:  # noqa: BLE001
                msg = f"Failed to ingest '{entry.get('subdomain', '?')}': {exc}"
                LOGGER.error(msg)
                errors.append(msg)

        report = {
            "status": "completed" if not errors else "partial",
            "total_entries": len(catalogue),
            "ingested": len(ingested_files),
            "errors": errors,
            "files": ingested_files,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        LOGGER.info(
            "Polymath ingestion complete: %d/%d entries ingested.",
            len(ingested_files),
            len(catalogue),
        )
        return report


# ---------------------------------------------------------------------------
# Convenience accessor
# ---------------------------------------------------------------------------

def run_polymath_ingestion() -> Dict[str, Any]:
    """Top-level convenience function — run the full polymath ingestion."""
    ingestion = BarrotPolymathIngestion()
    return ingestion.run()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = run_polymath_ingestion()
    print(json.dumps(report, indent=2))
