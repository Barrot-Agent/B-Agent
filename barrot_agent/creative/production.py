from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from barrot_agent.orchestration.shared_runtime import (
    Artifact,
    Checkpoint,
    CompletionGate,
    DurableStateStore,
    ExecutionRecord,
    Fingerprint,
    TaskState,
)


@dataclass
class ArtistBible:
    artist_id: str
    name: str
    island_identity: str
    musical_style: str
    visual_style: str
    character_rules: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SongBlueprint:
    song_id: str
    title: str
    theme: str
    arrangement: list[str]
    lyrics_outline: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProductionAsset:
    asset_id: str
    kind: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CreativeProductionRecord:
    production_id: str
    status: str
    artists: list[dict[str, Any]] = field(default_factory=list)
    songs: list[dict[str, Any]] = field(default_factory=list)
    assets: list[dict[str, Any]] = field(default_factory=list)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    execution_records: list[dict[str, Any]] = field(default_factory=list)
    completion_gate: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PerformanceEngine(Protocol):
    def generate(self, production: CreativeProductionRecord) -> ProductionAsset: ...


class LipSyncEngine(Protocol):
    def generate(self, production: CreativeProductionRecord) -> ProductionAsset: ...


class DanceEngine(Protocol):
    def generate(self, production: CreativeProductionRecord) -> ProductionAsset: ...


class AnimationEngine(Protocol):
    def generate(self, production: CreativeProductionRecord) -> ProductionAsset: ...


class VideoEngine(Protocol):
    def generate(self, production: CreativeProductionRecord) -> ProductionAsset: ...


class PendingEngine:
    def __init__(self, kind: str):
        self.kind = kind

    def generate(self, production: CreativeProductionRecord) -> ProductionAsset:
        return ProductionAsset(
            asset_id=Fingerprint.create(production.production_id, self.kind).value,
            kind=self.kind,
            status="PENDING",
            details={"reason": "No local backend configured; paid providers remain disabled by default."},
        )


class ProductionDirector:
    def __init__(
        self,
        workspace: str | Path,
        *,
        performance_engine: PerformanceEngine | None = None,
        lip_sync_engine: LipSyncEngine | None = None,
        dance_engine: DanceEngine | None = None,
        animation_engine: AnimationEngine | None = None,
        video_engine: VideoEngine | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.store = DurableStateStore(self.workspace, "barrot_creative")
        self.performance_engine = performance_engine or PendingEngine("performance")
        self.lip_sync_engine = lip_sync_engine or PendingEngine("lip_sync")
        self.dance_engine = dance_engine or PendingEngine("dance")
        self.animation_engine = animation_engine or PendingEngine("animation")
        self.video_engine = video_engine or PendingEngine("video")

    def run(self) -> CreativeProductionRecord:
        production = CreativeProductionRecord(production_id=Fingerprint.create("creative", int(time.time())).value[:24], status="PENDING")
        production.artists = [artist.to_dict() for artist in self._artists()]
        production.songs = [song.to_dict() for song in self._songs()]
        self._checkpoint(production, "ARTIST_BIBLES", "Prepared artist bibles and song blueprints.")
        pending_assets = [
            self.performance_engine.generate(production),
            self.lip_sync_engine.generate(production),
            self.dance_engine.generate(production),
            self.animation_engine.generate(production),
            self.video_engine.generate(production),
        ]
        production.assets = [asset.to_dict() for asset in pending_assets]
        for asset in pending_assets:
            production.execution_records.append(
                ExecutionRecord(
                    record_id=Fingerprint.create(production.production_id, asset.kind, asset.status).value,
                    operation=f"creative_{asset.kind}",
                    state=TaskState.CHECKPOINTED.value if asset.status == "PENDING" else TaskState.COMPLETE.value,
                    output_fingerprint=Fingerprint.create(asset.to_dict()).value,
                    response=asset.to_dict(),
                ).to_dict()
            )
        gate = CompletionGate(
            gate_id=Fingerprint.create(production.production_id, production.assets).value,
            requirements={
                "artist_bibles": len(production.artists) == 3,
                "song_blueprints": len(production.songs) == 3,
                "media_generated": all(asset["status"] == "COMPLETE" for asset in production.assets),
            },
            satisfied=False,
            unresolved=["Media backends are pending; no video or animation was claimed as generated."],
        )
        production.completion_gate = gate.to_dict()
        self._checkpoint(production, "PRODUCTION_QC", "Recorded pending media generation state.")
        self.store.write_state(production.production_id, production.to_dict(), fingerprint=Fingerprint.create("creative_bundle_v1").value)
        return production

    def _checkpoint(self, production: CreativeProductionRecord, state: str, summary: str) -> None:
        checkpoint = Checkpoint(
            checkpoint_id=Fingerprint.create(production.production_id, state, len(production.checkpoints)).value,
            task_id=production.production_id,
            state=state,
            summary=summary,
            fingerprint=Fingerprint.create(production.artists, production.songs, production.assets).value,
        )
        production.checkpoints.append(checkpoint.to_dict())
        self.store.write_checkpoint(checkpoint)

    @staticmethod
    def _artists() -> list[ArtistBible]:
        return [
            ArtistBible(
                artist_id="artist.marisele",
                name="Marisele Duvant",
                island_identity="Haiti / Guadeloupe diaspora",
                musical_style="kompa soul fused with cinematic pop",
                visual_style="royal carnival futurism",
                character_rules=["Lead with calm authority", "Maintain gold-indigo palette", "Use braided crown silhouette"],
            ),
            ArtistBible(
                artist_id="artist.nadira",
                name="Nadira Baptiste",
                island_identity="Trinidad and Tobago",
                musical_style="soca R&B with percussion-heavy hooks",
                visual_style="street mas choreography realism",
                character_rules=["High-motion performance energy", "Preserve feathered shoulder motif", "Keep warm copper color story"],
            ),
            ArtistBible(
                artist_id="artist.zaria",
                name="Zaria Mendez",
                island_identity="Dominican Republic / Puerto Rico Caribbean archipelago",
                musical_style="dembow-inflected art pop balladry",
                visual_style="moonlit waterfront surrealism",
                character_rules=["Soft-spoken off-stage, fierce on stage", "Preserve silver shell jewelry", "Keep ocean-night lighting cues"],
            ),
        ]

    @staticmethod
    def _songs() -> list[SongBlueprint]:
        return [
            SongBlueprint(
                song_id="song.1",
                title="Tide of Fire",
                theme="self-liberation through sisterhood",
                arrangement=["lead vocal", "counter-melody", "low harmony"],
                lyrics_outline=["call to awaken", "dance break", "collective vow"],
            ),
            SongBlueprint(
                song_id="song.2",
                title="Lantern Bay",
                theme="night harbor romance and ambition",
                arrangement=["whisper intro", "stacked chorus", "percussion outro"],
                lyrics_outline=["harbor scene", "promise", "departure"],
            ),
            SongBlueprint(
                song_id="song.3",
                title="Skyline Mas",
                theme="festival resilience after loss",
                arrangement=["solo verse", "trio refrain", "drum-led final hook"],
                lyrics_outline=["memory", "procession", "rebirth"],
            ),
        ]


def load_latest_creative_record(workspace: str | Path) -> dict[str, Any] | None:
    store = DurableStateStore(Path(workspace).resolve(), "barrot_creative")
    return store.load_state_by_fingerprint(Fingerprint.create("creative_bundle_v1").value)
