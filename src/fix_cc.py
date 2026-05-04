#!/usr/bin/env python3
"""
Interactively cleans CC/SDH elements from SRT subtitles.
"""

import copy
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from enum import auto as enum_auto
from pathlib import Path
from typing import List, Optional, Set, Tuple


class PatternMode(Enum):
    """Processing mode for a regex pattern."""

    AUTO = enum_auto()
    INTERACTIVE = enum_auto()


@dataclass
class Pattern:
    """A regex pattern paired with its processing mode."""

    regex: re.Pattern
    mode: PatternMode

    def search(self, string: str) -> Optional[re.Match[str]]:
        return self.regex.search(string)

    def sub(self, repl: str, string: str, count: int = 0) -> str:
        return self.regex.sub(repl, string, count)

    def match(self, string: str) -> Optional[re.Match[str]]:
        return self.regex.match(string)


class Patterns:
    """Padrões nomeados usados pela aplicação, cada um associado ao seu modo de processamento."""

    PARENTHESES = Pattern(re.compile(r"\([^)]*\)"), PatternMode.INTERACTIVE)
    BRACKETS = Pattern(re.compile(r"\[[^\]]*\]"), PatternMode.INTERACTIVE)
    CURLY_BRACKETS = Pattern(re.compile(r"\{[^}]*\}"), PatternMode.INTERACTIVE)
    HASH = Pattern(re.compile(r"#[^#]*#"), PatternMode.INTERACTIVE)
    MUSIC_SIGN = Pattern(re.compile(r"♪"), PatternMode.INTERACTIVE)
    DOUBLE_HYPHENS = Pattern(re.compile(r"--"), PatternMode.INTERACTIVE)
    LENGTHY_ELLIPSIS = Pattern(re.compile(r"\.{4,}"), PatternMode.AUTO)
    SPEAKER = Pattern(
        re.compile(r"^\s*([^:\n]+?)\s*:", re.IGNORECASE), PatternMode.INTERACTIVE
    )
    LEADING_DASHES = Pattern(re.compile(r"^[\-\–\—]"), PatternMode.INTERACTIVE)
    MULTIPLE_SPACES = Pattern(re.compile(r"\s+"), PatternMode.INTERACTIVE)
    SPACES_BEFORE_PUNCTUATION = Pattern(
        re.compile(r"\s+([.,!?;:])"), PatternMode.INTERACTIVE
    )


@dataclass
class SubtitleStructure:
    """Analyzed structure of a subtitle."""

    speakers: Set[str] = field(default_factory=set)
    has_dashes: bool = False
    has_parentheses: bool = False
    has_brackets: bool = False
    has_curly_brackets: bool = False
    has_hash_content: bool = False
    has_music: bool = False
    line_count: int = 0

    @property
    def speaker_count(self) -> int:
        """Returns the number of detected speakers."""
        return len(self.speakers)

    @property
    def has_speakers(self) -> bool:
        """Returns whether speakers were detected."""
        return self.speaker_count > 0


@dataclass
class Subtitle:
    """Complete representation of a subtitle."""

    number: int
    start_time: str
    end_time: str
    text: str
    original_text: str = ""
    lines: List[str] = field(default_factory=list)
    structure: SubtitleStructure = field(default_factory=SubtitleStructure)

    def __post_init__(self):
        if not self.lines:
            self.lines = self.text.split("\n")
        if not self.original_text:
            self.original_text = self.text
        # Analyze the structure of the subtitle
        self._analyze_structure()

    def _analyze_structure(self):
        """Analyzes the structure of the subtitle for decision making."""
        self.structure.line_count = len(self.lines)

        # Checks content patterns on the full text (multiline-aware)
        if Patterns.PARENTHESES.search(self.text):
            self.structure.has_parentheses = True
        if Patterns.BRACKETS.search(self.text):
            self.structure.has_brackets = True
        if Patterns.CURLY_BRACKETS.search(self.text):
            self.structure.has_curly_brackets = True
        if Patterns.HASH.search(self.text):
            self.structure.has_hash_content = True
        if Patterns.MUSIC_SIGN.search(self.text):
            self.structure.has_music = True

        for line in self.lines:
            line_stripped = line.strip()

            # Checks for speaker identification
            speaker_match = Patterns.SPEAKER.match(line_stripped)
            if speaker_match:
                raw_speaker = speaker_match.group(1).strip()
                # Cleans the speaker name by removing CC/SDH elements
                speaker_name = TextCleaner._clean_speaker_name(raw_speaker)
                if speaker_name:  # Only adds if something remains after cleaning
                    self.structure.speakers.add(speaker_name)

            if Patterns.LEADING_DASHES.match(line_stripped):
                self.structure.has_dashes = True


