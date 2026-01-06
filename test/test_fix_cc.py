from fix_cc import Subtitle, TextCleaner


class TestSubtitleCleaner:

    # --------------------------------------------------
    # Syntax cleaning function tests (basic unit tests)
    # --------------------------------------------------

    def test_remove_parentheses_content(self):
        assert TextCleaner._remove_parentheses_content(
            "(Hello) World") == " World"
        assert TextCleaner._remove_parentheses_content(
            "( Hello ) World") == " World"
        assert TextCleaner._remove_parentheses_content(
            "Hello (whispering) world") == "Hello  world"
        assert TextCleaner._remove_parentheses_content(
            "Hello ( whispering ) world") == "Hello  world"
        assert TextCleaner._remove_parentheses_content(
            "Hello (World)") == "Hello "
        assert TextCleaner._remove_parentheses_content(
            "Hello ( World )") == "Hello "
        assert TextCleaner._remove_parentheses_content("( )") == ""
        assert TextCleaner._remove_parentheses_content("()") == ""

    def test_remove_bracket_content(self):
        assert TextCleaner._remove_bracket_content("[Hello] World") == " World"
        assert TextCleaner._remove_bracket_content(
            "[ Hello ] World") == " World"
        assert TextCleaner._remove_bracket_content(
            "Hello [whispering] world") == "Hello  world"
        assert TextCleaner._remove_bracket_content(
            "Hello [ whispering ] world") == "Hello  world"
        assert TextCleaner._remove_bracket_content("Hello [World]") == "Hello "
        assert TextCleaner._remove_bracket_content(
            "Hello [ World ]") == "Hello "
        assert TextCleaner._remove_bracket_content("[ ]") == ""
        assert TextCleaner._remove_bracket_content("[]") == ""

    def test_remove_curly_bracket_content(self):
        assert TextCleaner._remove_curly_bracket_content(
            "{Hello} World") == " World"
        assert TextCleaner._remove_curly_bracket_content(
            "{ Hello } World") == " World"
        assert TextCleaner._remove_curly_bracket_content(
            "Hello {whispering} world") == "Hello  world"
        assert TextCleaner._remove_curly_bracket_content(
            "Hello { whispering } world") == "Hello  world"
        assert TextCleaner._remove_curly_bracket_content(
            "Hello {World}") == "Hello "
        assert TextCleaner._remove_curly_bracket_content(
            "Hello { World }") == "Hello "
        assert TextCleaner._remove_curly_bracket_content("{ }") == ""
        assert TextCleaner._remove_curly_bracket_content("{}") == ""

    def test_remove_hash_symbol_content(self):
        assert TextCleaner._remove_hash_symbol_content(
            "#Hello# World") == " World"
        assert TextCleaner._remove_hash_symbol_content(
            "# Hello # World") == " World"
        assert TextCleaner._remove_hash_symbol_content(
            "Hello #whispering# world") == "Hello  world"
        assert TextCleaner._remove_hash_symbol_content(
            "Hello # whispering # world") == "Hello  world"
        assert TextCleaner._remove_hash_symbol_content(
            "Hello #World#") == "Hello "
        assert TextCleaner._remove_hash_symbol_content(
            "Hello # World #") == "Hello "
        assert TextCleaner._remove_hash_symbol_content("# #") == ""
        assert TextCleaner._remove_hash_symbol_content("##") == ""

    def test_remove_music_indication(self):
        assert TextCleaner._remove_music_indication(
            "♪ Hello ♪ world") == " Hello  world"
        assert TextCleaner._remove_music_indication(
            "♪Hello♪ world") == "Hello world"
        assert TextCleaner._remove_music_indication(
            "Hello ♪ singing ♪ world") == "Hello  singing  world"
        assert TextCleaner._remove_music_indication(
            "Hello ♪singing♪ world") == "Hello singing world"
        assert TextCleaner._remove_music_indication(
            "Hello ♪ world ♪") == "Hello  world "
        assert TextCleaner._remove_music_indication(
            "Hello ♪world♪") == "Hello world"
        assert TextCleaner._remove_music_indication("♪ ♪") == " "
        assert TextCleaner._remove_music_indication("♪♪") == ""
        assert TextCleaner._remove_music_indication("♪") == ""

    def test_remove_speaker_identification(self):
        assert TextCleaner._remove_speaker_identification(
            "PERSON: How are you?") == " How are you?"
        assert TextCleaner._remove_speaker_identification(
            "MRS. WOLOWITZ: How are you?") == " How are you?"
        assert TextCleaner._remove_speaker_identification(
            "O'BRIEN: How are you?") == " How are you?"
        assert TextCleaner._remove_speaker_identification(
            "MARY-ANN: How are you?") == " How are you?"
        assert TextCleaner._remove_speaker_identification(
            "Person: How are you?") == " How are you?"
        assert TextCleaner._remove_speaker_identification(
            "person: how are you?") == " how are you?"
        assert TextCleaner._remove_speaker_identification(
            " person : how are you?") == " how are you?"

    # -----------------------------------
    # Final cleanup and formatting tests
    # -----------------------------------

    def test_final_cleanup_multiple_spaces(self):
        assert TextCleaner._final_cleanup("Hello     world") == "Hello world"
        assert TextCleaner._final_cleanup(
            "Hello   there   world") == "Hello there world"
        assert TextCleaner._final_cleanup(
            "  Leading  and  trailing  ") == "Leading and trailing"

    def test_final_cleanup_spaces_before_punctuation(self):
        assert TextCleaner._final_cleanup("Hello , world !") == "Hello, world!"
        assert TextCleaner._final_cleanup(
            "Hello . Goodbye !") == "Hello. Goodbye!"
        assert TextCleaner._final_cleanup(
            "Question ? Answer : Yes") == "Question? Answer: Yes"
        assert TextCleaner._final_cleanup(
            "Hello , world ! How are you ?") == "Hello, world! How are you?"

    def test_final_cleanup_multiline_whitespace(self):
        assert TextCleaner._final_cleanup(
            "  Line 1  \n  Line 2  ") == "Line 1\nLine 2"
        assert TextCleaner._final_cleanup(
            "   \n  Line 1  \n   \n  Line 2  \n   ") == "Line 1\nLine 2"
        assert TextCleaner._final_cleanup(
            "Line 1   \n   \n   Line 2") == "Line 1\nLine 2"

    def test_final_cleanup_dash_formatting(self):
        assert TextCleaner._final_cleanup(
            " -Line 1 \n - Line 2 ") == "-Line 1\n-Line 2"
        assert TextCleaner._final_cleanup(
            "- Line 1 \n-  Line 2") == "-Line 1\n-Line 2"
        assert TextCleaner._final_cleanup(" - ") == "-"
        assert TextCleaner._final_cleanup(
            "–Line 1 \n – Line 2 ") == "–Line 1\n–Line 2"
        assert TextCleaner._final_cleanup(
            "—Line 1 \n — Line 2 ") == "—Line 1\n—Line 2"

    def test_final_cleanup_empty_lines(self):
        assert TextCleaner._final_cleanup(
            "Line 1\n\nLine 2") == "Line 1\nLine 2"
        assert TextCleaner._final_cleanup(
            "\nLine 1\n\nLine 2\n") == "Line 1\nLine 2"
        assert TextCleaner._final_cleanup("\n\n\n") == ""

    def test_final_cleanup_preserves_valid_content(self):
        assert TextCleaner._final_cleanup("Hello world.") == "Hello world."
        assert TextCleaner._final_cleanup("Line 1\nLine 2") == "Line 1\nLine 2"
        assert TextCleaner._final_cleanup("-Dialog line") == "-Dialog line"

    # --------------------------
    # Structural analysis tests
    # --------------------------

    def test_structure_detects_speakers(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON: I have a theory!\nLEONARD: Not again...",
            lines=["SHELDON: I have a theory!", "LEONARD: Not again..."]
        )
        assert subtitle.structure.has_speakers
        assert subtitle.structure.speaker_count == 2
        assert "SHELDON" in subtitle.structure.speakers
        assert "LEONARD" in subtitle.structure.speakers

    def test_structure_detects_parentheses_before_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON (excitedly): I have a theory!",
            lines=["SHELDON (excitedly): I have a theory!"]
        )
        assert subtitle.structure.has_parentheses

    def test_structure_detects_parentheses_after_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON: I have (excitedly) a theory!",
            lines=["SHELDON: I have (excitedly) a theory!"]
        )
        assert subtitle.structure.has_parentheses

    def test_structure_detects_brackets_before_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="LEONARD [sighing]: Not again...",
            lines=["LEONARD [sighing]: Not again..."]
        )
        assert subtitle.structure.has_brackets

    def test_structure_detects_brackets_after_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="LEONARD: [Sighs] Not again...",
            lines=["LEONARD: [Sighs] Not again..."]
        )
        assert subtitle.structure.has_brackets

    def test_structure_detects_curly_brackets_before_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON {excitedly}: I have a theory!",
            lines=["SHELDON {excitedly}: I have a theory!"]
        )
        assert subtitle.structure.has_curly_brackets

    def test_structure_detects_curly_brackets_after_colon(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON: I have {excitedly} a theory!",
            lines=["SHELDON: I have {excitedly} a theory!"]
        )
        assert subtitle.structure.has_curly_brackets

    def test_structure_detects_music(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="♪ Not again... ♪",
            lines=["♪ Not again... ♪"]
        )
        assert subtitle.structure.has_music

    def test_structure_detects_leading_dash_single_line(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Hello world",
            lines=["-Hello world"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_leading_dash_first_line_only(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Hello world\nSecond line",
            lines=["-Hello world", "Second line"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_leading_dash_second_line_only(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="First line\n-World",
            lines=["First line", "-World"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_leading_dash_both_lines(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Hello\n-World",
            lines=["-Hello", "-World"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_different_dash_types(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="–Hello\n—World",  # en dash, em dash
            lines=["–Hello", "—World"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_dash_with_spaces(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text=" - Hello world\n – World ",
            lines=[" - Hello world", " – World "]
        )
        assert subtitle.structure.has_dashes

    def test_structure_detects_dash_with_special_chars(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-#Sighs#",
            lines=["-#Sighs#"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_ignores_non_leading_dash(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Hello - world\nWorld - hello",
            lines=["Hello - world", "World - hello"]
        )
        assert not subtitle.structure.has_dashes

    def test_structure_ignores_dash_in_middle(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Hello-world\nWorld-hello",
            lines=["Hello-world", "World-hello"]
        )
        assert not subtitle.structure.has_dashes

    def test_structure_ignores_dash_at_end(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Hello world-\nWorld hello-",
            lines=["Hello world-", "World hello-"]
        )
        assert not subtitle.structure.has_dashes

    def test_structure_mixed_leading_and_non_leading(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Hello world\nThis is - a test",
            lines=["-Hello world", "This is - a test"]
        )
        assert subtitle.structure.has_dashes

    def test_structure_line_count(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Line 1\nLine 2\nLine 3",
            lines=["Line 1", "Line 2", "Line 3"]
        )
        assert subtitle.structure.line_count == 3

    def test_structure_no_special_content(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Hello world. How are you?",
            lines=["Hello world. How are you?"]
        )
        assert not subtitle.structure.has_speakers
        assert not subtitle.structure.has_parentheses
        assert not subtitle.structure.has_brackets
        assert not subtitle.structure.has_curly_brackets
        assert not subtitle.structure.has_music
        assert not subtitle.structure.has_dashes

    def test_speaker_name_cleaning_with_special_chars(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="SHELDON (excitedly): I have a theory!",
            lines=["SHELDON (excitedly): I have a theory!"]
        )
        assert "SHELDON" in subtitle.structure.speakers

    # --------------------------------------
    # Integration tests (complete cleaning)
    # --------------------------------------

    def test_clean_subtitle_single_speaker(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="PERSON: How are you?",
            lines=["PERSON: How are you?"]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == "How are you?"

    def test_clean_subtitle_multiple_speakers(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="SHELDON: She's not that intelligent.\nLEONARD: She fixed your equation.",
            lines=["SHELDON: She's not that intelligent.",
                   "LEONARD: She fixed your equation."]
        )
        expected = "-She's not that intelligent.\n-She fixed your equation."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_no_dashes_needed(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="Hello world.\nHow are you?",
            lines=["Hello world.", "How are you?"]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == "Hello world.\nHow are you?"

    def test_clean_subtitle_speaker_then_dash(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="LESLIE: Good night, guys. Good job.\n-Thanks.",
            lines=["LESLIE: Good night, guys. Good job.", "-Thanks."]
        )
        expected = "-Good night, guys. Good job.\n-Thanks."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_dash_then_speaker(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Good night, guys. Good job.\nLESLIE: Thanks.",
            lines=["-Good night, guys. Good job.", "LESLIE: Thanks."]
        )
        expected = "-Good night, guys. Good job.\n-Thanks."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_preserves_meaningful_dashes(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-Hello world\n-This is a test",
            lines=["-Hello world", "-This is a test"]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == "-Hello world\n-This is a test"

    def test_clean_subtitle_no_dashes_needed_in_mixed_patterns(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="{excitedly} I have a theory!\n#Sighs# ♪ Not again... ♪",
            lines=["{excitedly} I have a theory!",
                   "#Sighs# ♪ Not again... ♪"]
        )
        expected = "I have a theory!\nNot again..."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_speaker_then_dash_in_mixed_patterns(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="SHELDON {excitedly}: I have a theory!\n-#Sighs# ♪ Not again... ♪",
            lines=["SHELDON {excitedly}: I have a theory!",
                   "-#Sighs# ♪ Not again... ♪"]
        )
        expected = "-I have a theory!\n-Not again..."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_dash_then_speaker_in_mixed_patterns(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="-I have (excitedly) a theory!\nLEONARD: [Sighs] ♪ Not again... ♪",
            lines=["-I have (excitedly) a theory!",
                   "LEONARD: [Sighs] ♪ Not again... ♪"]
        )
        expected = "-I have a theory!\n-Not again..."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_two_speakers_in_mixed_patterns(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="SHELDON (excitedly): I have a theory!\nLEONARD: [Sighs] ♪ Not again... ♪",
            lines=["SHELDON (excitedly): I have a theory!",
                   "LEONARD: [Sighs] ♪ Not again... ♪"]
        )
        expected = "-I have a theory!\n-Not again..."
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_preserves_dashes_in_mixed_patterns(self):
        subtitle = Subtitle(
            number=1, start_time="00:00:01,000", end_time="00:00:03,000",
            text="-(applause) Hello [music] world\n-♪Thanks♪",
            lines=["-(applause) Hello [music] world", "-♪Thanks♪"]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == "-Hello world\n-Thanks"

    def test_clean_subtitle_preserves_valid_content(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="Hello world.\nHow are you today?",
            lines=["Hello world.", "How are you today?"]
        )
        expected = "Hello world.\nHow are you today?"
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == expected

    def test_clean_subtitle_empty_subtitle(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="",
            lines=[]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == ""

    def test_clean_subtitle_with_only_special_content(self):
        subtitle = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:03,000",
            text="(applause) [music] ♪",
            lines=["(applause) [music] ♪"]
        )
        result = TextCleaner.clean_subtitle(subtitle)
        assert result.text == ""
