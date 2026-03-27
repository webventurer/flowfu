#!/usr/bin/env python3
"""Chat completion via OpenRouter. Zero-dependency on codefu.

Usage:
    python tools/openrouter-chat.py "prompt"
    python tools/openrouter-chat.py "prompt" -m openai/gpt-4.1
    python tools/openrouter-chat.py "prompt" -s "You are a reviewer."
"""

import os
from pathlib import Path

import click
import dotenv
import httpx

dotenv.load_dotenv(Path.home() / ".env")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4.1"


def check_env():
    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        raise click.ClickException("Missing: OPEN_ROUTER_API_KEY in ~/.env")


def send(prompt: str, model: str, system: str = "", effort: str = "") -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": model, "messages": messages}
    if effort:
        payload["reasoning"] = {"enabled": True, "effort": effort}
    resp = httpx.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPEN_ROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


@click.command()
@click.argument("prompt")
@click.option("-m", "--model", default=DEFAULT_MODEL, help=f"Model ID. Default: {DEFAULT_MODEL}.")
@click.option("-s", "--system", default="", help="System message.")
@click.option("-r", "--reasoning-effort", default="", help="Reasoning effort: low, medium, high.")
def main(prompt: str, model: str, system: str, reasoning_effort: str):
    check_env()
    data = send(prompt, model, system, reasoning_effort)
    click.echo(data["choices"][0]["message"].get("content", ""))


if __name__ == "__main__":
    main()