class TextCleaner:
    """Text cleaning pipeline with sequential steps."""

    @staticmethod
    def clean_subtitle(subtitle: Subtitle) -> Subtitle:
        """Executes all cleaning steps on a complete subtitle."""
        return TextCleaner.clean_subtitle_interactive(
            TextCleaner.clean_subtitle_auto(subtitle)
        )

    @staticmethod
    def clean_subtitle_auto(subtitle: Subtitle) -> Subtitle:
        """Applies AUTO-mode cleaning steps without requiring user review."""
        cleaned = copy.deepcopy(subtitle)
        text = TextCleaner._fix_lengthy_ellipsis(subtitle.text)
        text = TextCleaner._final_cleanup(text)
        cleaned.text = text
        cleaned.lines = text.split("\n")
        return cleaned

    @staticmethod
    def clean_subtitle_interactive(subtitle: Subtitle) -> Subtitle:
        """Applies INTERACTIVE-mode cleaning steps that require user review."""
        cleaned = copy.deepcopy(subtitle)

        text = subtitle.text
        text = TextCleaner._remove_parentheses_content(text)
        text = TextCleaner._remove_bracket_content(text)
        text = TextCleaner._remove_curly_bracket_content(text)
        text = TextCleaner._remove_hash_symbol_content(text)
        text = TextCleaner._remove_music_indication(text)
        text = TextCleaner._fix_double_hyphens(text)

        cleaned_lines = []
        for line in text.split("\n"):
            line = TextCleaner._remove_speaker_identification(line).strip()
            if line:
                cleaned_lines.append(line)

        text = TextCleaner._format_structure(subtitle, "\n".join(cleaned_lines))
        text = TextCleaner._final_cleanup(text)

        cleaned.text = text
        cleaned.lines = text.split("\n")
        return cleaned

    @staticmethod
    def _remove_parentheses_content(text: str) -> str:
        """Removes content between parentheses."""
        return Patterns.PARENTHESES.sub("", text)

    @staticmethod
    def _remove_bracket_content(text: str) -> str:
        """Removes content between brackets."""
        return Patterns.BRACKETS.sub("", text)

    @staticmethod
    def _remove_curly_bracket_content(text: str) -> str:
        """Removes content between curly brackets."""
        return Patterns.CURLY_BRACKETS.sub("", text)

    @staticmethod
    def _remove_hash_symbol_content(text: str) -> str:
        """Removes content between hash symbols."""
        return Patterns.HASH.sub("", text)

    @staticmethod
    def _remove_music_indication(text: str) -> str:
        """Removes musical indication symbols."""
        return Patterns.MUSIC_SIGN.sub("", text)

    @staticmethod
    def _fix_double_hyphens(text: str) -> str:
        """Replaces double hyphens with em dash."""
        return Patterns.DOUBLE_HYPHENS.sub("\u2014", text)

    @staticmethod
    def _fix_lengthy_ellipsis(text: str) -> str:
        """Replaces sequences of more than 3 dots with exactly 3 dots."""
        return Patterns.LENGTHY_ELLIPSIS.sub("...", text)

    @staticmethod
    def _remove_speaker_identification(text: str) -> str:
        """Removes speaker identification."""
        # Removes only at the beginning of the line to avoid removing dialogues
        return Patterns.SPEAKER.sub("", text)

    @staticmethod
    def _format_structure(subtitle: Subtitle, cleaned_text: str) -> str:
        """Formats the text structure based on the analysis of the original subtitle."""
        if not cleaned_text.strip():
            return cleaned_text

        cleaned_lines = cleaned_text.split("\n")

        # DECISION: When to format with dashes?
        should_format = (
            subtitle.structure.speaker_count > 1  # Multiple speakers
            or subtitle.structure.has_dashes  # Already had dashes
            or
            # Has dashes after cleaning
            any(
                Patterns.LEADING_DASHES.match(line.strip())
                for line in cleaned_lines
                if line.strip()
            )
        )

        if not should_format:
            return cleaned_text

        # Applies consistent formatting with dashes
        formatted_lines = []
        for line in cleaned_lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # Removes any residual dash for consistent reformatting
            cleaned = Patterns.LEADING_DASHES.sub("", stripped)

            if cleaned:
                formatted_lines.append(f"-{cleaned}")
            else:
                formatted_lines.append(stripped)

        return "\n".join(formatted_lines)

    @staticmethod
    def _clean_speaker_name(raw_name: str) -> str:
        """Cleans the speaker name by removing CC/SDH elements."""
        cleaned = raw_name
        # Removes all types of special content
        cleaners = [
            TextCleaner._remove_parentheses_content,
            TextCleaner._remove_bracket_content,
            TextCleaner._remove_curly_bracket_content,
            TextCleaner._remove_hash_symbol_content,
            TextCleaner._remove_music_indication,
        ]

        for cleaner in cleaners:
            cleaned = cleaner(cleaned)

        return cleaned.strip()

    @staticmethod
    def _final_cleanup(text: str) -> str:
        """Final cleanup of the text."""
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = Patterns.MULTIPLE_SPACES.sub(" ", line)
            line = line.strip()
            line = re.sub(r"([\-\–\—])\s+", r"\1", line)
            line = Patterns.SPACES_BEFORE_PUNCTUATION.sub(r"\1", line)
            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)


class SubtitleCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.subtitles: List[Subtitle] = []
        self.original_content: List[str] = []
        self.text_cleaner = TextCleaner()

    def load_subtitles(self) -> bool:
        """Loads the content of the SRT file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.original_content = file.readlines()
            return True
        except UnicodeDecodeError:
            try:
                with open(self.file_path, "r", encoding="latin-1") as file:
                    self.original_content = file.readlines()
                return True
            except Exception as e:
                print(f"Error reading file: {e}")
                return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def parse_subtitles(self):
        """Parses the content of the SRT file into Subtitle objects."""
        current_number = 0
        current_start = ""
        current_end = ""
        current_text_lines = []

        i = 0
        while i < len(self.original_content):
            line = self.original_content[i].rstrip("\n\r")

            if not line.strip():
                if current_number > 0 and current_text_lines:
                    text = "\n".join(current_text_lines)
                    subtitle = Subtitle(
                        number=current_number,
                        start_time=current_start,
                        end_time=current_end,
                        text=text,
                        lines=current_text_lines.copy(),
                    )
                    self.subtitles.append(subtitle)
                    current_text_lines = []
                    current_number = 0

                i += 1
                continue

            if line.isdigit() and not current_text_lines:
                current_number = int(line)
                i += 1
                continue

            if "-->" in line and current_number > 0:
                times = line.split("-->")
                if len(times) == 2:
                    current_start = times[0].strip()
                    current_end = times[1].strip()
                i += 1
                continue

            if current_number > 0:
                current_text_lines.append(line)
                i += 1
                continue

            i += 1

        if current_number > 0 and current_text_lines:
            text = "\n".join(current_text_lines)
            subtitle = Subtitle(
                number=current_number,
                start_time=current_start,
                end_time=current_end,
                text=text,
                lines=current_text_lines.copy(),
            )
            self.subtitles.append(subtitle)

    @staticmethod
    def _prompt_edit_lines(lines: List[str]) -> str:
        """Prompts the user to edit each line of a subtitle individually."""
        edited_lines = []
        for i, line in enumerate(lines, 1):
            print(f"  Line {i} current: {line}")
            new_line = input(f"  Line {i} new: ").strip()
            if new_line:
                edited_lines.append(new_line)
        return "\n".join(edited_lines)

    def process_interactively(self):
        """Interactively process subtitles with the user."""
        changes_made = []
        subtitles_to_remove = []

        print(f"\nAnalyzing {len(self.subtitles)} subtitles...")
        print("=" * 60)

        all_processed = []
        for i, subtitle in enumerate(self.subtitles):
            auto = self.text_cleaner.clean_subtitle_auto(subtitle)
            fully = self.text_cleaner.clean_subtitle_interactive(auto)
            all_processed.append((i, subtitle, auto, fully))

        auto_changes = [
            (subtitle, auto)
            for _, subtitle, auto, fully in all_processed
            if auto.text != subtitle.text and fully.text == auto.text
        ]

        pending = [
            (i, subtitle, auto, fully)
            for i, subtitle, auto, fully in all_processed
            if fully.text != auto.text
        ]

        changes_made.extend(auto_changes)

        for count, (i, subtitle, auto_sub, cleaned_subtitle) in enumerate(pending, 1):
            print(
                f"\n-------------- Subtitle #{subtitle.number} ({count}/{len(pending)}) --------------"
            )
            print(auto_sub.text)

            # Determine if the correction results in empty text
            will_remove = not cleaned_subtitle.text.strip()

            if will_remove:
                print(f"\n-----------------------------------------")
                print(f"⚠️  REMOVE SUBTITLE")
                print(f"-----------------------------------------")
            else:
                print(f"\n-----------------------------------------")
                print(f"{cleaned_subtitle.text}")
                print(f"-----------------------------------------")

            print("\nOptions:")
            print("1 - Accept correction")
            print("2 - Keep original")
            print("3 - Remove subtitle completely")
            print("4 - Edit manually")
            print("0 - Exit")

            choice = input("\nChoose (1/2/3/4/0): ").strip()

            if choice == "0":
                print("Operation cancelled by user.")
                return False
            elif choice == "1":
                if will_remove:
                    subtitles_to_remove.append(i)
                    print("✓ Removal accepted")
                else:
                    changes_made.append((subtitle, cleaned_subtitle))
                    print("✓ Correction accepted")
            elif choice == "2":
                if auto_sub.text != subtitle.text:
                    changes_made.append((subtitle, auto_sub))
                print("✓ Kept original")
            elif choice == "3":
                subtitles_to_remove.append(i)
                print("✓ Subtitle marked for removal")
            elif choice == "4":
                new_text = self._prompt_edit_lines(auto_sub.lines)
                if new_text:
                    new_subtitle = copy.deepcopy(subtitle)
                    new_subtitle.text = new_text
                    new_subtitle.lines = new_text.split("\n")
                    changes_made.append((subtitle, new_subtitle))
                    print("✓ Manual edit saved")
                else:
                    print("✗ Empty text, keeping original")
            else:
                print("✓ Kept original (invalid option)")

        if auto_changes:
            print(f"\n{'=' * 60}")
            print(f"AUTO-APPLIED CHANGES ({len(auto_changes)})")
            print(f"{'=' * 60}")
            for original, auto in auto_changes:
                print(f"\n-------------- Subtitle #{original.number} --------------")
                print(original.text)
                print(f"\n-----------------------------------------")
                print(auto.text)
                print(f"-----------------------------------------")

        if changes_made or subtitles_to_remove:
            self.apply_changes(changes_made, subtitles_to_remove)
            return True
        else:
            print("\nNo changes were made.")
            return False

    def apply_changes(
        self, changes: List[Tuple[Subtitle, Subtitle]], to_remove: List[int]
    ):
        """Apply changes by creating a new SRT file."""
        backup_path = self.file_path + ".backup"
        Path(self.file_path).rename(backup_path)

        try:
            subtitle_dict = {sub.number: sub for sub in self.subtitles}
            for old_sub, new_sub in changes:
                subtitle_dict[old_sub.number] = new_sub

            for i in sorted(to_remove, reverse=True):
                if i < len(self.subtitles):
                    sub_to_remove = self.subtitles[i]
                    if sub_to_remove.number in subtitle_dict:
                        del subtitle_dict[sub_to_remove.number]

            final_subtitles = list(subtitle_dict.values())
            final_subtitles.sort(key=lambda x: x.number)

            for new_number, subtitle in enumerate(final_subtitles, 1):
                subtitle.number = new_number

            with open(self.file_path, "w", encoding="utf-8") as outfile:
                for subtitle in final_subtitles:
                    outfile.write(f"{subtitle.number}\n")
                    outfile.write(f"{subtitle.start_time} --> {subtitle.end_time}\n")
                    outfile.write(f"{subtitle.text}\n")
                    outfile.write("\n")

            print(f"\n✓ Changes applied successfully!")
            print(f"✓ Backup saved as: {backup_path}")
            print(f"✓ Subtitles removed: {len(to_remove)}")
            print(f"✓ Subtitles modified: {len(changes)}")

        except Exception as e:
            print(f"Error applying changes: {e}")
            if Path(backup_path).exists():
                Path(backup_path).rename(self.file_path)
                print("✓ Backup restored due to error")


def main():
    script_name = Path(sys.argv[0]).name
    if len(sys.argv) != 2:
        print(f"Usage: {script_name} <srt_file>")
        print(f"Example: {script_name} subtitles.srt")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    cleaner = SubtitleCleaner(file_path)

    if not cleaner.load_subtitles():
        print("Failed to load file.")
        sys.exit(1)

    cleaner.parse_subtitles()

    print("=" * 60)
    print("INTERACTIVE CC/SDH SUBTITLE CLEANING")
    print("=" * 60)

    if cleaner.process_interactively():
        print("\n✓ Processing completed!")
    else:
        print("\n✗ Processing cancelled or no changes.")


if __name__ == "__main__":
    main()
