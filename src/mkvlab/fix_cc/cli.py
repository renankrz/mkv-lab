"""File-level orchestrator: load → process → save."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .interactive import Choice, InteractiveDecider
from .model import Subtitle
from .pipeline import AcceptAllDecider, AutoDecider, run_pipeline
from .srt_io import load_srt, save_srt
from .steps import default_pipeline


class SubtitleSession:
    """Loads an SRT, runs the cleaning pipeline with interactive review,
    and writes the result back (keeping a ``.backup`` of the original).
    """

    def __init__(
        self,
        file_path: str,
        decider: Optional[InteractiveDecider] = None,
    ) -> None:
        self.file_path = file_path
        self.subtitles: List[Subtitle] = []
        self.steps = default_pipeline()
        self.decider = decider or InteractiveDecider()

    def load(self) -> bool:
        try:
            self.subtitles = load_srt(self.file_path)
            return True
        except Exception as exc:
            print(f"Error loading file: {exc}")
            return False

    def process_interactively(self) -> bool:
        print(f"\nAnalyzing {len(self.subtitles)} subtitles...")
        print("=" * 60)

        auto_decider = AutoDecider()
        accept_all = AcceptAllDecider()

        # Compute auto and fully-cleaned variants once per subtitle.
        processed: List[Tuple[int, Subtitle, Subtitle, Subtitle]] = []
        for idx, sub in enumerate(self.subtitles):
            auto = run_pipeline(sub, self.steps, auto_decider)
            fully = run_pipeline(sub, self.steps, accept_all)
            processed.append((idx, sub, auto, fully))

        auto_changes: List[Tuple[Subtitle, Subtitle]] = [
            (sub, auto)
            for _, sub, auto, fully in processed
            if auto.text != sub.text and fully.text == auto.text
        ]
        pending = [
            (idx, sub, auto, fully)
            for idx, sub, auto, fully in processed
            if fully.text != auto.text
        ]

        changes: List[Tuple[Subtitle, Subtitle]] = list(auto_changes)
        to_remove: List[int] = []

        for count, (idx, sub, auto, fully) in enumerate(pending, 1):
            decision = self.decider.decide(sub, auto, fully, (count, len(pending)))
            if decision.choice is Choice.CANCEL:
                print("Operation cancelled by user.")
                return False
            if decision.choice is Choice.ACCEPT_FULL:
                changes.append((sub, fully))
                print("✓ Correction accepted")
            elif decision.choice is Choice.KEEP_AUTO:
                if auto.text != sub.text:
                    changes.append((sub, auto))
                print("✓ Kept original")
            elif decision.choice is Choice.REMOVE:
                to_remove.append(idx)
                print("✓ Subtitle marked for removal")
            elif decision.choice is Choice.EDIT and decision.edited_text is not None:
                changes.append((sub, sub.with_text(decision.edited_text)))
                print("✓ Manual edit saved")

        if auto_changes:
            print(f"\n{'=' * 60}")
            print(f"AUTO-APPLIED CHANGES ({len(auto_changes)})")
            print(f"{'=' * 60}")
            for original, auto in auto_changes:
                print(f"\n-------------- Subtitle #{original.number} --------------")
                print(original.text)
                print("-----------------------------------------")
                print(auto.text)
                print("-----------------------------------------")

        if changes or to_remove:
            self._apply_changes(changes, to_remove)
            return True
        print("\nNo changes were made.")
        return False

    def _apply_changes(
        self,
        changes: List[Tuple[Subtitle, Subtitle]],
        to_remove: List[int],
    ) -> None:
        backup_path = self.file_path + ".backup"
        Path(self.file_path).rename(backup_path)
        try:
            by_number = {s.number: s for s in self.subtitles}
            for old, new in changes:
                by_number[old.number] = new
            for idx in sorted(to_remove, reverse=True):
                if idx < len(self.subtitles):
                    by_number.pop(self.subtitles[idx].number, None)
            final = sorted(by_number.values(), key=lambda s: s.number)
            save_srt(self.file_path, final)
            print("\n✓ Changes applied successfully!")
            print(f"✓ Backup saved as: {backup_path}")
            print(f"✓ Subtitles removed: {len(to_remove)}")
            print(f"✓ Subtitles modified: {len(changes)}")
        except Exception as exc:
            print(f"Error applying changes: {exc}")
            if Path(backup_path).exists():
                Path(backup_path).rename(self.file_path)
                print("✓ Backup restored due to error")


def main() -> None:
    script_name = Path(sys.argv[0]).name
    if len(sys.argv) != 2:
        print(f"Usage: {script_name} <srt_file>")
        print(f"Example: {script_name} subtitles.srt")
        sys.exit(1)

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    session = SubtitleSession(file_path)
    if not session.load():
        print("Failed to load file.")
        sys.exit(1)

    print("=" * 60)
    print("INTERACTIVE CC/SDH SUBTITLE CLEANING")
    print("=" * 60)

    if session.process_interactively():
        print("\n✓ Processing completed!")
    else:
        print("\n✗ Processing cancelled or no changes.")


if __name__ == "__main__":
    main()
