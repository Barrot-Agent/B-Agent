"""
Stupid Sindy – Free Video Production Series Generator
======================================================

Manages the 15-episode "Stupid Sindy" series: metadata, scripts,
character dialogue, and scene descriptions used by the video pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Character:
    name: str
    description: str
    catchphrase: str


@dataclass
class Scene:
    scene_number: int
    title: str
    location: str
    description: str
    dialogue: List[Dict[str, str]]  # [{"character": ..., "line": ...}]


@dataclass
class Episode:
    episode_number: int
    title: str
    description: str
    runtime_minutes: int
    characters: List[str]
    scenes: List[Scene]

    def full_script(self) -> str:
        """Return a formatted script string for the episode."""
        lines: List[str] = []
        lines.append(f"STUPID SINDY – Episode {self.episode_number}")
        lines.append(f'"{self.title}"')
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"DESCRIPTION: {self.description}")
        lines.append(f"RUNTIME: ~{self.runtime_minutes} minutes")
        lines.append(f"CAST: {', '.join(self.characters)}")
        lines.append("")
        for scene in self.scenes:
            lines.append(f"{'=' * 40}")
            lines.append(f"SCENE {scene.scene_number}: {scene.title}")
            lines.append(f"LOCATION: {scene.location}")
            lines.append(f"{scene.description}")
            lines.append("")
            for beat in scene.dialogue:
                char = beat["character"].upper()
                line = beat["line"]
                lines.append(f"{char}")
                lines.append(f"  {line}")
                lines.append("")
        lines.append("END OF EPISODE")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Series characters
# ---------------------------------------------------------------------------

CHARACTERS: Dict[str, Character] = {
    "Sindy": Character(
        name="Sindy",
        description="An overconfident aspiring influencer who somehow always ends up on camera during the worst moments.",
        catchphrase="I meant to do that.",
    ),
    "Dex": Character(
        name="Dex",
        description="Sindy's long-suffering cameraman who documents everything with deadpan commentary.",
        catchphrase="Rolling… unfortunately.",
    ),
    "Aunt Vera": Character(
        name="Aunt Vera",
        description="Sindy's no-nonsense aunt who shows up uninvited and accidentally steals every scene.",
        catchphrase="That's not how you do it. Here, let me.",
    ),
    "Bryce": Character(
        name="Bryce",
        description="A rival influencer with flawless presentation but nothing to say.",
        catchphrase="Hashtag blessed.",
    ),
    "Mango": Character(
        name="Mango",
        description="Sindy's hyperactive dog who has destroyed more shoots than anyone can count.",
        catchphrase="*barks enthusiastically*",
    ),
}

# ---------------------------------------------------------------------------
# 15-episode series
# ---------------------------------------------------------------------------


def _make_episode(
    num: int,
    title: str,
    description: str,
    runtime: int,
    scenes: List[Scene],
    extra_chars: List[str] | None = None,
) -> Episode:
    base_chars = ["Sindy", "Dex"]
    if extra_chars:
        base_chars += extra_chars
    return Episode(
        episode_number=num,
        title=title,
        description=description,
        runtime_minutes=runtime,
        characters=base_chars,
        scenes=scenes,
    )


EPISODES: List[Episode] = [
    _make_episode(
        1,
        "Pilot: Going Viral (The Wrong Way)",
        "Sindy attempts to film her first viral video but accidentally films a neighbourhood crime instead.",
        22,
        [
            Scene(
                1,
                "The Setup",
                "Sindy's living room",
                "Sindy outlines her grand plan to Dex, surrounded by ring lights and a greenscreen that keeps falling over.",
                [
                    {"character": "Sindy", "line": "Today is the day I become famous."},
                    {"character": "Dex", "line": "Rolling… unfortunately."},
                    {"character": "Sindy", "line": "Stop saying that."},
                ],
            ),
            Scene(
                2,
                "The Shoot",
                "Front garden",
                "Mango escapes and drags Sindy into the neighbour's garden mid-take.",
                [
                    {"character": "Sindy", "line": "MANGO! Not on camera!"},
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                ],
            ),
            Scene(
                3,
                "The Upload",
                "Sindy's bedroom",
                "The accidental footage of the neighbour's garden gnome smuggling ring goes viral.",
                [
                    {"character": "Sindy", "line": "I meant to do that."},
                    {"character": "Dex", "line": "No you didn't."},
                    {"character": "Sindy", "line": "Shh. We're famous."},
                ],
            ),
        ],
        ["Mango"],
    ),
    _make_episode(
        2,
        "Cooking with Chaos",
        "Sindy launches a cooking channel; Aunt Vera visits unannounced and takes over.",
        20,
        [
            Scene(
                1,
                "Kitchen Prep",
                "Kitchen",
                "Sindy arranges a beautiful flat lay of ingredients she cannot identify.",
                [
                    {"character": "Sindy", "line": "This is definitely saffron."},
                    {"character": "Dex", "line": "That's turmeric from a value pack."},
                ],
            ),
            Scene(
                2,
                "The Interruption",
                "Kitchen – continuous",
                "Aunt Vera arrives, dismisses Sindy's mise en place, and produces a roast from nowhere.",
                [
                    {"character": "Aunt Vera", "line": "That's not how you do it. Here, let me."},
                    {"character": "Sindy", "line": "This is MY show!"},
                    {"character": "Aunt Vera", "line": "Then why is the oven off?"},
                ],
            ),
            Scene(
                3,
                "The Aftermath",
                "Dining room",
                "The roast wins a comment-section poll as the best cooking video of the month.",
                [
                    {"character": "Sindy", "line": "I meant to bring her here."},
                    {"character": "Dex", "line": "You called her by accident."},
                ],
            ),
        ],
        ["Aunt Vera"],
    ),
    _make_episode(
        3,
        "Fitness Goals",
        "Sindy tries to film a workout routine; rivals Bryce in a spontaneous park-off.",
        18,
        [
            Scene(
                1,
                "Warm Up",
                "Park",
                "Sindy stretches dramatically while Dex films from a scooter.",
                [
                    {"character": "Sindy", "line": "Wellness is a journey."},
                    {"character": "Dex", "line": "You've been stretching for twenty minutes."},
                ],
            ),
            Scene(
                2,
                "The Challenge",
                "Park – open space",
                "Bryce jogs past, triggering an impromptu fitness influencer battle.",
                [
                    {"character": "Bryce", "line": "Hashtag blessed."},
                    {"character": "Sindy", "line": "Don't you dare hashtag in my park."},
                ],
            ),
            Scene(
                3,
                "The Collapse",
                "Park bench",
                "Both influencers run out of stamina simultaneously and agree to a truce.",
                [
                    {"character": "Sindy", "line": "I meant to pace myself."},
                    {"character": "Bryce", "line": "Same. Hashtag recovery."},
                ],
            ),
        ],
        ["Bryce"],
    ),
    _make_episode(
        4,
        "DIY Disaster",
        "Sindy documents a home renovation; the wall comes down but the content stays up.",
        24,
        [
            Scene(
                1,
                "Planning",
                "Living room",
                "Sindy studies a Pinterest board before picking up a sledgehammer.",
                [
                    {"character": "Sindy", "line": "It's just one wall."},
                    {"character": "Dex", "line": "That's load-bearing."},
                    {"character": "Sindy", "line": "How do you know that?"},
                    {"character": "Dex", "line": "The engineer sticker on it."},
                ],
            ),
            Scene(
                2,
                "The Swing",
                "Hallway",
                "The wall comes down. So does the ceiling light. Mango is fine.",
                [
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Sindy", "line": "Open plan. Very trendy."},
                ],
            ),
            Scene(
                3,
                "The Landlord's Call",
                "Garden – outside",
                "Sindy answers the landlord's call while standing in rubble.",
                [
                    {"character": "Sindy", "line": "I meant to create an open-plan space."},
                    {"character": "Dex", "line": "Rolling… unfortunately."},
                ],
            ),
        ],
        ["Mango"],
    ),
    _make_episode(
        5,
        "The Sponsorship",
        "Sindy lands her first brand deal; it turns out to be a sentient blender company with high expectations.",
        21,
        [
            Scene(
                1,
                "The Brief",
                "Sindy's desk",
                "Sindy reads a twelve-page brand document for a blender.",
                [
                    {"character": "Sindy", "line": "It says the blender has feelings."},
                    {"character": "Dex", "line": "That's a metaphor."},
                    {"character": "Sindy", "line": "The blender has a name. Gerald."},
                ],
            ),
            Scene(
                2,
                "The Ad",
                "Kitchen",
                "Sindy attempts an unboxing. Gerald explodes with kale.",
                [
                    {"character": "Sindy", "line": "Gerald, we talked about this."},
                    {"character": "Dex", "line": "Is that a warranty issue?"},
                ],
            ),
            Scene(
                3,
                "The Review",
                "Sindy's bedroom",
                "The clip of Gerald attacking Sindy goes viral; the blender company is delighted.",
                [
                    {"character": "Sindy", "line": "I meant to let Gerald express himself."},
                    {"character": "Dex", "line": "Gerald expressed himself on the ceiling."},
                ],
            ),
        ],
    ),
    _make_episode(
        6,
        "Road Trip (No Plan)",
        "Sindy decides to vlog a road trip with zero preparation. Dex brings a map. Sindy ignores it.",
        26,
        [
            Scene(
                1,
                "Departure",
                "Driveway",
                "The car is packed entirely with camera equipment and zero food.",
                [
                    {"character": "Sindy", "line": "Content first, provisions second."},
                    {"character": "Dex", "line": "We have no provisions."},
                ],
            ),
            Scene(
                2,
                "The Detour",
                "Country road",
                "They end up at a goat farm after Sindy misreads the map app.",
                [
                    {"character": "Sindy", "line": "This is better. Goats are very now."},
                    {"character": "Dex", "line": "A goat is eating the lens cap."},
                ],
            ),
            Scene(
                3,
                "The Return",
                "Home driveway",
                "They return with 40 goat videos and no destination footage.",
                [
                    {"character": "Sindy", "line": "I meant to go to the goat farm all along."},
                    {"character": "Dex", "line": "You called it a five-star resort."},
                ],
            ),
        ],
    ),
    _make_episode(
        7,
        "Pet Influencer",
        "Sindy tries to make Mango a star. Mango has other ideas.",
        19,
        [
            Scene(
                1,
                "Mango's Debut",
                "Living room studio",
                "Sindy sets up a tiny desk for Mango's 'review' channel.",
                [
                    {"character": "Sindy", "line": "You're going to be a star, Mango."},
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Dex", "line": "He's eaten the script."},
                ],
            ),
            Scene(
                2,
                "The Performance",
                "Living room",
                "Mango reviews a sock, a cushion, and Dex's sandwich with equal enthusiasm.",
                [
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Sindy", "line": "And what do you give the sandwich?"},
                    {"character": "Mango", "line": "*eats sandwich*"},
                ],
            ),
            Scene(
                3,
                "The Metrics",
                "Sindy's phone",
                "Mango's channel surpasses Sindy's in followers within six hours.",
                [
                    {"character": "Sindy", "line": "I meant for him to be more famous than me."},
                    {"character": "Dex", "line": "You cried for twenty minutes."},
                ],
            ),
        ],
        ["Mango"],
    ),
    _make_episode(
        8,
        "The Collaboration",
        "Sindy and Bryce attempt a collab; creative differences emerge immediately.",
        23,
        [
            Scene(
                1,
                "The Meeting",
                "Coffee shop",
                "Sindy and Bryce present opposing 40-slide decks simultaneously.",
                [
                    {"character": "Bryce", "line": "My brand is aspirational."},
                    {"character": "Sindy", "line": "My brand is authentic chaos."},
                    {"character": "Dex", "line": "That's the first honest thing you've said."},
                ],
            ),
            Scene(
                2,
                "The Shoot",
                "Rooftop",
                "They attempt to film together but argue over every camera angle.",
                [
                    {"character": "Bryce", "line": "Hashtag blessed golden hour."},
                    {"character": "Sindy", "line": "Stop hashtagging out loud!"},
                ],
            ),
            Scene(
                3,
                "The Edit",
                "Dex's laptop",
                "Their combined footage is accidentally perfect. Neither will admit the other helped.",
                [
                    {"character": "Sindy", "line": "I carried this."},
                    {"character": "Bryce", "line": "Hashtag teamwork."},
                    {"character": "Dex", "line": "I quit. Again."},
                ],
            ),
        ],
        ["Bryce"],
    ),
    _make_episode(
        9,
        "Haunted House Content",
        "Sindy visits a reportedly haunted house for Halloween content. Aunt Vera has been living there.",
        25,
        [
            Scene(
                1,
                "The Arrival",
                "Outside old house",
                "Sindy films an intro in the dark. A light turns on upstairs.",
                [
                    {"character": "Sindy", "line": "We are definitely alone here."},
                    {"character": "Dex", "line": "There's a light on."},
                    {"character": "Sindy", "line": "That's ambiance."},
                ],
            ),
            Scene(
                2,
                "The Reveal",
                "Upstairs hallway",
                "Aunt Vera emerges in a dressing gown, furious that anyone knocked at 9pm.",
                [
                    {
                        "character": "Aunt Vera",
                        "line": "This is my house. I bought it at auction. Go away.",
                    },
                    {"character": "Sindy", "line": "GHOST!"},
                    {"character": "Aunt Vera", "line": "I'm your aunt, you idiot."},
                ],
            ),
            Scene(
                3,
                "Tea and Trauma",
                "Aunt Vera's kitchen",
                "They end up having tea. Dex documents everything.",
                [
                    {"character": "Sindy", "line": "I meant to find her."},
                    {"character": "Dex", "line": "You screamed for four minutes."},
                    {"character": "Aunt Vera", "line": "Biscuit?"},
                ],
            ),
        ],
        ["Aunt Vera"],
    ),
    _make_episode(
        10,
        "The Interview",
        "Sindy attempts to interview a local councillor. Mango conducts a better interview.",
        20,
        [
            Scene(
                1,
                "Prep",
                "Sindy's living room",
                "Sindy practises hard-hitting questions. All of them are about the colour of the town hall.",
                [
                    {"character": "Sindy", "line": "This is journalism."},
                    {"character": "Dex", "line": "You have one question."},
                    {"character": "Sindy", "line": "It's a very important colour."},
                ],
            ),
            Scene(
                2,
                "The Interview",
                "Town hall steps",
                "Mango escapes the bag and sits attentively while the councillor addresses all answers to the dog.",
                [
                    {"character": "Mango", "line": "*listens with apparent intelligence*"},
                    {"character": "Sindy", "line": "He's not even registered to vote!"},
                ],
            ),
            Scene(
                3,
                "The Aftermath",
                "Car park",
                "Mango's interview clip is cited in a local paper. Sindy is not mentioned.",
                [
                    {"character": "Sindy", "line": "I meant to feature Mango prominently."},
                    {"character": "Dex", "line": "You tried to zip him in a tote bag."},
                ],
            ),
        ],
        ["Mango"],
    ),
    _make_episode(
        11,
        "Sindy vs Tech Support",
        "Sindy's entire editing setup crashes mid-project; she films the 45-minute support call.",
        22,
        [
            Scene(
                1,
                "The Crash",
                "Editing suite (bedroom)",
                "Everything stops working at the worst possible moment.",
                [
                    {"character": "Sindy", "line": "It was fine this morning."},
                    {"character": "Dex", "line": "You poured tea into the keyboard."},
                    {"character": "Sindy", "line": "That's not confirmed."},
                ],
            ),
            Scene(
                2,
                "On Hold",
                "Same bedroom",
                "Sindy is on hold for 40 minutes. Dex films every minute.",
                [
                    {"character": "Sindy", "line": "This hold music is actually a bop."},
                    {"character": "Dex", "line": "You've been asleep for ten minutes."},
                ],
            ),
            Scene(
                3,
                "Resolution",
                "Bedroom",
                "The fix is turning it off and on again. The 45-minute call becomes their most-watched video.",
                [
                    {"character": "Sindy", "line": "I meant to document the whole process."},
                    {"character": "Dex", "line": "You snored through the climax."},
                ],
            ),
        ],
    ),
    _make_episode(
        12,
        "The Awards Show",
        "Sindy is nominated for a community media award. She prepares an acceptance speech for every category.",
        21,
        [
            Scene(
                1,
                "The Nomination",
                "Sindy's phone",
                "Sindy discovers she's been nominated for 'Most Unexpected Content Creator'.",
                [
                    {"character": "Sindy", "line": "That's an insult. I accept."},
                    {"character": "Dex", "line": "It comes with a voucher for a sandwich."},
                ],
            ),
            Scene(
                2,
                "The Ceremony",
                "Community centre",
                "Sindy delivers a seven-minute acceptance speech before the winner is announced.",
                [
                    {"character": "Sindy", "line": "I'd like to thank my camera—"},
                    {"character": "Host", "line": "The winner is Mango the Dog."},
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                ],
            ),
            Scene(
                3,
                "The After Party",
                "Car park",
                "Sindy holds Mango's voucher while Dex photographs the trophy.",
                [
                    {"character": "Sindy", "line": "I meant to train him for this."},
                    {"character": "Dex", "line": "He accepts the voucher with dignity."},
                ],
            ),
        ],
        ["Mango"],
    ),
    _make_episode(
        13,
        "The Brand Rebrand",
        "Sindy decides to pivot her brand three times in one afternoon. Bryce watches with concern.",
        19,
        [
            Scene(
                1,
                "Pivot One",
                "Sindy's living room",
                "Sindy announces a switch to 'serious documentary journalism'.",
                [
                    {"character": "Sindy", "line": "I'm done with chaos content."},
                    {"character": "Dex", "line": "You tripped over the tripod saying that."},
                ],
            ),
            Scene(
                2,
                "Pivot Two",
                "Same living room",
                "Sindy pivots to 'luxury lifestyle' content while wearing a borrowed top.",
                [
                    {"character": "Bryce", "line": "That's my top."},
                    {"character": "Sindy", "line": "It's a loan. For authenticity."},
                ],
            ),
            Scene(
                3,
                "Pivot Three",
                "Same living room",
                "Sindy returns to chaos content and the audience exhales with relief.",
                [
                    {"character": "Sindy", "line": "I was always going to come back."},
                    {"character": "Dex", "line": "You sent three farewell emails."},
                    {"character": "Sindy", "line": "I meant to."},
                ],
            ),
        ],
        ["Bryce"],
    ),
    _make_episode(
        14,
        "The Finale Teaser",
        "Everyone gathers to plan the season finale. Nothing is agreed but the tea is excellent.",
        23,
        [
            Scene(
                1,
                "The Meeting",
                "Aunt Vera's kitchen",
                "The full cast convenes to plan a grand finale. Mango brings a toy.",
                [
                    {"character": "Aunt Vera", "line": "I have a plan."},
                    {"character": "Sindy", "line": "So do I."},
                    {"character": "Bryce", "line": "Hashtag synergy."},
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Dex", "line": "Rolling… unfortunately."},
                ],
            ),
            Scene(
                2,
                "The Disagreement",
                "Same kitchen",
                "All five plans are presented. None are compatible. Vera makes more tea.",
                [
                    {"character": "Aunt Vera", "line": "Biscuit? It helps."},
                    {"character": "Sindy", "line": "We need ONE plan."},
                    {"character": "Bryce", "line": "Mine is already hashtagged."},
                ],
            ),
            Scene(
                3,
                "The Agreement",
                "Same kitchen",
                "They agree on tea, biscuits, and to 'figure it out on the day'.",
                [
                    {"character": "Sindy", "line": "I meant for this to be productive."},
                    {"character": "Dex", "line": "We had seventeen biscuits."},
                    {"character": "Aunt Vera", "line": "That IS productive."},
                ],
            ),
        ],
        ["Aunt Vera", "Bryce", "Mango"],
    ),
    _make_episode(
        15,
        "Grand Finale: I Meant To Do That",
        "The season finale: every plan goes wrong, everything works out, and Sindy uploads it all anyway.",
        30,
        [
            Scene(
                1,
                "The Grand Setup",
                "Hired community hall",
                "Sindy has rented a hall, hired a drone, and invited the whole neighbourhood.",
                [
                    {"character": "Sindy", "line": "This is our magnum opus."},
                    {"character": "Dex", "line": "The drone just flew into the bunting."},
                    {"character": "Sindy", "line": "Artistic choice."},
                ],
            ),
            Scene(
                2,
                "The Chaos",
                "Community hall – during event",
                "Mango chases Bryce's ring light. Vera takes over the PA system. The drone returns trailing bunting.",
                [
                    {"character": "Aunt Vera", "line": "ATTENTION EVERYONE. I have announcements."},
                    {"character": "Bryce", "line": "That's MY ring light! MANGO!"},
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Dex", "line": "I'm getting all of this."},
                ],
            ),
            Scene(
                3,
                "The Upload",
                "Outside community hall",
                "They watch the video together. It's chaotic, warm, and completely them.",
                [
                    {
                        "character": "Sindy",
                        "line": "I meant for every single thing to happen exactly like that.",
                    },
                    {"character": "Dex", "line": "You know what? I actually believe you."},
                    {
                        "character": "Aunt Vera",
                        "line": "Good. Now someone help me with this bunting.",
                    },
                    {"character": "Mango", "line": "*barks enthusiastically*"},
                    {"character": "Bryce", "line": "Hashtag… family."},
                ],
            ),
        ],
        ["Aunt Vera", "Bryce", "Mango"],
    ),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_episode(episode_number: int) -> Episode:
    """Return Episode by 1-based number (1–15)."""
    if not 1 <= episode_number <= 15:
        raise ValueError(f"Episode number must be 1–15, got {episode_number}")
    return EPISODES[episode_number - 1]


def get_all_episodes() -> List[Episode]:
    """Return all 15 episodes."""
    return EPISODES


def get_character(name: str) -> Character:
    """Return Character by name."""
    if name not in CHARACTERS:
        raise KeyError(f"Unknown character: {name!r}")
    return CHARACTERS[name]


def get_all_characters() -> Dict[str, Character]:
    """Return all characters."""
    return CHARACTERS


def episode_summary_card(episode: Episode) -> Dict[str, str]:
    """Return a dict suitable for display in a UI card."""
    return {
        "number": str(episode.episode_number),
        "title": episode.title,
        "description": episode.description,
        "runtime": f"{episode.runtime_minutes} min",
        "cast": ", ".join(episode.characters),
        "scenes": str(len(episode.scenes)),
    }
