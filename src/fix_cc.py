#!/usr/bin/env python3
"""
Interactively cleans CC/SDH elements from SRT subtitles.
"""

import copy
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Set


class RegexPatterns:
    """Reusable regex patterns for the entire application."""

    # Patterns for content
    PARENTHESES = re.compile(r'\([^)]*\)')
    BRACKETS = re.compile(r'\[[^\]]*\]')
    CURLY_BRACKETS = re.compile(r'\{[^}]*\}')
    HASH = re.compile(r'#[^#]*#')
    SPEAKER = re.compile(r'^\s*([^:\n]+?)\s*:', re.IGNORECASE)

    # Patterns for cleaning
    LEADING_DASHES = re.compile(r'^[\-\–\—]')
    MULTIPLE_SPACES = re.compile(r'\s+')
    SPACES_BEFORE_PUNCTUATION = re.compile(r'\s+([.,!?;:])')


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
            self.lines = self.text.split('\n')
        if not self.original_text:
            self.original_text = self.text
        # Analyze the structure of the subtitle
        self._analyze_structure()

    def _analyze_structure(self):
        """Analyzes the structure of the subtitle for decision making."""
        self.structure.line_count = len(self.lines)

        for line in self.lines:
            line_stripped = line.strip()

            # Checks for speaker identification
            speaker_match = RegexPatterns.SPEAKER.match(line_stripped)
            if speaker_match:
                raw_speaker = speaker_match.group(1).strip()
                # Cleans the speaker name by removing CC/SDH elements
                speaker_name = TextCleaner._clean_speaker_name(raw_speaker)
                if speaker_name:  # Only adds if something remains after cleaning
                    self.structure.speakers.add(speaker_name)

            # Checks other structural patterns using reusable patterns
            if RegexPatterns.PARENTHESES.search(line_stripped):
                self.structure.has_parentheses = True
            if RegexPatterns.BRACKETS.search(line_stripped):
                self.structure.has_brackets = True
            if RegexPatterns.CURLY_BRACKETS.search(line_stripped):
                self.structure.has_curly_brackets = True
            if RegexPatterns.HASH.search(line_stripped):
                self.structure.has_hash_content = True
            if '♪' in line_stripped:
                self.structure.has_music = True
            if RegexPatterns.LEADING_DASHES.match(line_stripped):
                self.structure.has_dashes = True


class TextCleaner:
    """Text cleaning pipeline with sequential steps."""

    @staticmethod
    def clean_subtitle(subtitle: Subtitle) -> Subtitle:
        """Executes all cleaning steps on a complete subtitle."""
        # Creates a copy to avoid modifying the original
        cleaned_subtitle = copy.deepcopy(subtitle)

        # Applies basic cleaning steps
        cleaned_lines = []
        for line in subtitle.lines:
            cleaned_line = TextCleaner._clean_line(line)
            if cleaned_line.strip():  # Keeps only non-empty lines
                cleaned_lines.append(cleaned_line)

        # Joins the cleaned lines
        cleaned_text = '\n'.join(cleaned_lines)

        # Applies structural formatting based on analysis
        cleaned_text = TextCleaner._format_structure(subtitle, cleaned_text)

        # Final cleanup
        cleaned_text = TextCleaner._final_cleanup(cleaned_text)

        cleaned_subtitle.text = cleaned_text
        cleaned_subtitle.lines = cleaned_text.split('\n')

        return cleaned_subtitle

    @staticmethod
    def _clean_line(line: str) -> str:
        """Cleans a single line of text."""
        cleaned = line

        # Removes different types of special content using reusable patterns
        cleaners = [
            TextCleaner._remove_parentheses_content,
            TextCleaner._remove_bracket_content,
            TextCleaner._remove_curly_bracket_content,
            TextCleaner._remove_hash_symbol_content,
            TextCleaner._remove_music_indication,
            TextCleaner._remove_speaker_identification
        ]

        for cleaner in cleaners:
            cleaned = cleaner(cleaned)

        return cleaned.strip()

    @staticmethod
    def _remove_parentheses_content(text: str) -> str:
        """Removes content between parentheses."""
        return RegexPatterns.PARENTHESES.sub('', text)

    @staticmethod
    def _remove_bracket_content(text: str) -> str:
        """Removes content between brackets."""
        return RegexPatterns.BRACKETS.sub('', text)

    @staticmethod
    def _remove_curly_bracket_content(text: str) -> str:
        """Removes content between curly brackets."""
        return RegexPatterns.CURLY_BRACKETS.sub('', text)

    @staticmethod
    def _remove_hash_symbol_content(text: str) -> str:
        """Removes content between hash symbols."""
        return RegexPatterns.HASH.sub('', text)

    @staticmethod
    def _remove_music_indication(text: str) -> str:
        """Removes musical indication symbols."""
        return text.replace('♪', '')

    @staticmethod
    def _remove_speaker_identification(text: str) -> str:
        """Removes speaker identification."""
        # Removes only at the beginning of the line to avoid removing dialogues
        return RegexPatterns.SPEAKER.sub('', text)

    @staticmethod
    def _format_structure(subtitle: Subtitle, cleaned_text: str) -> str:
        """Formats the text structure based on the analysis of the original subtitle."""
        if not cleaned_text.strip():
            return cleaned_text

        cleaned_lines = cleaned_text.split('\n')

        # DECISION: When to format with dashes?
        should_format = (
            subtitle.structure.speaker_count > 1 or    # Multiple speakers
            subtitle.structure.has_dashes or           # Already had dashes
            # Has dashes after cleaning
            any(RegexPatterns.LEADING_DASHES.match(line.strip())
                for line in cleaned_lines if line.strip())
        )

        if not should_format:
            return cleaned_text

        # Applies consistent formatting with dashes
        formatted_lines = []
        for line in cleaned_lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue

            # Removes any residual dash for consistent reformatting
            cleaned = RegexPatterns.LEADING_DASHES.sub('', stripped)

            if cleaned:
                formatted_lines.append(f'-{cleaned}')
            else:
                formatted_lines.append(stripped)

        return '\n'.join(formatted_lines)

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
            TextCleaner._remove_music_indication
        ]

        for cleaner in cleaners:
            cleaned = cleaner(cleaned)

        return cleaned.strip()

    @staticmethod
    def _final_cleanup(text: str) -> str:
        """Final cleanup of the text."""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = RegexPatterns.MULTIPLE_SPACES.sub(' ', line)
            line = line.strip()
            line = re.sub(r'([\-\–\—])\s+', r'\1', line)
            line = RegexPatterns.SPACES_BEFORE_PUNCTUATION.sub(r'\1', line)
            if line:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)


class SubtitleCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.subtitles: List[Subtitle] = []
        self.original_content: List[str] = []
        self.text_cleaner = TextCleaner()

    def load_subtitles(self) -> bool:
        """Loads the content of the SRT file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.original_content = file.readlines()
            return True
        except UnicodeDecodeError:
            try:
                with open(self.file_path, 'r', encoding='latin-1') as file:
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
            line = self.original_content[i].rstrip('\n\r')

            if not line.strip():
                if current_number > 0 and current_text_lines:
                    text = '\n'.join(current_text_lines)
                    subtitle = Subtitle(
                        number=current_number,
                        start_time=current_start,
                        end_time=current_end,
                        text=text,
                        lines=current_text_lines.copy()
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

            if '-->' in line and current_number > 0:
                times = line.split('-->')
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
            text = '\n'.join(current_text_lines)
            subtitle = Subtitle(
                number=current_number,
                start_time=current_start,
                end_time=current_end,
                text=text,
                lines=current_text_lines.copy()
            )
            self.subtitles.append(subtitle)

    def process_interactively(self):
        """Interactively process subtitles with the user."""
        changes_made = []
        subtitles_to_remove = []

        print(f"\nAnalyzing {len(self.subtitles)} subtitles...")
        print("=" * 60)

        for i, subtitle in enumerate(self.subtitles):
            cleaned_subtitle = self.text_cleaner.clean_subtitle(subtitle)

            # Skip if there were no changes

            if cleaned_subtitle.text == subtitle.text:
                continue

            print(f"\n-------------- Subtitle #{subtitle.number} --------------")
            print(subtitle.text)

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

            if choice == '0':
                print("Operation cancelled by user.")
                return False
            elif choice == '1':
                if will_remove:
                    subtitles_to_remove.append(i)
                    print("✓ Removal accepted")
                else:
                    changes_made.append((subtitle, cleaned_subtitle))
                    print("✓ Correction accepted")
            elif choice == '2':
                print("✓ Kept original")
            elif choice == '3':
                subtitles_to_remove.append(i)
                print("✓ Subtitle marked for removal")
            elif choice == '4':
                new_text = input("Enter new text: ").strip()
                if new_text:
                    new_subtitle = copy.deepcopy(subtitle)
                    new_subtitle.text = new_text
                    new_subtitle.lines = new_text.split('\n')
                    changes_made.append((subtitle, new_subtitle))
                    print("✓ Manual edit saved")
                else:
                    print("✗ Empty text, keeping original")
            else:
                print("✓ Kept original (invalid option)")

        if changes_made or subtitles_to_remove:
            self.apply_changes(changes_made, subtitles_to_remove)
            return True
        else:
            print("\nNo changes were made.")
            return False

    def apply_changes(self, changes: List[Tuple[Subtitle, Subtitle]], to_remove: List[int]):
        """Apply changes by creating a new SRT file."""
        backup_path = self.file_path + '.backup'
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

            with open(self.file_path, 'w', encoding='utf-8') as outfile:
                for subtitle in final_subtitles:
                    outfile.write(f"{subtitle.number}\n")
                    outfile.write(
                        f"{subtitle.start_time} --> {subtitle.end_time}\n")
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
    if len(sys.argv) != 2:
        print("Usage: python clean_subtitles.py <srt_file>")
        print("Example: python clean_subtitles.py subtitles.srt")
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
