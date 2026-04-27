"""
Maps skill names to skill classes and handles keyword-based dispatch
for free-text input that doesn't come from a skill button click.
"""

from .skills.standup import StandupSkill
from .skills.sync import SyncSkill
from .skills.refinement import RefinementSkill
from .skills.one_on_one import OneOnOneSkill
from .skills.email import EmailSkill
from .skills.close import CloseSkill
from .skills.base import BaseSkill

SKILL_MAP: dict[str, type[BaseSkill]] = {
    "standup": StandupSkill,
    "sync": SyncSkill,
    "refinement": RefinementSkill,
    "one_on_one": OneOnOneSkill,
    "email": EmailSkill,
    "close": CloseSkill,
}

# Keyword → skill name for free-text dispatch
_KEYWORD_ROUTES: list[tuple[list[str], str]] = [
    (["standup", "end of day", "eod", "daily check", "reflect"], "standup"),
    (["sync", "meeting", "i just had a", "process meeting"], "sync"),
    (["refinement", "plan my week", "sprint planning", "weekly planning", "week plan"], "refinement"),
    (["1:1", "one on one", "1 on 1", "prep for my", "coaching"], "one_on_one"),
    (["email", "draft", "reply to", "ping", "compose"], "email"),
    (["close", "end session", "wrap up", "handoff"], "close"),
]


def resolve_skill(skill_name: str | None, message: str) -> type[BaseSkill]:
    """
    Return the skill class for a given skill name or a free-text message.
    Falls back to StandupSkill when no match is found.
    """
    if skill_name and skill_name in SKILL_MAP:
        return SKILL_MAP[skill_name]

    lower = message.lower()
    for keywords, name in _KEYWORD_ROUTES:
        if any(kw in lower for kw in keywords):
            return SKILL_MAP[name]

    return StandupSkill  # safe default
