"""Provider/model registry with explicit duplicate protection."""

from core.provider_intelligence.models import ModelProfile, ProviderProfile


class ProviderRegistry:
    """In-memory registry; registration never grants execution permission."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderProfile] = {}

    def register(self, provider: ProviderProfile) -> None:
        if provider.provider_id in self._providers:
            raise ValueError(f"provider already registered: {provider.provider_id}")
        self._providers[provider.provider_id] = provider

    def replace(self, provider: ProviderProfile) -> None:
        if provider.provider_id not in self._providers:
            raise KeyError(provider.provider_id)
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> ProviderProfile:
        return self._providers[provider_id]

    def list_enabled(self) -> tuple[ProviderProfile, ...]:
        return tuple(
            provider
            for provider in self._providers.values()
            if provider.enabled
        )

    def models(self) -> tuple[tuple[ProviderProfile, ModelProfile], ...]:
        return tuple(
            (provider, model)
            for provider in self.list_enabled()
            for model in provider.models
            if model.enabled
        )
