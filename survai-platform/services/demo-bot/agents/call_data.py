"""
Shared state dataclass passed as AgentSession userdata throughout the call.
All three agents (Greeting, Questions, Ending) access this via context.userdata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class DemoCallData:
    survey_responses: dict
    caller_number: str
    call_start_time: datetime
    log_handler: Any
    cleanup_logging_fn: Callable
    disconnect_fn: Callable
    question_ids: List[str]
    questions_map: dict
    survey_id: Optional[str]
    survey_url: Optional[str]
    rider_email: Optional[str]
    rider_name: Optional[str]
    # agent registry: "greeting", "questions", "ending"
    agents: Dict[str, Any] = field(default_factory=dict)
    # set by to_questions/to_ending tools so next agent can copy chat history
    prev_agent: Optional[Any] = None
