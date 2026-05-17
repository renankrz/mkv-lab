"""End-to-end pipeline tests and Decider behaviour.

These tests exercise the full default pipeline (the equivalent of the
previous ``TextCleaner.clean_subtitle`` integration tests) and the policy
boundaries of :class:`AutoDecider` and :class:`AcceptAllDecider`.
"""

from mkvlab.fix_cc import (
    AcceptAllDecider,
    AutoDecider,
    Confidence,
    Proposal,
    Subtitle,
    clean_subtitle,
    default_pipeline,
    run_pipeline,
)

from .helpers import make_subtitle

# ---------------------------------------------------------------------------
# Deciders (policy tests, independent of any specific step)
# ---------------------------------------------------------------------------


def _proposal(confidence, original=None, proposed=None):
    original = original or make_subtitle("a")
    proposed = proposed or make_subtitle("b")
    return Proposal("dummy", original, proposed, confidence)


class TestAutoDecider:
    def test_accepts_certain(self):
        assert AutoDecider().accepts(_proposal(Confidence.CERTAIN)) is True

    def test_rejects_ambiguous(self):
        assert AutoDecider().accepts(_proposal(Confidence.AMBIGUOUS)) is False


class TestAcceptAllDecider:
    def test_accepts_certain(self):
        assert AcceptAllDecider().accepts(_proposal(Confidence.CERTAIN)) is True

    def test_accepts_ambiguous(self):
        assert AcceptAllDecider().accepts(_proposal(Confidence.AMBIGUOUS)) is True


# ---------------------------------------------------------------------------
# Auto-only pipeline behaviour (what runs unattended)
# ---------------------------------------------------------------------------


class TestAutoModePipeline:
    """With ``AutoDecider``, only CERTAIN steps fire (ellipsis + cleanup)."""

    def test_fixes_lengthy_ellipsis(self):
        sub = make_subtitle("Hello....")
        result = run_pipeline(sub, default_pipeline(), AutoDecider())
        assert result.text == "Hello..."

    def test_does_not_remove_parentheses(self):
        sub = make_subtitle("(noise) Hello")
        result = run_pipeline(sub, default_pipeline(), AutoDecider())
        assert "(noise)" in result.text

    def test_does_not_remove_speakers(self):
        sub = make_subtitle("SHELDON: Hello")
        result = run_pipeline(sub, default_pipeline(), AutoDecider())
        assert result.text.startswith("SHELDON:")

    def test_applies_final_cleanup(self):
        sub = make_subtitle("Hello  ,  world  !")
        result = run_pipeline(sub, default_pipeline(), AutoDecider())
        assert result.text == "Hello, world!"


# ---------------------------------------------------------------------------
# Full pipeline behaviour (every step accepted)
# ---------------------------------------------------------------------------


