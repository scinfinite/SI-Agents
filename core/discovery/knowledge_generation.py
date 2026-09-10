from __future__ import annotations

from dataclasses import dataclass

from core.discovery.models import DiscoveryFinding


@dataclass(frozen=True)
class KnowledgeProposal:
    """A discovery-derived proposal; it never promotes knowledge by itself."""

    name: str
    category: str
    summary: str
    source: str
    confidence: float
    verification: tuple[str, ...]


def propose_from_findings(findings: tuple[DiscoveryFinding, ...]) -> tuple[KnowledgeProposal, ...]:
    proposals: list[KnowledgeProposal] = []
    for finding in findings:
        proposals.append(
            KnowledgeProposal(
                name=finding.name,
                category=finding.category,
                summary=f"Discovered {finding.name}: {finding.value}",
                source=finding.source,
                confidence=finding.confidence,
                verification=finding.verification,
            )
        )
    return tuple(proposals)
