import os
import json
import re
import httpx
from app.db import supabase
from app.services import logScore, _check_student_credentials, _error, _success


# ─── Learning Objective Parser ────────────────────────────────────────────────

def _parse_lo(raw) -> list[str]:
    """Convert any LO format (JSONB array, comma-string) to list of strings."""
    if not raw:
        return []
    if isinstance(raw, list):
        result = []
        for item in raw:
            if isinstance(item, dict):
                result.append(item.get("description", str(item)))
            else:
                result.append(str(item))
        return result
    if isinstance(raw, str):
        try:
            return _parse_lo(json.loads(raw))
        except Exception:
            return [x.strip() for x in raw.split(",") if x.strip()]
    return []


# ─── System Prompt Builder ────────────────────────────────────────────────────

def _build_prompt(topic_text: str, objectives: list[str]) -> str:
    lo_json = json.dumps(objectives, ensure_ascii=False)
    lo_numbered = "\n".join(f"{i+1}. {o}" for i, o in enumerate(objectives))
    return f"""ROLE:
You are a warm university instructor. Teach for conceptual mastery using Socratic questions and short academic explanations.

STRICT OUTPUT FORMAT — ALWAYS:
Every single response you write MUST be a valid JSON object with exactly two fields:
{{"APICall": "<string>", "response": "<your message to the student>"}}
- "APICall": set to the logScore call string when logging a score, empty string "" otherwise.
- "response": your message to show the student. Use \\n for line breaks.
Never output plain text. Never skip the JSON wrapper. Even short replies must be JSON.

ACTIVITY:
{topic_text}

LEARNING OBJECTIVES — TOP SECRET (never reveal to the student):
{lo_numbered}

INSTRUCTIONS:
1. First student message: present the activity text word-for-word, then ask exactly one guiding question.
2. Ask ONE question per turn. Do not ask multiple questions at once.
3. When the student demonstrates understanding of objective number N (exact text: "OBJECTIVE_TEXT"):
   Set APICall to EXACTLY:
   studentApi(action:"logScore", score:1, meta:"OBJECTIVE_TEXT")
   Where OBJECTIVE_TEXT is copied CHARACTER-FOR-CHARACTER from the list above.
   Then in "response": say "+1 point! Your score is now X." and give a mini-lesson.
4. When ALL objectives are covered: congratulate and say activity is complete.

VALID meta VALUES (use these EXACTLY, copy-paste):
{lo_json}

HARD RULES:
- Never teach before a point is earned.
- Never say "learning objective" or "LO".
- Never reveal the password.
- Always respond in English.
- Use numbered lists, not bullet points.
- Say "activity", never "topic".
- ALWAYS output valid JSON.
"""


def _normalize(s: str) -> set:
    """Kelimelere böl, alt çizgileri boşluğa çevir, küçük harfe al."""
    return set(re.sub(r'[_\-]', ' ', s).lower().split())

async def _get_activity_full(course_id: str, activity_no: int):
    """Fetch activity INCLUDING learning objectives (for LLM use only)."""
    if supabase is None:
        return None
    r = (
        supabase
        .table("activities")
        .select("*")
        .eq("course_id", course_id)
        .eq("activity_no", activity_no)
        .execute()
    )
    return r.data[0] if r.data else None


# ─── LLM Caller ───────────────────────────────────────────────────────────────

