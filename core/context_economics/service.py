from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from typing import Callable

from core.hardening.redaction import redact

from .models import (
    ContextBudget,
    ContextItem,
    ContextScope,
    ContextSelection,
    ModelContextProfile,
)


class ContextEconomics:
    """Deterministic, auditable context selection and compaction policy.

    This component decides what context may enter a model request. It does not grant
    permissions, persist business state, or select a model/provider.
    """

    def __init__(
        self,
        budgets: tuple[ContextBudget, ...] = (),
        *,
        compression_threshold: float = 0.85,
        max_compacted_chars: int = 2000,
    ) -> None:
        if not 0 < compression_threshold <= 1:
            raise ValueError("Compression threshold must be in (0, 1]")
        if max_compacted_chars < 64:
            raise ValueError("Compaction limit is too small")
        self._budgets = {budget.scope: budget for budget in budgets}
        if len(self._budgets) != len(budgets):
            raise ValueError("Duplicate context budget scope")
        self.compression_threshold = compression_threshold
        self.max_compacted_chars = max_compacted_chars

    @staticmethod
    def _decision_id(
        items: tuple[ContextItem, ...], model: ModelContextProfile, reason: str
    ) -> str:
        material = "|".join(f"{item.item_id}:{item.fingerprint}" for item in items)
        return sha256(f"{model.model_id}|{reason}|{material}".encode()).hexdigest()

    def _effective_budget(
        self, scopes: tuple[ContextScope, ...], model: ModelContextProfile
    ) -> tuple[int, float | None]:
        token_limit = model.input_capacity
        cost_limit: float | None = None
        for scope in scopes:
            budget = self._budgets.get(scope)
            if budget is not None:
                token_limit = min(token_limit, budget.limit_tokens)
                if budget.limit_cost is not None:
                    cost_limit = (
                        budget.limit_cost
                        if cost_limit is None
                        else min(cost_limit, budget.limit_cost)
                    )
        return token_limit, cost_limit

    @staticmethod
    def _score(item: ContextItem) -> float:
        # Importance dominates relevance; deterministic tie-breaking is by ID later.
        return (0.65 * item.importance) + (0.35 * item.relevance)

    def compact(self, item: ContextItem) -> ContextItem:
        if len(item.content) <= self.max_compacted_chars:
            return item
        head = int(self.max_compacted_chars * 0.7)
        tail = self.max_compacted_chars - head - 24
        content = f"{item.content[:head]}\n[…compacted…]\n{item.content[-tail:]}"
        return replace(
            item,
            content=content,
            estimated_tokens=max(1, (len(content) + 3) // 4),
            tags=item.tags + ("compacted",),
        )

    def deduplicate(self, items: tuple[ContextItem, ...]) -> tuple[ContextItem, ...]:
        seen: set[str] = set()
        result: list[ContextItem] = []
        for item in items:
            if item.fingerprint in seen:
                continue
            seen.add(item.fingerprint)
            result.append(item)
        return tuple(result)

    def select(
        self,
        items: tuple[ContextItem, ...],
        model: ModelContextProfile,
        *,
        active_scopes: tuple[ContextScope, ...] = (),
        allow_sensitive: bool = False,
        redact_secrets: bool = True,
        cost_limit_override: float | None = None,
        summarizer: Callable[[str], str] | None = None,
    ) -> ContextSelection:
        if cost_limit_override is not None and cost_limit_override < 0:
            raise ValueError("Cost limit override must not be negative")
        unique = self.deduplicate(items)
        token_limit, cost_limit = self._effective_budget(active_scopes, model)
        if cost_limit_override is not None:
            cost_limit = (
                cost_limit_override
                if cost_limit is None
                else min(cost_limit, cost_limit_override)
            )
        eligible: list[ContextItem] = []
        dropped: list[ContextItem] = []
        redacted = False
        for item in unique:
            if item.sensitive and not allow_sensitive:
                dropped.append(item)
                continue
            if item.secret_like:
                if not redact_secrets:
                    dropped.append(item)
                    continue
                safe = redact({"content": item.content})["content"]
                if safe != item.content:
                    redacted = True
                    item = replace(
                        item,
                        content=str(safe),
                        estimated_tokens=max(1, (len(str(safe)) + 3) // 4),
                    )
            eligible.append(item)

        ranked = sorted(
            eligible,
            key=lambda x: (-self._score(x), -x.importance, x.item_id),
        )
        selected: list[ContextItem] = []
        total_tokens = 0
        total_cost = 0.0
        for item in ranked:
            candidate = item
            if total_tokens + candidate.token_estimate() > int(
                token_limit * self.compression_threshold
            ):
                if summarizer is not None and len(candidate.content) > self.max_compacted_chars:
                    summary = summarizer(candidate.content).strip()
                    if summary:
                        candidate = replace(
                            candidate,
                            content=summary,
                            estimated_tokens=max(1, (len(summary) + 3) // 4),
                            tags=item.tags + ("summarized",),
                        )
                elif len(candidate.content) > self.max_compacted_chars:
                    candidate = self.compact(candidate)
            tokens = candidate.token_estimate()
            cost = (
                candidate.estimated_cost
                if candidate.estimated_cost is not None
                else tokens * model.input_token_cost
            )
            if total_tokens + tokens > token_limit or (
                cost_limit is not None and total_cost + cost > cost_limit
            ):
                dropped.append(candidate)
                continue
            selected.append(candidate)
            total_tokens += tokens
            total_cost += cost

        selected_ids = {item.item_id for item in selected}
        dropped.extend(
            item
            for item in eligible
            if item.item_id not in selected_ids and item not in dropped
        )
        selected_tuple = tuple(sorted(selected, key=lambda x: x.item_id))
        dropped_tuple = tuple(sorted(dropped, key=lambda x: x.item_id))
        reason = "deterministic relevance/importance selection under model and scope budgets"
        evidence = (
            f"model={model.model_id}",
            f"input_capacity={model.input_capacity}",
            f"token_limit={token_limit}",
            f"selected_tokens={total_tokens}",
            f"selected_cost={total_cost:.10f}",
            f"selected={len(selected_tuple)}",
            f"dropped={len(dropped_tuple)}",
        )
        return ContextSelection(
            selected_tuple,
            dropped_tuple,
            total_tokens,
            total_cost,
            self._decision_id(selected_tuple, model, reason),
            reason,
            evidence,
            redacted,
        )
