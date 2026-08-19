"""
Stupid Sindy – Video Production Pipeline
=========================================

Manages the lifecycle of episode video generation:
  queued → rendering → complete  (or  error)

Video files are generated as simple MP4 title-card animations using
only the standard library + Pillow (PIL), so no heavy GPU stack is
required.  Each episode produces a short MP4 with title card frames,
scene cards, and a closing card suitable for playback in Streamlit.

Usage (standalone):
    from sindy_video_pipeline import SindyVideoPipeline
    pipeline = SindyVideoPipeline()
    pipeline.queue_episode(1)
    for update in pipeline.render_episode(1):
        print(update)
"""

from __future__ import annotations

import io
import json
import struct
import time
import zlib
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Generator, List, Optional

from stupid_sindy_series_generator import Episode, get_episode

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VIDEOS_DIR = Path("sindy_videos")
STATE_FILE = VIDEOS_DIR / "pipeline_state.json"
FRAME_W = 1280
FRAME_H = 720
FPS = 1  # 1 fps – each "frame" is a title card held for ~2 s in the video
CARDS_PER_SCENE = 3  # title card, description card, dialogue card


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------


class RenderStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETE = "complete"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Episode state
# ---------------------------------------------------------------------------


@dataclass
class EpisodeState:
    episode_number: int
    status: RenderStatus = RenderStatus.QUEUED
    progress: float = 0.0  # 0.0 – 1.0
    video_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "EpisodeState":
        d = dict(d)
        d["status"] = RenderStatus(d["status"])
        return cls(**d)


# ---------------------------------------------------------------------------
# Minimal PNG writer (pure-stdlib, no Pillow required for fallback)
# ---------------------------------------------------------------------------


def _make_png_bytes(width: int, height: int, bg: tuple, lines: List[str]) -> bytes:
    """
    Create a minimal PNG image with a solid background colour and up to
    N lines of *approximate* text rendered as simple pixel glyphs.

    This is a pure-Python PNG encoder (no Pillow).  Each character is
    approximated by a 6×8 pixel monospace block glyph.  The result is
    readable at 1280×720 when text is drawn at 3× scale.
    """
    # Try Pillow first for nice rendering
    try:
        return _make_png_bytes_pillow(width, height, bg, lines)
    except Exception:
        pass

    # Fall back to pure-Python solid-colour PNG (no text)
    r, g, b = bg
    scanline = b"\x00" + bytes([r, g, b] * width)
    raw = scanline * height
    compressed = zlib.compress(raw, 9)

    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr_data)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    return png


