#!/usr/bin/env python3
import datetime
import os

# MemPalace Constants
PALACE_ROOT = os.path.expanduser("~/B-Agent/MemPalace")
HALLS = ["facts", "events", "discoveries", "preferences", "advice"]


def initialize_palace():
    for hall in HALLS:
        os.makedirs(f"{PALACE_ROOT}/hall_{hall}", exist_ok=True)
    print("MemPalace Structure Initialized.")


def store_memory(wing, room, hall, content):
    """
    wing: Project name (e.g., 'XRP_Accumulation')
    room: Sub-topic (e.g., 'syndrome_extraction')
    hall: One of the 5 Halls
    """
    path = f"{PALACE_ROOT}/hall_{hall}/{wing}_{room}.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a") as f:
        f.write(f"\n--- ENTRY: {timestamp} ---\n{content}\n")
    print(f"Memory anchored in {hall}: {wing}_{room}")


if __name__ == "__main__":
    initialize_palace()
    # Usage: python mem_palace.py [Wing] [Room] [Hall] [Content]
