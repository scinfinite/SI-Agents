from tools.sandbox.local_sandbox import LocalSandbox


def test_command_results_have_unique_ids(tmp_path) -> None:
    sandbox = LocalSandbox(tmp_path)

    first = sandbox.run("python -c \"print('one')\"")
    second = sandbox.run("python -c \"print('two')\"")

    assert first.id != second.id
    assert first.started_at.tzinfo is not None
    assert second.started_at.tzinfo is not None
