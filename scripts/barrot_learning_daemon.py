"""Long-running verified progressive learning daemon for Barrot."""

from __future__ import annotations

import signal
import time
from datetime import datetime, timezone

from barrot_agent.barrot_brain import BarrotBrain
from barrot_agent.orchestration import (
    BarrotActionLoop,
    ValidatedPublisher,
)


RUNNING = True


def stop_handler(signum, frame):
    global RUNNING
    print("\nBARROT_LEARNING_DAEMON_STOP_REQUESTED")
    RUNNING = False


signal.signal(
    signal.SIGINT,
    stop_handler,
)
signal.signal(
    signal.SIGTERM,
    stop_handler,
)


def main() -> None:
    global RUNNING

    brain = BarrotBrain()

    loop = BarrotActionLoop(
        brain=brain,
        workspace=".",
        max_attempts=2,
    )

    publisher = ValidatedPublisher(
        workspace=".",
        remotes=(
            "origin",
            "gitlab",
        ),
    )

    cycle = 0
    sleep_seconds = 60

    print("BARROT_LEARNING_DAEMON_STARTED")
    print("MODE: VERIFIED_PROGRESSIVE_LEARNING")
    print("PUBLISH: GITHUB_AND_GITLAB")
    print("STOP: CTRL+C")

    while RUNNING:
        cycle += 1

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        print("\n" + "=" * 60)
        print("BARROT LEARNING CYCLE:", cycle)
        print("TIME:", timestamp)
        print("MODE: AUTONOMOUS_PROGRESSIVE_GOAL_SELECTION")
        print("=" * 60)

        try:
            result = loop.run_next_learning_goal()

            print(
                "GOAL:",
                getattr(
                    result,
                    "goal",
                    "Selected internally by LearningCurriculum",
                ),
            )

            print("SUCCESS:", result.success)
            print("ATTEMPTS:", result.attempts)

            attempt = (
                result.history[-1]
                if result.history
                else {}
            )

            print(
                "OUTCOME:",
                attempt.get("outcome"),
            )

            print(
                "LEARNING:",
                attempt.get("learning"),
            )

            if result.success:
                publish = publisher.publish(
                    message=(
                        "barrot: validated autonomous learning "
                        f"cycle {cycle}"
                    ),
                )

                print(
                    "PUBLISH_SUCCESS:",
                    publish.success,
                )
                print(
                    "COMMITTED:",
                    publish.committed,
                )
                print(
                    "PUSHED:",
                    publish.pushed,
                )
                print(
                    "PUBLISH_REASON:",
                    publish.reason,
                )

        except Exception as exc:
            print(
                "CYCLE_ERROR:",
                repr(exc),
            )

        if RUNNING:
            print(
                f"SLEEPING: "
                f"{sleep_seconds} seconds"
            )

            time.sleep(
                sleep_seconds
            )

    print(
        "BARROT_LEARNING_DAEMON_STOPPED"
    )


if __name__ == "__main__":
    main()
