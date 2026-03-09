"""
Shared state dataclass passed as AgentSession userdata throughout the call.
Both GreeterAgent and QuestionsAgent access this via context.userdata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class SurveyCallData:
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
    # agent registry filled by agent.py before session.start()
    agents: Dict[str, Any] = field(default_factory=dict)
    # set by to_questions tool so QuestionsAgent can copy chat history
    prev_agent: Optional[Any] = None
    # Spanish question texts used when an English-initiated call switches to Spanish mid-call
    questions_map_es: dict = field(default_factory=dict)
    # set by set_language() tool after recipient chooses their preferred language
    detected_language: str = "en"
