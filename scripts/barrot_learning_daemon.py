"""Long-running verified progressive learning daemon for Barrot.

External inference and local repository mutation require separate interactive
operator approvals. Remote publication is disabled by the primary mission.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from datetime import datetime, timezone

from barrot_agent.barrot_brain import BarrotBrain
from barrot_agent.orchestration import BarrotActionLoop
from barrot_agent.orchestration.repository_repair_loop import assert_clean_feature_worktree


RUNNING = True


def stop_handler(signum, frame):
    global RUNNING
    print("\\nBARROT_LEARNING_DAEMON_STOP_REQUESTED")
    RUNNING = False


signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)


def _confirm(prompt: str, expected: str) -> None:
    answer = input(prompt).strip()
    if answer != expected:
        raise SystemExit("Operator confirmation did not match; daemon was not started.")


def main(argv=None) -> None:
    global RUNNING

    parser = argparse.ArgumentParser(description="Run Barrot's local verified learning daemon")
    parser.add_argument(
        "--allow-external-inference",
        action="store_true",
        help="Authorize repository/learning context to be sent to GitHub Models or Groq.",
    )
    parser.add_argument(
        "--allow-local-mutations",
        action="store_true",
        help="Authorize verified local file changes in a clean non-default feature worktree.",
    )
    args = parser.parse_args(argv)

    if not args.allow_external_inference:
        raise SystemExit("External inference is disabled; pass --allow-external-inference only after reviewing the provider/data-transfer scope.")
    if not args.allow_local_mutations:
        raise SystemExit("Local mutations are disabled; pass --allow-local-mutations only when a clean feature worktree is ready.")
    if not sys.stdin.isatty():
        raise SystemExit("The learning daemon requires an interactive terminal; unattended inference and mutation are disabled.")

    _confirm(
        "Type SEND BARROT LEARNING CONTEXT TO GITHUB MODELS OR GROQ: ",
        "SEND BARROT LEARNING CONTEXT TO GITHUB MODELS OR GROQ",
    )
    _confirm(
        "Type START BARROT LEARNING ON CLEAN FEATURE BRANCH: ",
        "START BARROT LEARNING ON CLEAN FEATURE BRANCH",
    )

    try:
        workspace = assert_clean_feature_worktree(".", default_branch="main")
    except ValueError as exc:
        raise SystemExit(f"Learning daemon blocked: {exc}") from exc

    brain = BarrotBrain(allow_external_inference=True)
    loop = BarrotActionLoop(
        brain=brain,
        workspace=str(workspace),
        max_attempts=2,
    )

    cycle = 0
    sleep_seconds = 60
    RUNNING = True

    print("BARROT_LEARNING_DAEMON_STARTED")
    print("MODE: VERIFIED_PROGRESSIVE_LEARNING")
    print("WORKTREE: clean non-default feature branch verified at startup")
    print("EXTERNAL_INFERENCE: explicitly authorized for this process")
    print("REMOTE_PUBLISH: DISABLED_BY_PRIMARY_MISSION_GUARDRAIL")
    print("STOP: CTRL+C")

    while RUNNING:
        cycle += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        print("\\n" + "=" * 60)
        print("BARROT LEARNING CYCLE:", cycle)
        print("TIME:", timestamp)
        print("MODE: AUTONOMOUS_PROGRESSIVE_GOAL_SELECTION")
        print("=" * 60)

        try:
            result = loop.run_next_learning_goal()
            print(
                "GOAL:",
                getattr(result, "goal", "Selected internally by LearningCurriculum"),
            )
            print("SUCCESS:", result.success)
            print("ATTEMPTS:", result.attempts)

            attempt = result.history[-1] if result.history else {}
            print("OUTCOME:", attempt.get("outcome"))
            print("LEARNING:", attempt.get("learning"))
            if result.success:
                print("LOCAL_LEARNING_RESULT: verified; changes remain in the feature worktree")
                print("REMOTE_PUBLISH: skipped; no git add, commit or push was attempted")

        except Exception as exc:
            print("CYCLE_ERROR:", repr(exc))

        if RUNNING:
            print(f"SLEEPING: {sleep_seconds} seconds")
            time.sleep(sleep_seconds)

    print("BARROT_LEARNING_DAEMON_STOPPED")


if __name__ == "__main__":
    main()
