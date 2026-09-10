from core.orchestrator.orchestrator import Orchestrator
from tools.registry.registry import ToolRegistry


def test_orchestrator_owns_a_tool_registry_without_granting_execution() -> None:
    orchestrator = Orchestrator(tool_registry=ToolRegistry())
    orchestrator.register_builtin_tools()
    assert len(orchestrator.tools.all()) == 14
    assert orchestrator.tools.by_category("sandbox")


def test_custom_tool_registration_is_explicit() -> None:
    from tools.registry.registry import ToolDescriptor

    orchestrator = Orchestrator()
    tool = orchestrator.register_tool(ToolDescriptor("custom", "test"))
    assert orchestrator.tools.get(tool.id).name == "custom"
