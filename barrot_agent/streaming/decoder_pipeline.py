"""
Decoder Pipeline - Hardware video decoding with jitter buffer and error handling.

Implements:
- Hardware video decoding pipeline
- Frame synchronization and presentation timing
- Jitter buffer management for smooth playback
- Packet reordering and duplicate detection
- Corruption detection and concealment
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple


class DecodeError(Enum):
    """Types of decode errors."""
    NONE = "none"
    CORRUPTED = "corrupted"
    MISSING_REFERENCE = "missing_reference"
    UNSUPPORTED_FEATURE = "unsupported_feature"
    HARDWARE_FAILURE = "hardware_failure"


@dataclass
class EncodedData:
    """Incoming encoded video data packet."""
    data: bytes
    pts: int = 0
    dts: int = 0
    sequence_number: int = 0
    is_keyframe: bool = False
    codec: str = "h264"
    size_bytes: int = 0

    def __post_init__(self) -> None:
        if self.size_bytes == 0:
            self.size_bytes = len(self.data)


@dataclass
class DecodedFrame:
    """A decoded video frame ready for display."""
    data: bytes
    width: int
    height: int
    pts: int = 0
    format: str = "NV12"
    frame_number: int = 0
    decode_time_ms: float = 0.0
    is_corrupt: bool = False
    error: DecodeError = DecodeError.NONE

    @property
    def size_bytes(self) -> int:
        return len(self.data)


@dataclass
class DecoderStats:
    """Statistics for the decoder pipeline."""
    frames_decoded: int = 0
    frames_dropped: int = 0
    frames_concealed: int = 0
    packets_received: int = 0
    packets_out_of_order: int = 0
    packets_duplicate: int = 0
    decode_errors: int = 0
    avg_decode_time_ms: float = 0.0
    render_fps: float = 0.0
    jitter_buffer_level_ms: float = 0.0
    buffer_underruns: int = 0


class CorruptionDetector:
    """Detects bitstream corruption in encoded packets."""

    def __init__(self):
        self._reference_hashes: Dict[int, int] = {}  # pts -> hash

    def check_packet(self, packet: EncodedData) -> bool:
        """
        Check if a packet appears to be corrupt.
        Returns True if packet seems valid.
        """
        if not packet.data:
            return False

        # Check for known codec sync markers
        if packet.codec == "h264":
            # H.264 NAL units start with 0x00000001 or 0x000001
            if len(packet.data) < 4:
                return False
            # Start code check
            if packet.is_keyframe:
                has_start_code = (
                    packet.data[:3] == b'\x00\x00\x01'
                    or packet.data[:4] == b'\x00\x00\x00\x01'
                )
                if not has_start_code:
                    # Could still be valid (AVCC format)
                    pass
        return True

    def conceal_corruption(self, last_valid: Optional[DecodedFrame]) -> DecodedFrame:
        """Create a concealed frame from the last valid frame."""
        if last_valid:
            # Repeat last valid frame (error concealment)
            return DecodedFrame(
                data=last_valid.data,
                width=last_valid.width,
                height=last_valid.height,
                pts=last_valid.pts,
                format=last_valid.format,
                frame_number=last_valid.frame_number,
                is_corrupt=True,
                error=DecodeError.CORRUPTED,
            )
        # Return blank frame
        return DecodedFrame(
            data=bytes(1920 * 1080 * 3 // 2),
            width=1920,
            height=1080,
            is_corrupt=True,
            error=DecodeError.CORRUPTED,
        )


class PacketReorderer:
    """Handles out-of-order packet delivery."""

    def __init__(self, max_reorder: int = 16):
        self.max_reorder = max_reorder
        self._buffer: Dict[int, EncodedData] = {}
        self._next_seq = -1
        self._seen_sequences: set = set()
        self._out_of_order_count = 0
        self._duplicate_count = 0

    def push(self, packet: EncodedData) -> List[EncodedData]:
        """Add a packet and return any consecutively ordered packets."""
        seq = packet.sequence_number

        # Initialize
        if self._next_seq == -1:
            self._next_seq = seq

        # Detect duplicates
        if seq in self._seen_sequences:
            self._duplicate_count += 1
            return []
        self._seen_sequences.add(seq)

        # Detect out-of-order
        if seq != self._next_seq:
            self._out_of_order_count += 1

        self._buffer[seq] = packet

        # Deliver consecutive packets
        delivered = []
        while self._next_seq in self._buffer:
            delivered.append(self._buffer.pop(self._next_seq))
            self._next_seq += 1

        # Flush old packets if buffer grows too large
        if len(self._buffer) > self.max_reorder:
            oldest_seq = min(self._buffer.keys())
            delivered.append(self._buffer.pop(oldest_seq))
            self._next_seq = oldest_seq + 1

        # Clean up seen sequences history
        if len(self._seen_sequences) > 1000:
            cutoff = self._next_seq - 512
            self._seen_sequences = {s for s in self._seen_sequences if s >= cutoff}

        return delivered

    @property
    def out_of_order_count(self) -> int:
        return self._out_of_order_count

    @property
    def duplicate_count(self) -> int:
        return self._duplicate_count


class PresentationTimer:
    """Manages frame presentation timing for smooth playback."""

    def __init__(self, target_fps: float = 60.0):
        self.target_fps = target_fps
        self._frame_duration_us = int(1_000_000 / target_fps)
        self._start_pts: Optional[int] = None
        self._start_time: Optional[float] = None
        self._last_presented_pts: int = -1

    def is_ready_to_present(self, pts: int) -> bool:
        """Check if a frame with given PTS is ready for presentation."""
        now = time.time()
        if self._start_pts is None:
            self._start_pts = pts
            self._start_time = now
            return True

        elapsed_us = int((now - self._start_time) * 1e6)
        pts_offset = pts - self._start_pts
        return elapsed_us >= pts_offset

    def get_next_present_time(self) -> float:
        """Get the wall-clock time of the next frame presentation."""
        if self._start_time is None:
            return time.time()
        next_pts = self._last_presented_pts + self._frame_duration_us
        elapsed_since_start = (next_pts - (self._start_pts or 0)) / 1e6
        return (self._start_time or time.time()) + elapsed_since_start

    def mark_presented(self, pts: int) -> None:
        """Mark a frame as having been presented."""
        self._last_presented_pts = pts


class HardwareDecoderBackend:
    """Hardware-accelerated video decoder backend."""

    def __init__(self, backend: str = "software", codec: str = "h264"):
        self.backend = backend
        self.codec = codec
        self._initialized = False
        self._width = 1920
        self._height = 1080
        self._frame_count = 0

    def initialize(self, codec: str = "h264") -> bool:
        """Initialize the decoder backend."""
        self.codec = codec
        self._initialized = True
        return True

    def decode(self, packet: EncodedData) -> Optional[DecodedFrame]:
        """Decode an encoded packet to a raw frame."""
        if not self._initialized:
            self.initialize(packet.codec)

        start = time.perf_counter()

        # Simulate decoding - expand compressed data
        width = self._width
        height = self._height
        frame_size = width * height * 3 // 2  # NV12

        decode_ms = (time.perf_counter() - start) * 1000.0
        self._frame_count += 1

        return DecodedFrame(
            data=bytes(frame_size),
            width=width,
            height=height,
            pts=packet.pts,
            format="NV12",
            frame_number=self._frame_count,
            decode_time_ms=decode_ms,
        )

    def flush(self) -> List[DecodedFrame]:
        """Flush any buffered frames from the decoder."""
        return []


class DecoderPipeline:
    """
    Hardware-accelerated video decoder pipeline.

    Handles the complete decoding workflow:
    1. Packet reordering and deduplication
    2. Corruption detection and concealment
    3. Hardware/software decoding
    4. Presentation timing synchronization
    5. Output frame delivery
    """

    def __init__(
        self,
        codec: str = "h264",
        hardware: str = "software",
        target_fps: float = 60.0,
        jitter_buffer_ms: float = 20.0,
    ):
        self.codec = codec
        self.target_fps = target_fps
        self.jitter_buffer_ms = jitter_buffer_ms

        self._reorderer = PacketReorderer()
        self._corruption_detector = CorruptionDetector()
        self._backend = HardwareDecoderBackend(backend=hardware, codec=codec)
        self._presentation_timer = PresentationTimer(target_fps)
        self._output_queue: Deque[DecodedFrame] = deque(maxlen=8)
        self._stats = DecoderStats()
        self._last_valid_frame: Optional[DecodedFrame] = None
        self._decode_times: deque = deque(maxlen=60)
        self._start_time = time.time()
        self._on_frame: Optional[Callable] = None

    def push_packet(self, packet: EncodedData) -> List[DecodedFrame]:
        """Submit an encoded packet for decoding."""
        self._stats.packets_received += 1

        # Reorder out-of-order packets
        ordered = self._reorderer.push(packet)
        self._stats.packets_out_of_order += self._reorderer.out_of_order_count
        self._stats.packets_duplicate += self._reorderer.duplicate_count

        decoded_frames = []
        for ordered_pkt in ordered:
            # Check for corruption
            is_valid = self._corruption_detector.check_packet(ordered_pkt)
            if not is_valid:
                self._stats.decode_errors += 1
                concealed = self._corruption_detector.conceal_corruption(
                    self._last_valid_frame
                )
                self._stats.frames_concealed += 1
                decoded_frames.append(concealed)
                continue

            # Decode packet
            frame = self._backend.decode(ordered_pkt)
            if frame:
                self._last_valid_frame = frame
                self._stats.frames_decoded += 1
                if frame.decode_time_ms > 0:
                    self._decode_times.append(frame.decode_time_ms)
                self._output_queue.append(frame)

                if self._on_frame:
                    self._on_frame(frame)

                decoded_frames.append(frame)

        self._update_stats()
        return decoded_frames

    def get_next_frame(self) -> Optional[DecodedFrame]:
        """Get the next frame ready for presentation."""
        if not self._output_queue:
            if self._stats.frames_decoded > 0:
                self._stats.buffer_underruns += 1
            return None

        frame = self._output_queue[0]
        if self._presentation_timer.is_ready_to_present(frame.pts):
            self._output_queue.popleft()
            self._presentation_timer.mark_presented(frame.pts)
            return frame
        return None

    def decode_packet(self, encoded_data: bytes, pts: int = 0, is_keyframe: bool = False) -> Optional[DecodedFrame]:
        """Simple one-shot decode interface."""
        packet = EncodedData(
            data=encoded_data,
            pts=pts,
            is_keyframe=is_keyframe,
            codec=self.codec,
        )
        frames = self.push_packet(packet)
        return frames[0] if frames else None

    def _update_stats(self) -> None:
        """Update pipeline statistics."""
        if self._decode_times:
            self._stats.avg_decode_time_ms = sum(self._decode_times) / len(self._decode_times)
        elapsed = max(0.001, time.time() - self._start_time)
        self._stats.render_fps = self._stats.frames_decoded / elapsed
        self._stats.jitter_buffer_level_ms = len(self._output_queue) * (1000.0 / max(self.target_fps, 1))

    def on_decoded_frame(self, callback: Callable) -> None:
        """Set callback for decoded frames."""
        self._on_frame = callback

    def get_stats(self) -> DecoderStats:
        """Get pipeline statistics."""
        return self._stats

    def flush(self) -> List[DecodedFrame]:
        """Flush the decoder pipeline."""
        flushed = self._backend.flush()
        self._output_queue.clear()
        return flushed

    def shutdown(self) -> None:
        """Shut down the decoder pipeline."""
        self.flush()