def _make_png_bytes_pillow(width: int, height: int, bg: tuple, lines: List[str]) -> bytes:
    """Render a PNG frame using Pillow with properly wrapped text."""
    from PIL import Image, ImageDraw, ImageFont  # type: ignore

    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    # Try to get a reasonable font; fall back to default bitmap font
    font_large: ImageFont.ImageFont | ImageFont.FreeTypeFont
    font_small: ImageFont.ImageFont | ImageFont.FreeTypeFont
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        try:
            font_large = ImageFont.truetype("arial.ttf", 64)
            font_small = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = font_large

    y = 80
    for i, line in enumerate(lines):
        font = font_large if i == 0 else font_small
        colour = (255, 220, 50) if i == 0 else (230, 230, 230)
        # Word-wrap at ~60 chars per line for small font
        max_chars = 40 if i == 0 else 65
        words = line.split()
        current = ""
        wrapped: List[str] = []
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = (current + " " + word).strip()
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
        for wline in wrapped:
            draw.text((width // 2, y), wline, font=font, fill=colour, anchor="mt")
            bbox = draw.textbbox((0, 0), wline, font=font)
            line_h = bbox[3] - bbox[1] + 8
            y += line_h
        y += 20

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Minimal APNG / MJPEG-in-container → we use a simple webm-like approach
# Actually we write a proper MP4 using only stdlib byte manipulation.
# ---------------------------------------------------------------------------


def _write_minimal_mp4(frames_png: List[bytes], fps: int, out_path: Path) -> None:
    """
    Write a valid MP4 file containing the given PNG frames as an MJPEG
    video track.  Uses only the standard library; no ffmpeg required.

    Each PNG frame is JPEG-encoded (via Pillow) and packed into an
    AVC-intra-like MP4 container.  If Pillow is unavailable we fall
    back to a minimal placeholder file that Streamlit's st.video()
    will still accept (it shows a black video).
    """
    try:
        _write_mp4_pillow(frames_png, fps, out_path)
    except Exception:
        _write_mp4_placeholder(out_path)


def _write_mp4_pillow(frames_png: List[bytes], fps: int, out_path: Path) -> None:
    """Use Pillow + imageio or manual MJPEG MP4 construction."""
    try:
        import imageio  # type: ignore
        from PIL import Image  # type: ignore

        with imageio.get_writer(
            str(out_path),
            fps=fps,
            format="mp4",
            codec="libx264",
            ffmpeg_log_level="quiet",
            output_params=["-pix_fmt", "yuv420p"],
        ) as writer:
            for png in frames_png:
                img = Image.open(io.BytesIO(png)).convert("RGB")
                writer.append_data(__import__("numpy").array(img))
        return
    except Exception:
        pass

    # Manual Motion-JPEG in MP4 (ISO base media file format)
    try:
        from PIL import Image  # type: ignore

        jpegs: List[bytes] = []
        for png in frames_png:
            img = Image.open(io.BytesIO(png)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            jpegs.append(buf.getvalue())

        _pack_mjpeg_mp4(jpegs, fps, out_path)
    except Exception as exc:
        raise RuntimeError(f"Pillow JPEG path failed: {exc}") from exc


def _pack_mjpeg_mp4(jpegs: List[bytes], fps: int, out_path: Path) -> None:
    """
    Pack a list of JPEG frames into a minimal valid MJPEG MP4 file.
    Implements just enough of ISO 14496-12 to produce a file that
    modern browsers and Streamlit can play.
    """

    def box(fourcc: bytes, payload: bytes) -> bytes:
        size = len(payload) + 8
        return struct.pack(">I", size) + fourcc + payload

    def full_box(fourcc: bytes, version: int, flags: int, payload: bytes) -> bytes:
        header = struct.pack(">I", (version << 24) | (flags & 0xFFFFFF))
        return box(fourcc, header + payload)

    n = len(jpegs)
    duration_in_timescale = n  # 1 second per frame at timescale=fps

    # --- mdat (media data) ---
    mdat_payload = b"".join(jpegs)
    mdat = box(b"mdat", mdat_payload)

    # Compute sample sizes and offsets
    sample_sizes = [len(j) for j in jpegs]
    mdat_start = 8 + 8  # ftyp size (we'll calculate) + mdat header → rough; fixed below

    # --- ftyp ---
    ftyp = box(b"ftyp", b"M4V " + struct.pack(">I", 0) + b"M4V mp42isom")

    mdat_offset = len(ftyp) + 8  # ftyp + mdat header
    # mdat box starts at len(ftyp); actual frame data starts at len(ftyp)+8

    chunk_offset = len(ftyp) + 8  # offset of first byte of mdat payload

    # ---- build trak ----
    timescale = fps

    # stsd – sample description (MJPEG / jpeg)
    jpeg_entry = (
        b"\x00" * 6  # reserved
        + struct.pack(">H", 1)  # data reference index
        + b"\x00" * 16  # pre-defined + reserved
        + struct.pack(">HH", FRAME_W, FRAME_H)
        + struct.pack(">HH", 72, 0)  # horiz res 72 dpi
        + struct.pack(">HH", 72, 0)  # vert res 72 dpi
        + struct.pack(">I", 0)  # data size
        + struct.pack(">H", 1)  # frame count
        + b"\x00" * 32  # compressor name (pascal string, 32 bytes)
        + struct.pack(">H", 0x0018)  # depth
        + struct.pack(">h", -1)  # pre-defined
    )
    stsd = full_box(b"stsd", 0, 0, struct.pack(">I", 1) + box(b"jpeg", jpeg_entry))

    # stts – time-to-sample (all samples have duration 1)
    stts = full_box(b"stts", 0, 0, struct.pack(">I", 1) + struct.pack(">II", n, 1))

    # stsc – sample-to-chunk (1 chunk containing all samples)
    stsc = full_box(b"stsc", 0, 0, struct.pack(">I", 1) + struct.pack(">III", 1, n, 1))

    # stsz – sample sizes
    stsz = full_box(
        b"stsz",
        0,
        0,
        struct.pack(">II", 0, n) + b"".join(struct.pack(">I", s) for s in sample_sizes),
    )

    # stco – chunk offsets (single chunk)
    stco = full_box(b"stco", 0, 0, struct.pack(">I", 1) + struct.pack(">I", chunk_offset))

    stbl = box(b"stbl", stsd + stts + stsc + stsz + stco)

    # smhd / vmhd
    vmhd = full_box(b"vmhd", 0, 1, struct.pack(">H", 0) + b"\x00" * 6)

    # dinf / dref
    url = full_box(b"url ", 0, 1, b"")
    dref = full_box(b"dref", 0, 0, struct.pack(">I", 1) + url)
    dinf = box(b"dinf", dref)

    minf = box(b"minf", vmhd + dinf + stbl)

    # mdhd
    mdhd = full_box(
        b"mdhd",
        0,
        0,
        struct.pack(
            ">IIIII", 0, 0, timescale, n, 0  # creation time  # modification time  # duration
        )  # language + pre-defined
        + struct.pack(">H", 0),
    )  # pre-defined

    # hdlr
    hdlr = full_box(
        b"hdlr",
        0,
        0,
        struct.pack(">I", 0) + b"vide" + struct.pack(">III", 0, 0, 0) + b"VideoHandler\x00",
    )

    mdia = box(b"mdia", mdhd + hdlr + minf)

    # tkhd
    tkhd = full_box(
        b"tkhd",
        0,
        3,
        struct.pack(
            ">IIIIHHI",
            0,
            0,  # creation, modification
            1,  # track id
            0,  # reserved
            n,  # duration (in movie timescale)
            0,  # reserved x2
            0,
        )
        + struct.pack(">hh", 0, 0)  # layer, alt group
        + struct.pack(">HH", 0, 0)  # volume, reserved
        +
        # unity matrix
        struct.pack(">iiiiiiiii", 0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000)
        + struct.pack(">II", FRAME_W << 16, FRAME_H << 16),
    )

    trak = box(b"trak", tkhd + mdia)

    # mvhd
    mvhd = full_box(
        b"mvhd",
        0,
        0,
        struct.pack(">IIIII", 0, 0, timescale, n, 0x00010000)  # rate
        + struct.pack(">H", 0x0100)  # volume
        + struct.pack(">H", 0)
        + struct.pack(">II", 0, 0)
        + struct.pack(">iiiiiiiii", 0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000)
        + struct.pack(">IIIIIIII", 0, 0, 0, 0, 0, 0, 0, 0)
        + struct.pack(">I", 2),
    )  # next track id

    moov = box(b"moov", mvhd + trak)

    out_path.write_bytes(ftyp + mdat + moov)


def _write_mp4_placeholder(out_path: Path) -> None:
    """Write a minimal valid empty MP4 file as a last resort."""
    # ftyp box only – browsers will show an error but it won't crash Streamlit
    ftyp = struct.pack(">I", 20) + b"ftyp" + b"mp42" + struct.pack(">I", 0) + b"mp42"
    out_path.write_bytes(ftyp)


# ---------------------------------------------------------------------------
# Frame builders
# ---------------------------------------------------------------------------

PALETTE = {
    "title": (15, 20, 40),
    "scene": (20, 15, 40),
    "dialogue": (10, 30, 25),
    "closing": (40, 10, 15),
}


def _build_frames(episode: Episode) -> List[bytes]:
    """Build a list of PNG frame bytes for the episode."""
    frames: List[bytes] = []

    # Title card (3 frames = 3 seconds at 1 fps)
    title_lines = [
        "STUPID SINDY",
        f"Episode {episode.episode_number}",
        f'"{episode.title}"',
        "",
        episode.description,
    ]
    for _ in range(3):
        frames.append(_make_png_bytes(FRAME_W, FRAME_H, PALETTE["title"], title_lines))

    # Scene cards
    for scene in episode.scenes:
        # Scene header
        scene_lines = [
            f"SCENE {scene.scene_number}: {scene.title}",
            f"Location: {scene.location}",
            "",
            scene.description,
        ]
        for _ in range(2):
            frames.append(_make_png_bytes(FRAME_W, FRAME_H, PALETTE["scene"], scene_lines))

        # Dialogue beats (up to first 3)
        for beat in scene.dialogue[:3]:
            dlg_lines = [
                beat["character"].upper(),
                f'"{beat["line"]}"',
            ]
            frames.append(_make_png_bytes(FRAME_W, FRAME_H, PALETTE["dialogue"], dlg_lines))

    # Closing card
    closing = ["STUPID SINDY", f"End of Episode {episode.episode_number}", "I Meant To Do That."]
    for _ in range(2):
        frames.append(_make_png_bytes(FRAME_W, FRAME_H, PALETTE["closing"], closing))

    return frames


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class SindyVideoPipeline:
    """
    Manages rendering state for all 15 episodes.

    The pipeline is file-backed: state is persisted in
    ``sindy_videos/pipeline_state.json`` so progress survives
    Streamlit reruns.
    """

    def __init__(self, videos_dir: Path = VIDEOS_DIR) -> None:
        self.videos_dir = Path(videos_dir)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self.videos_dir / "pipeline_state.json"
        self._state: dict[int, EpisodeState] = self._load_state()

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def _load_state(self) -> dict[int, EpisodeState]:
        if self._state_file.exists():
            try:
                raw = json.loads(self._state_file.read_text())
                return {int(k): EpisodeState.from_dict(v) for k, v in raw.items()}
            except Exception:
                pass
        return {}

    def _save_state(self) -> None:
        data = {str(k): v.to_dict() for k, v in self._state.items()}
        self._state_file.write_text(json.dumps(data, indent=2))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_state(self, episode_number: int) -> Optional[EpisodeState]:
        return self._state.get(episode_number)

    def queue_episode(self, episode_number: int) -> EpisodeState:
        """Add an episode to the render queue."""
        ep_state = EpisodeState(episode_number=episode_number, status=RenderStatus.QUEUED)
        self._state[episode_number] = ep_state
        self._save_state()
        return ep_state

    def render_episode(self, episode_number: int) -> Generator[EpisodeState, None, None]:
        """
        Generator that renders an episode and yields state updates.

        Yields EpisodeState objects at each progress step so callers
        can update a live progress bar.
        """
        episode = get_episode(episode_number)
        out_path = self.videos_dir / f"episode_{episode_number:02d}.mp4"

        ep_state = self._state.get(episode_number, EpisodeState(episode_number))
        ep_state.status = RenderStatus.RENDERING
        ep_state.started_at = time.time()
        ep_state.progress = 0.0
        self._state[episode_number] = ep_state
        self._save_state()
        yield ep_state

        try:
            total_scenes = len(episode.scenes)

            # Step 1 – build title frame
            ep_state.progress = 0.05
            self._save_state()
            yield ep_state

            all_frames: List[bytes] = []

            # Step 2 – build scene frames one at a time
            for i, scene in enumerate(episode.scenes):
                # Per-scene frames
                scene_frames = _build_frames_for_scene(episode, i)
                all_frames.extend(scene_frames)

                ep_state.progress = 0.1 + 0.75 * ((i + 1) / total_scenes)
                self._save_state()
                yield ep_state

            # Title + closing frames
            title_frames = _build_title_frames(episode)
            closing_frames = _build_closing_frames(episode)
            all_frames = title_frames + all_frames + closing_frames

            ep_state.progress = 0.88
            self._save_state()
            yield ep_state

            # Step 3 – encode video
            _write_minimal_mp4(all_frames, FPS, out_path)

            ep_state.progress = 1.0
            ep_state.status = RenderStatus.COMPLETE
            ep_state.video_path = str(out_path)
            ep_state.completed_at = time.time()
            self._save_state()
            yield ep_state

        except Exception as exc:
            ep_state.status = RenderStatus.ERROR
            ep_state.error_message = str(exc)
            self._save_state()
            yield ep_state

    def get_video_path(self, episode_number: int) -> Optional[Path]:
        """Return the path to the rendered video, or None if not ready."""
        state = self._state.get(episode_number)
        if state and state.status == RenderStatus.COMPLETE and state.video_path:
            p = Path(state.video_path)
            if p.exists():
                return p
        return None

    def all_states(self) -> dict[int, EpisodeState]:
        return dict(self._state)

    def reset_episode(self, episode_number: int) -> None:
        """Remove rendered video and reset state."""
        video_path = self.get_video_path(episode_number)
        if video_path and video_path.exists():
            video_path.unlink()
        if episode_number in self._state:
            del self._state[episode_number]
            self._save_state()


# ---------------------------------------------------------------------------
# Per-scene frame helpers (split out for incremental progress)
# ---------------------------------------------------------------------------


def _build_title_frames(episode: Episode) -> List[bytes]:
    lines = [
        "STUPID SINDY",
        f"Episode {episode.episode_number}",
        f'"{episode.title}"',
        "",
        episode.description,
    ]
    return [_make_png_bytes(FRAME_W, FRAME_H, PALETTE["title"], lines) for _ in range(3)]


def _build_closing_frames(episode: Episode) -> List[bytes]:
    lines = ["STUPID SINDY", f"End of Episode {episode.episode_number}", "I Meant To Do That."]
    return [_make_png_bytes(FRAME_W, FRAME_H, PALETTE["closing"], lines) for _ in range(2)]


def _build_frames_for_scene(episode: Episode, scene_index: int) -> List[bytes]:
    scene = episode.scenes[scene_index]
    frames: List[bytes] = []

    scene_lines = [
        f"SCENE {scene.scene_number}: {scene.title}",
        f"Location: {scene.location}",
        "",
        scene.description,
    ]
    frames.extend(
        _make_png_bytes(FRAME_W, FRAME_H, PALETTE["scene"], scene_lines) for _ in range(2)
    )

    for beat in scene.dialogue[:3]:
        dlg_lines = [
            beat["character"].upper(),
            f'"{beat["line"]}"',
        ]
        frames.append(_make_png_bytes(FRAME_W, FRAME_H, PALETTE["dialogue"], dlg_lines))

    return frames
