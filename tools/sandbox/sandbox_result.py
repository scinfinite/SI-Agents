from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    command: str
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0 and not self.timed_out
