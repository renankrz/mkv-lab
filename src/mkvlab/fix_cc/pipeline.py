"""Cleaning pipeline core: :class:`CleaningStep`, :class:`Decider`, runner.

The orchestrator is intentionally tiny — it iterates the configured steps
against a running :class:`Subtitle`, asks the :class:`Decider` whether each
:class:`Proposal` should be applied, and threads the accepted result into
the next step.

This separation makes the pipeline open for extension:

* New transformations = new :class:`CleaningStep`.
* New decision policies (e.g. an AI-backed one) = new :class:`Decider`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Protocol

from .model import Confidence, Proposal, Subtitle


class CleaningStep(ABC):
    """A single atomic transformation of a :class:`Subtitle`.

    Each step decides internally whether it operates on the whole text,
    on individual lines, or by consulting the original subtitle layout.
    """

    #: Short identifier, useful for logging and proposals.
    name: str = ""

    @abstractmethod
    def propose(self, subtitle: Subtitle) -> Proposal:
        """Produces a :class:`Proposal` describing the desired transformation."""
        raise NotImplementedError


class Decider(Protocol):
    """Policy that decides whether a step's proposal should be applied."""

    def accepts(self, proposal: Proposal) -> bool: ...


class AutoDecider:
    """Accepts only :attr:`Confidence.CERTAIN` proposals — unattended-safe."""

    def accepts(self, proposal: Proposal) -> bool:
        return proposal.confidence is Confidence.CERTAIN


class AcceptAllDecider:
    """Accepts every proposal — used to compute the fully-cleaned preview."""

    def accepts(self, proposal: Proposal) -> bool:  # noqa: ARG002
        return True


def run_pipeline(
    subtitle: Subtitle,
    steps: List[CleaningStep],
    decider: Decider,
) -> Subtitle:
    """Runs ``steps`` sequentially against ``subtitle``, applying each
    proposal the ``decider`` accepts. Subsequent steps observe the cumulative
    effect of previously-accepted transformations.
    """
    current = subtitle
    for step in steps:
        proposal = step.propose(current)
        if decider.accepts(proposal):
            current = proposal.proposed
    return current
