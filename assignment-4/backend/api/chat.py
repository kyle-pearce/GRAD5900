"""
Chat API — real SSE streaming via asyncio.Queue.

POST /api/chat/send   — add a user message, start skill in background thread
GET  /api/chat/stream — SSE stream; reads from per-session queue as tokens arrive
POST /api/chat/close  — run the close skill on the current session history
"""

import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..router import resolve_skill
from ..skills.close import CloseSkill

router = APIRouter(prefix="/api/chat")

# session_id → conversation history
_sessions: dict[str, list[dict]] = {}

# session_id → asyncio.Queue of SSE event dicts
_queues: dict[str, asyncio.Queue] = {}

_executor = ThreadPoolExecutor(max_workers=10)


class SendRequest(BaseModel):
    session_id: str | None = None
    skill: str | None = None
    message: str = ""


@router.post("/send")
async def send_message(req: SendRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history = list(_sessions.get(session_id, []))

    skill_cls = resolve_skill(req.skill, req.message)
    skill = skill_cls()

    # Create the queue before launching the background task so no events are lost
    queue: asyncio.Queue = asyncio.Queue()
    _queues[session_id] = queue
    loop = asyncio.get_event_loop()

    # Capture values for the thread closure
    skill_history = list(history)
    user_msg = req.message

    def run_skill() -> None:
        assistant_tokens: list[str] = []
        try:
            for event in skill.stream(skill_history, user_msg):
                if event["event"] == "token" and isinstance(event["data"], str):
                    assistant_tokens.append(event["data"])
                loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception as exc:
            loop.call_soon_threadsafe(
                queue.put_nowait, {"event": "token", "data": f"\n\n[Error: {exc}]"}
            )
            loop.call_soon_threadsafe(queue.put_nowait, {"event": "done", "data": ""})
            return

        # Persist the turn to session history
        new_history = list(skill_history)
        if user_msg:
            new_history.append({"role": "user", "content": user_msg})
        if assistant_tokens:
            new_history.append({"role": "assistant", "content": "".join(assistant_tokens)})
        _sessions[session_id] = new_history

    loop.run_in_executor(_executor, run_skill)
    return {"session_id": session_id}


@router.get("/stream")
async def stream_session(session_id: str):
    queue = _queues.get(session_id)
    if not queue:
        return Response("Session not found", status_code=404)

    async def generator():
        while True:
            event = await queue.get()
            data = event["data"]
            payload = data if isinstance(data, str) else json.dumps(data)
            yield f"event: {event['event']}\ndata: {payload}\n\n"
            if event["event"] == "done":
                _queues.pop(session_id, None)
                break

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class CloseRequest(BaseModel):
    session_id: str


@router.post("/close")
async def close_session(req: CloseRequest):
    history = list(_sessions.get(req.session_id, []))
    skill = CloseSkill()

    queue: asyncio.Queue = asyncio.Queue()
    close_id = req.session_id + "_close"
    _queues[close_id] = queue
    loop = asyncio.get_event_loop()

    def run_close() -> None:
        try:
            for event in skill.stream(history):
                loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception as exc:
            loop.call_soon_threadsafe(
                queue.put_nowait, {"event": "token", "data": f"\n\n[Error: {exc}]"}
            )
            loop.call_soon_threadsafe(queue.put_nowait, {"event": "done", "data": ""})
        _sessions.pop(req.session_id, None)

    loop.run_in_executor(_executor, run_close)
    return {"session_id": close_id}