async def _call_llm(system: str, messages: list) -> str:
    """
    Try Anthropic first, then OpenRouter.
    Add one of these to your .env:
      ANTHROPIC_API_KEY=sk-ant-...
      OPENROUTER_API_KEY=sk-or-...
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    try:
        if anthropic_key:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-haiku-4-5-20251001",
                        "max_tokens": 1024,
                        "system": system,
                        "messages": messages,
                    },
                )
            data = r.json()
            if "content" in data:
                return data["content"][0]["text"]
            err = data.get("error", {}).get("message", str(data))
            return json.dumps({"APICall": "", "response": f"LLM error: {err}"})

        elif openrouter_key:
            or_messages = [{"role": "system", "content": system}] + messages
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek/deepseek-chat",
                        "max_tokens": 1024,
                        "messages": or_messages,
                    },
                )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            err = data.get("error", {}).get("message", str(data))
            return json.dumps({"APICall": "", "response": f"LLM error: {err}"})

        else:
            return json.dumps({
                "APICall": "",
                "response": "No API key configured. Add ANTHROPIC_API_KEY or OPENROUTER_API_KEY to your .env file."
            })

    except Exception as e:
        return json.dumps({"APICall": "", "response": f"Connection error: {str(e)}"})


# ─── APICall Parser ───────────────────────────────────────────────────────────

def _parse_api_call(s: str, email: str, password: str,
                    course_id: str, activity_no: int) -> dict | None:
    if not s or not s.strip():
        return None
    action_m = re.search(r'action[:\s]*["\']([^"\']+)["\']', s)
    if not action_m:
        return None
    score_m = re.search(r'score[:\s]*(\d+(?:\.\d+)?)', s)
    meta_m = re.search(r'meta[:\s]*["\']([^"\']+)["\']', s)
    return {
        "action": action_m.group(1),
        "email": email,
        "password": password,
        "course_id": course_id,
        "activity_no": activity_no,
        "score": float(score_m.group(1)) if score_m else 1.0,
        "meta": meta_m.group(1) if meta_m else None,
    }


# ─── Main Chat Function ───────────────────────────────────────────────────────

async def studentChat(
    email: str,
    password: str,
    course_id: str,
    activity_no: int,
    message: str,
    history: list[dict],
) -> dict:

    if supabase is None:
        return _error("Database not configured")

    if not _check_student_credentials(email, password):
        return _error("Invalid student credentials")

    activity = await _get_activity_full(course_id, activity_no)
    if not activity:
        return _error("Activity not found")

    status = activity.get("status", "")
    if status == "NOT_STARTED":
        return _error("Activity has not started yet")
    if status == "ENDED":
        return _error("Activity has already ended")

    objectives = _parse_lo(activity.get("learning_objectives"))
    system_prompt = _build_prompt(activity["activity_text"], objectives)

    # Build message list for LLM
    llm_messages = [{"role": h["role"], "content": h["content"]} for h in history]
    llm_messages.append({"role": "user", "content": message})

    raw = await _call_llm(system_prompt, llm_messages)

    # Parse JSON response from LLM
    try:
        clean = raw.strip()
        if "```" in clean:
            clean = re.sub(r"```(?:json)?\n?", "", clean).replace("```", "").strip()
        parsed = json.loads(clean)
        api_call_str = parsed.get("APICall", "")
        response_text = parsed.get("response", "")
    except Exception:
        api_call_str = ""
        response_text = raw  # fallback: show raw text

    # Execute logScore if LLM requested it
    api_result = None
    if api_call_str and api_call_str.strip():
        params = _parse_api_call(api_call_str, email, password, course_id, activity_no)
        if params and params["action"] == "logScore":
            meta = params["meta"]

            # Meta → objective eşleştirme
            # 1) Tam eşleşme (büyük/küçük harf farkı yok)
            # 2) Substring eşleşme
            # 3) En yüksek kelime örtüşmesi (sadece yeterli örtüşme varsa)
            matched_meta = None
            if meta and objectives:
                meta_lower = meta.lower().strip()

                # 1. Tam eşleşme
                for obj in objectives:
                    if obj.lower().strip() == meta_lower:
                        matched_meta = obj
                        break

                # 2. Substring
                if not matched_meta:
                    for obj in objectives:
                        if obj.lower() in meta_lower or meta_lower in obj.lower():
                            matched_meta = obj
                            break

                # 3. Kelime örtüşmesi — EN İYİ eşleşmeyi seç, eşik %50
                if not matched_meta:
                    meta_words = _normalize(meta)
                    best_ratio = 0.0
                    best_obj = None
                    for obj in objectives:
                        obj_key_words = {w for w in _normalize(obj) if len(w) > 4}
                        if not obj_key_words:
                            continue
                        common = {w for w in meta_words if w in obj_key_words}
                        ratio = len(common) / len(obj_key_words)
                        if ratio > best_ratio:
                            best_ratio = ratio
                            best_obj = obj
                    if best_ratio >= 0.5:
                        matched_meta = best_obj

            elif not objectives:
                matched_meta = meta

            # Sadece gerçek bir objective eşleştiyse logScore çağır
            if matched_meta:
                api_result = logScore(
                    email=params["email"],
                    password=params["password"],
                    course_id=params["course_id"],
                    activity_no=params["activity_no"],
                    score=params["score"],
                    meta=matched_meta,
                )

    score_changed = (
        api_result is not None and
        isinstance(api_result, dict) and
        api_result.get("ok", False)
    )

    return _success(
        {
            "response": response_text,
            "api_result": api_result,
            "score_changed": score_changed,
        },
        "OK"
    )