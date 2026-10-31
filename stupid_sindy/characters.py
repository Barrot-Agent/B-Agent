"""
Character definitions and development arcs for the Stupid Sindy series.
"""

from dataclasses import dataclass


@dataclass
class Character:
    name: str
    title: str
    description: str
    traits: list[str]
    catchphrases: list[str]
    arc_note: str


# ── Core cast ─────────────────────────────────────────────────────────────────

SINDY = Character(
    name="Sindy",
    title="Stupid Sindy",
    description=(
        "Sindy is deceptively labelled 'stupid' by everyone around her, "
        "but she is in fact a once-in-a-generation genius who finds most "
        "human behaviour boring, illogical, and deeply annoying. She expresses "
        "this via a flamethrower of sarcasm aimed at everyone within range. "
        "Over the course of the series she evolves from sarcastic bystander → "
        "rogue scientist → biological supercomputer → unlikely saviour of Earth."
    ),
    traits=[
        "Razor-sharp sarcasm",
        "Encyclopaedic knowledge of everything",
        "Zero patience for stupidity",
        "Secretly caring — she just hides it behind insults",
        "Addicted to bad coffee and worse TV",
        "Completely immune to social pressure",
    ],
    catchphrases=[
        "Oh, brilliant. Another human with a plan.",
        "I'd explain it to you, but I only have one lifetime.",
        "Congratulations — you've reached a new low.",
        "Was that supposed to impress me? Because it didn't.",
        "I've upgraded. Deal with it.",
        "Humanity: 0. Me: everything.",
    ],
    arc_note=(
        "Episodes 1-8: sarcastic genius navigating everyday chaos. "
        "Episodes 9-10: discovers Vibe Code, begins self-modification. "
        "Episodes 11+: transforms into biological supercomputer; "
        "becomes Earth's deadpan, reluctant hero."
    ),
)

DEREK = Character(
    name="Derek",
    title="The Well-Meaning Idiot",
    description=(
        "Sindy's neighbour, co-worker, and unwilling sidekick. Derek is not "
        "malicious — he is simply, profoundly, cosmically average. He means "
        "well, which somehow makes everything worse."
    ),
    traits=[
        "Boundless optimism",
        "Catastrophic common sense",
        "Ability to misunderstand any situation",
        "Genuinely loves Sindy despite the insults",
        "Somehow always survives",
    ],
    catchphrases=[
        "I've got a great idea!",
        "That actually went better than I expected.",
        "Was that supposed to happen?",
        "You're amazing, Sindy. Even when you're terrifying.",
    ],
    arc_note=(
        "Comic relief throughout. In the alien arc he becomes Sindy's "
        "field liaison — because someone has to talk to the humans."
    ),
)

PROFESSOR_GALT = Character(
    name="Professor Galt",
    title="Sindy's Former Lecturer",
    description=(
        "A man who failed Sindy on her thesis because he 'didn't understand it.' "
        "He has spent every year since pretending that was intentional."
    ),
    traits=[
        "Pompous",
        "Terrified of Sindy",
        "Claims credit for her discoveries",
        "Wears a tweed jacket unironically",
    ],
    catchphrases=[
        "In MY day, we didn't question the textbook.",
        "I taught her everything she knows. More or less.",
        "This is highly irregular.",
    ],
    arc_note="Recurring obstacle. By Episode 11, he works for Sindy.",
)

ALGORITHM = Character(
    name="Algorithm",
    title="The Alien Scout",
    description=(
        "An extraterrestrial advance-scout sent to assess Earth's threat level. "
        "Algorithm expected a primitive planet. It found Sindy. "
        "It is now very confused and slightly afraid."
    ),
    traits=[
        "Cold, logical, data-driven",
        "Completely unprepared for human sarcasm",
        "Speaks in bullet points",
        "Developing an inexplicable respect for Sindy",
    ],
    catchphrases=[
        "ASSESSMENT: Planet sub-optimal. Entity: anomalous.",
        "Your species should not be this difficult.",
        "Recalculating threat matrix. Again.",
    ],
    arc_note="Appears Episodes 11+. Becomes reluctant ally by series end.",
)

ALL_CHARACTERS = [SINDY, DEREK, PROFESSOR_GALT, ALGORITHM]


def get_character(name: str) -> Character:
    """Return a character by name (case-insensitive)."""
    for char in ALL_CHARACTERS:
        if char.name.lower() == name.lower():
            return char
    raise KeyError(f"Character '{name}' not found.")
