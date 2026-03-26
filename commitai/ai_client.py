from __future__ import annotations

import os
import sys
from typing import Optional

SYSTEM_PROMPT = """You are an expert at writing git commit messages.
Generate {count} different commit message options following the Conventional Commits specification.
Each message should:
- Start with a type: feat, fix, docs, style, refactor, test, chore, perf, ci, build
- Be concise (under 72 characters for the subject line)
- Use the imperative mood ("add feature" not "added feature")
- Accurately describe the changes

Return ONLY a JSON array of strings, nothing else. Example:
["feat: add user authentication", "feat(auth): implement JWT login flow"]"""

USER_PROMPT = """Branch: {branch}

Recent commits (for context/style):
{recent_commits}

Staged changes:
{diff}

Generate {count} commit message options."""


def generate_messages(
    diff: str,
    context: dict,
    count: int = 5,
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> list[str]:
    if provider == "anthropic":
        return _anthropic(diff, context, count, model)
    elif provider == "openai":
        return _openai(diff, context, count, model)
    elif provider == "ollama":
        return _ollama(diff, context, count, model)
    else:
        print(f"❌ Unknown provider: {provider}", file=sys.stderr)
        sys.exit(1)


def _anthropic(diff: str, context: dict, count: int, model: Optional[str]) -> list[str]:
    try:
        import anthropic
    except ImportError:
        print("❌ anthropic package not found. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    model = model or "claude-haiku-4-5-20251001"

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=SYSTEM_PROMPT.format(count=count),
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT.format(
                    branch=context.get("branch", "main"),
                    recent_commits=context.get("recent_commits", "none"),
                    diff=diff[:8000],
                    count=count,
                ),
            }
        ],
    )

    return _parse_json(response.content[0].text)


def _openai(diff: str, context: dict, count: int, model: Optional[str]) -> list[str]:
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not found. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    model = model or "gpt-4o-mini"

    response = client.chat.completions.create(
        model=model,
        max_tokens=512,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(count=count)},
            {
                "role": "user",
                "content": USER_PROMPT.format(
                    branch=context.get("branch", "main"),
                    recent_commits=context.get("recent_commits", "none"),
                    diff=diff[:8000],
                    count=count,
                ),
            },
        ],
    )

    return _parse_json(response.choices[0].message.content)


def _ollama(diff: str, context: dict, count: int, model: Optional[str]) -> list[str]:
    try:
        import requests
    except ImportError:
        print("❌ requests package not found. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    model = model or "llama3.2"
    prompt = SYSTEM_PROMPT.format(count=count) + "\n\n" + USER_PROMPT.format(
        branch=context.get("branch", "main"),
        recent_commits=context.get("recent_commits", "none"),
        diff=diff[:8000],
        count=count,
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    return _parse_json(response.json()["response"])


def _parse_json(text: str) -> list[str]:
    import json
    import re

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    lines = [l.strip().strip('"').strip("'") for l in text.strip().splitlines() if l.strip()]
    return [l for l in lines if l][:10]
