"""Read-only provider adapter contract for model intelligence."""

from typing import Protocol

from core.provider_intelligence.models import QuotaSnapshot


class ProviderAdapter(Protocol):
    """A provider adapter reports metadata/usage; it is not a permission authority."""

    @property
    def provider_id(self) -> str: ...

    def quota(self) -> QuotaSnapshot | None: ...
