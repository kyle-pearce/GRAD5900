"""
Onboarding API

GET  /api/onboarding/status       — check if onboarding is complete
POST /api/onboarding/use-defaults — copy Kyle's context files from WSL2 mount
POST /api/onboarding/save-custom  — generate context files from user-provided answers
"""

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.config import settings
from ..core.ollama_client import chat

router = APIRouter(prefix="/api/onboarding")

ONBOARDED_MARKER = settings.context_dir / ".onboarded"


CONTEXT_GENERATORS = {
    "goals.md": (
        "role_goals",
        "Generate a concise personal context file for an AI assistant called 'goals.md'. "
        "It should capture this person's long-term goals and current priorities based on what they told you. "
        "Format it as a markdown file with clear sections. Be direct and factual. "
        "Based on this description: {answer}",
    ),
    "projects.md": (
        "projects",
        "Generate a concise personal context file called 'projects.md' for an AI assistant. "
        "It should list the person's active projects with key details like stakeholders and status. "
        "Format as markdown with one section per project. "
        "Based on this description: {answer}",
    ),
    "writing-style.md": (
        "writing_style",
        "Generate a personal writing style guide called 'writing-style.md' for an AI assistant. "
        "Include tone, voice, phrases to use and avoid, and sign-off preferences. "
        "Based on this description: {answer}",
    ),
    "email-goals.md": (
        "email_prefs",
        "Generate a personal email preferences file called 'email-goals.md' for an AI assistant. "
        "Include communication goals, response norms, and preferred email structure. "
        "Based on this description: {answer}",
    ),
    "mental-model.md": (
        "mental_model",
        "Generate a personal decision-making and mental model file called 'mental-model.md' for an AI assistant. "
        "Include how this person makes decisions, known blind spots, and recurring failure modes. "
        "Based on this description: {answer}",
    ),
}


@router.get("/status")
async def status():
    return {"onboarded": ONBOARDED_MARKER.exists()}


@router.post("/use-defaults")
async def use_defaults():
    settings.context_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for src in settings.defaults_dir.iterdir():
        if src.suffix == ".md":
            shutil.copy2(src, settings.context_dir / src.name)
            copied.append(src.name)

    ONBOARDED_MARKER.touch()

    return {"status": "ok", "copied": copied}


class CustomContextRequest(BaseModel):
    role_goals: str
    projects: str
    writing_style: str
    email_prefs: str
    mental_model: str


@router.post("/save-custom")
async def save_custom(req: CustomContextRequest):
    settings.context_dir.mkdir(parents=True, exist_ok=True)
    answers = req.model_dump()
    written = []

    for filename, (answer_key, prompt_template) in CONTEXT_GENERATORS.items():
        answer = answers.get(answer_key, "")
        if not answer.strip():
            continue
        prompt = prompt_template.format(answer=answer)
        generated = chat([{"role": "user", "content": prompt}])
        dest = settings.context_dir / filename
        dest.write_text(generated, encoding="utf-8")
        written.append(filename)

    ONBOARDED_MARKER.touch()
    return {"status": "ok", "files_written": written}


@router.post("/reset")
async def reset():
    """Clear onboarding state so the UI redirects back to /onboard."""
    if ONBOARDED_MARKER.exists():
        ONBOARDED_MARKER.unlink()
    return {"status": "ok"}
