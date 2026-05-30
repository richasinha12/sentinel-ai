"""Core shared types, interfaces, and base agent class for Sentinel AI."""
from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class AgentType(str, Enum):
    GTM = "gtm"
    FINANCE = "finance"
    SECURITY = "security"
    SYNTHESIS = "synthesis"


class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Signal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: AgentType
    title: str
    summary: str
    severity: SignalSeverity
    source_url: Optional[str] = None
    raw_data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SynthesisInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    narrative: str                      # Claude's cross-agent story
    signals: list[Signal]               # contributing signals
    recommended_actions: list[str]
    severity: SignalSeverity
    affected_domains: list[AgentType]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentRunResult(BaseModel):
    agent: AgentType
    signals: list[Signal]
    model_used: str                     # claude / featherless model name
    duration_ms: int
    error: Optional[str] = None