class TestFullPipeline:
    """Integration tests mirroring the original ``clean_subtitle`` cases."""

    def test_single_speaker(self):
        assert (
            clean_subtitle(make_subtitle("PERSON: How are you?")).text == "How are you?"
        )

    def test_multiple_speakers(self):
        sub = make_subtitle(
            "SHELDON: She's not that intelligent.\nLEONARD: She fixed your equation."
        )
        assert (
            clean_subtitle(sub).text
            == "-She's not that intelligent.\n-She fixed your equation."
        )

    def test_no_dashes_needed(self):
        sub = make_subtitle("Hello world.\nHow are you?")
        assert clean_subtitle(sub).text == "Hello world.\nHow are you?"

    def test_speaker_then_dash(self):
        sub = make_subtitle("LESLIE: Good night, guys. Good job.\n-Thanks.")
        assert clean_subtitle(sub).text == "-Good night, guys. Good job.\n-Thanks."

    def test_dash_then_speaker(self):
        sub = make_subtitle("-Good night, guys. Good job.\nLESLIE: Thanks.")
        assert clean_subtitle(sub).text == "-Good night, guys. Good job.\n-Thanks."

    def test_preserves_meaningful_dashes(self):
        sub = make_subtitle("-Hello world\n-This is a test")
        assert clean_subtitle(sub).text == "-Hello world\n-This is a test"

    def test_no_dashes_needed_mixed_patterns(self):
        sub = make_subtitle("{excitedly} I have a theory!\n#Sighs# ♪ Not again... ♪")
        assert clean_subtitle(sub).text == "I have a theory!\nNot again..."

    def test_speaker_then_dash_mixed_patterns(self):
        sub = make_subtitle(
            "SHELDON {excitedly}: I have a theory!\n-#Sighs# ♪ Not again... ♪"
        )
        assert clean_subtitle(sub).text == "-I have a theory!\n-Not again..."

    def test_dash_then_speaker_mixed_patterns(self):
        sub = make_subtitle(
            "-I have (excitedly) a theory!\nLEONARD: [Sighs] ♪ Not again... ♪"
        )
        assert clean_subtitle(sub).text == "-I have a theory!\n-Not again..."

    def test_two_speakers_mixed_patterns(self):
        sub = make_subtitle(
            "SHELDON (excitedly): I have a theory!\nLEONARD: [Sighs] ♪ Not again... ♪"
        )
        assert clean_subtitle(sub).text == "-I have a theory!\n-Not again..."

    def test_preserves_dashes_mixed_patterns(self):
        sub = make_subtitle("-(applause) Hello [music] world\n-♪Thanks♪")
        assert clean_subtitle(sub).text == "-Hello world\n-Thanks"

    def test_preserves_valid_content(self):
        sub = make_subtitle("Hello world.\nHow are you today?")
        assert clean_subtitle(sub).text == "Hello world.\nHow are you today?"

    def test_empty_subtitle(self):
        assert clean_subtitle(make_subtitle("")).text == ""

    def test_only_special_content(self):
        assert clean_subtitle(make_subtitle("(applause) [music] ♪")).text == ""

    # Multiline pattern cases ------------------------------------------------

    def test_multiline_parentheses_full(self):
        sub = make_subtitle(
            '(2001: A SPACE ODYSSEY\'S "MAIN TITLE"\nPLAYS OVER SPEAKERS)'
        )
        assert clean_subtitle(sub).text == ""

    def test_multiline_parentheses_partial(self):
        sub = make_subtitle("Hello (this spans\ntwo lines) world.")
        assert clean_subtitle(sub).text == "Hello world."

    def test_multiline_brackets_full(self):
        sub = make_subtitle("[DRAMATIC MUSIC\nPLAYING]")
        assert clean_subtitle(sub).text == ""

    def test_multiline_brackets_partial(self):
        sub = make_subtitle("Hello [this spans\ntwo lines] world.")
        assert clean_subtitle(sub).text == "Hello world."

    def test_multiline_curly_full(self):
        sub = make_subtitle("{DRAMATIC MUSIC\nPLAYING}")
        assert clean_subtitle(sub).text == ""

    def test_multiline_parentheses_text_after(self):
        sub = make_subtitle("(WHISPERING)\nHow are you?")
        assert clean_subtitle(sub).text == "How are you?"

    # Double-hyphen / ellipsis interactions ----------------------------------

    def test_double_hyphens_end_of_line(self):
        sub = make_subtitle("It wasn't-- It was not--\nYou are a nutcase.")
        assert (
            clean_subtitle(sub).text
            == "It wasn't\u2014It was not\u2014\nYou are a nutcase."
        )

    def test_double_hyphens_single_line(self):
        sub = make_subtitle("Wait-- no, I didn't mean--")
        assert clean_subtitle(sub).text == "Wait\u2014no, I didn't mean\u2014"

    def test_double_hyphens_with_speaker(self):
        sub = make_subtitle("JOHN: I was just--\nMARY: Don't even start.")
        assert clean_subtitle(sub).text == "-I was just\u2014\n-Don't even start."

    def test_lengthy_ellipsis_end_of_line(self):
        sub = make_subtitle("There was, uh, Joyce Kim,\nLeslie Winkle....")
        assert clean_subtitle(sub).text == "There was, uh, Joyce Kim,\nLeslie Winkle..."

    def test_lengthy_ellipsis_single_line(self):
        sub = make_subtitle("Wait.... no, I didn't mean.....")
        assert clean_subtitle(sub).text == "Wait... no, I didn't mean..."

    def test_lengthy_ellipsis_with_speaker(self):
        sub = make_subtitle("JOHN: I was just....\nMARY: Don't even start.....")
        assert clean_subtitle(sub).text == "-I was just...\n-Don't even start..."

    def test_lengthy_ellipsis_with_double_hyphens(self):
        sub = make_subtitle("It wasn't-- Joyce Kim,\nLeslie Winkle....")
        assert clean_subtitle(sub).text == "It wasn't\u2014Joyce Kim,\nLeslie Winkle..."


# ---------------------------------------------------------------------------
# Subtitle model semantics
# ---------------------------------------------------------------------------


class TestSubtitleModel:
    def test_original_text_preserved_across_with_text(self):
        sub = make_subtitle("ORIG")
        derived = sub.with_text("new")
        assert derived.text == "new"
        assert derived.original_text == "ORIG"

    def test_original_text_initialised_from_text(self):
        sub = Subtitle(
            number=1,
            start_time="00:00:01,000",
            end_time="00:00:02,000",
            text="hi",
        )
        assert sub.original_text == "hi"
