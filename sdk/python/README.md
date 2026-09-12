# SI-Agents Python SDK

Dependency-free, typed client for the SI-Agents Control API v1.

```python
from sdk.python.si_agents import SIClient

client = SIClient(
    "http://127.0.0.1:8787",
    token="...",
    subject="ci",
    project="example",
)
print(client.health())
for agent in client.paginate("agents", page_size=25, query="builder"):
    print(agent["id"])

run = client.create_run({"action": "inspect", "subject": "ci"}, idempotency_key="stable-001")
```

The SDK provides stable typed errors, bearer authentication, identity headers, filter-bound cursor pagination, idempotent run creation, bounded concurrent calls, and SSE/WebSocket subscription URL helpers. It never puts credentials into query strings.
