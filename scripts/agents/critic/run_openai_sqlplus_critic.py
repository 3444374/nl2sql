from __future__ import annotations

import argparse
import http.client
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
API_URL = "https://api.openai.com/v1/responses"


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as handle:
        return {json.loads(line)["id"] for line in handle if line.strip()}


def call_openai(api_key: str, model: str, prompt: str, max_output_tokens: int, retries: int) -> dict:
    payload = {"model": model, "input": prompt, "max_output_tokens": max_output_tokens}
    data = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(retries + 1):
        request = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, http.client.IncompleteRead, http.client.RemoteDisconnected, ssl.SSLError) as exc:
            if attempt >= retries:
                raise
            sleep_seconds = min(2**attempt, 30)
            print(f"transient network error, retrying in {sleep_seconds}s: {exc}", flush=True)
            time.sleep(sleep_seconds)
    raise RuntimeError("unreachable retry state")


def extract_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"].strip()
    chunks = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def clean_text(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def parse_output(case_id: str, text: str) -> dict:
    cleaned = clean_text(text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {
            "id": case_id,
            "likely_error_type": "unknown",
            "localized_steps": [],
            "global_repair_hints": [],
            "confidence": "low",
            "parse_error": str(exc),
            "raw_output": text,
        }
    parsed["id"] = str(parsed.get("id") or case_id)
    parsed["raw_output"] = text
    return parsed


def build_prompt(template: str, row: dict) -> str:
    public_row = dict(row)
    public_row.pop("evaluation_only", None)
    return template.replace("{{input_json}}", json.dumps(public_row, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", default=str(ROOT / "data" / "sqlplus_schema_agent_inputs.jsonl"))
    parser.add_argument("--prompt-template", default=str(ROOT / "prompts" / "agents" / "critic" / "sqlplus_critic.md"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "agents" / "critic" / "sqlplus_critic_model.jsonl"))
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--max-output-tokens", type=int, default=1600)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_jsonl(Path(args.inputs))
    template = Path(args.prompt_template).read_text(encoding="utf-8")
    selected = rows[: args.limit] if args.limit is not None else rows

    if args.dry_run:
        print(f"Loaded {len(rows)} schema-agent rows")
        print(f"Selected {len(selected)} rows")
        print(f"Output: {args.output}")
        if selected:
            print("--- first prompt preview ---")
            print(build_prompt(template, selected[0])[:2000])
        print("Dry run did not call the OpenAI API")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set. Set it before running real model experiments.", file=sys.stderr)
        return 2

    done = existing_ids(Path(args.output)) if args.resume else set()
    written = 0
    for row in selected:
        case_id = row["id"]
        if case_id in done:
            continue
        response = call_openai(api_key, args.model, build_prompt(template, row), args.max_output_tokens, args.retries)
        parsed = parse_output(case_id, extract_text(response))
        parsed.update(
            {
                "model": args.model,
                "method": "sqlplus_critic",
                "response_id": response.get("id"),
                "usage": response.get("usage", {}),
            }
        )
        append_jsonl(Path(args.output), parsed)
        written += 1
        print(f"critic: wrote {case_id}", flush=True)
        if args.delay_seconds > 0:
            time.sleep(args.delay_seconds)
    print(f"Wrote {written} critic outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


