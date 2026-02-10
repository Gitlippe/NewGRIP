from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentProviderConfig:
    mode: str = "disabled"
    remote_model: str | None = None
    local_model: str | None = None


class AgentProvider:
    def __init__(self, config: AgentProviderConfig) -> None:
        self.config = config

    def generate_text(self, prompt: str) -> str:
        if self.config.mode == "disabled":
            return "disabled"
        if self.config.mode == "local_model":
            return f"local:{prompt[:120]}"
        if self.config.mode == "remote_model":
            return f"remote:{prompt[:120]}"
        raise ValueError(f"Unsupported mode: {self.config.mode}")
