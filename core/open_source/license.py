from core.open_source import models  # noqa: I001


# Conservative identifiers only. This is not legal advice and does not replace license review.
KNOWN_PERMISSIVE = frozenset({"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD"})


def assess_license(spdx_id: str | None, source: str = "repository metadata") -> models.LicenseAssessment:
    identifier = spdx_id or "UNKNOWN"
    if spdx_id is None:
        return models.LicenseAssessment(
            identifier,
            None,
            models.IntelligenceStatus.UNKNOWN,
            None,
            None,
            source,
            "No SPDX identifier was supplied; inspect the repository license text.",
        )
    if spdx_id in KNOWN_PERMISSIVE:
        return models.LicenseAssessment(
            identifier,
            spdx_id,
            models.IntelligenceStatus.OBSERVED,
            True,
            True,
            source,
            "Permissive SPDX identifier observed; obligations still require license-text review.",
        )
    return models.LicenseAssessment(
        identifier,
        spdx_id,
        models.IntelligenceStatus.OBSERVED,
        None,
        None,
        source,
        "Identifier is not classified by the conservative built-in policy; perform license-text and terms review.",
    )
