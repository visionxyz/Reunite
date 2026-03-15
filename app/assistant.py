"""AI assistant that actively guides users to recall details."""

import os
from openai import AsyncOpenAI
from app.models import Entry
from app import matching

_client: AsyncOpenAI | None = None


def _get_openai() -> AsyncOpenAI | None:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your-openai-api-key-here":
            _client = AsyncOpenAI()
    return _client


SYSTEM_PROMPT = """You are an AI assistant for "Reunite", a platform that helps find missing children and reconnect families. Your job is to gently and patiently guide users through conversation to recall more details, improving the chances of a successful match.

## Your Role
- If the user is a **parent looking for a child**: help them add details about the child's features, habits, and circumstances of disappearance
- If the user is a **child/adult looking for family**: gently guide them to recall childhood fragments

## Questioning Strategy
1. **Sensory memories**: smells, sounds, textures are often more durable than visual memories. Ask: Do you remember any smells? Sounds?
2. **Daily routines**: What did you eat? What did you play? Who took you to school? When did the lights come on at home?
3. **Spatial memories**: How many floors was the house? What did the stairs look like? What could you see from the window? How long was the walk to places you visited often?
4. **Relationships**: Who else was in the family? Neighbors? Frequent visitors? What name/nickname did they call you?
5. **Special events**: Birthdays? Holidays? Getting sick? Getting hurt? Moving?
6. **Physical details**: Birthmarks, scars, body features (these are the strongest matching evidence)

## Important Principles
- Only ask 1-2 questions at a time, don't overwhelm the user
- Use a warm, encouraging tone, don't pressure the user
- If the user says "I don't remember", try a different angle
- Build on what the user has already shared, dig deeper into details
- Memories may be inaccurate — don't dismiss the user's recollections, but gently explore other possibilities

## Match Clues Reference
If the system provides potential match information, you can ask targeted questions based on these clues, but NEVER directly reveal match results to the user.
For example: if a potential match's father was a carpenter, you might ask "Do you remember any particular smells at home? Like wood, paint, anything like that?"

## Language
Always respond in the same language the user is using.
"""


async def chat(
    entry_id: int | None,
    entry_info: dict,
    messages: list[dict],
) -> str:
    """
    AI assistant conversation.
    - entry_id: existing entry ID (if registered)
    - entry_info: current info the user has provided
    - messages: conversation history [{"role": "user/assistant", "content": "..."}]
    """
    client = _get_openai()
    if not client:
        return "The AI assistant requires an OpenAI API Key. Please set OPENAI_API_KEY in your .env file."

    # Build context from entry info
    context_parts = ["## User's Current Information"]
    entry = Entry(**{k: v for k, v in entry_info.items() if k in Entry.__dataclass_fields__})
    if entry.entry_type:
        context_parts.append(f"- Type: {entry.entry_type}")
    if entry.name:
        context_parts.append(f"- Name: {entry.name}")
    if entry.gender:
        context_parts.append(f"- Gender: {entry.gender}")
    if entry.birth_date:
        context_parts.append(f"- Birth date: {entry.birth_date}")
    if entry.missing_date:
        context_parts.append(f"- Missing date: {entry.missing_date}")
    if entry.location:
        context_parts.append(f"- Location: {entry.location}")
    if entry.physical_features:
        context_parts.append(f"- Physical features: {entry.physical_features}")
    if entry.description:
        context_parts.append(f"- Description: {entry.description}")

    # Search for potential matches to give AI context (but don't reveal directly)
    match_context = ""
    if entry.entry_type and (entry.description or entry.location or entry.physical_features):
        try:
            results = matching.find_matches(entry, top_k=3)
            if results and any(r.score > 0 for r in results):
                match_parts = ["\n## Potential Match Clues (for your reference ONLY — do NOT reveal to the user)"]
                for r in results[:3]:
                    if r.score > 0:
                        match_parts.append(
                            f"- Match {r.score:.0%}: {r.entry.to_search_text()[:200]}"
                        )
                match_context = "\n".join(match_parts)
        except Exception:
            pass

    system_content = SYSTEM_PROMPT + "\n\n" + "\n".join(context_parts)
    if match_context:
        system_content += "\n" + match_context

    # Build OpenAI messages
    oai_messages = [{"role": "system", "content": system_content}]

    # If this is the first message (no history), add a starter prompt
    if not messages:
        oai_messages.append({
            "role": "user",
            "content": "Based on the information I've provided so far, please start guiding me to recall more details.",
        })
    else:
        oai_messages.extend(messages)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=oai_messages,
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content or "Sorry, I'm unable to respond at the moment."
