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

ROOT = Path(__file__).resolve().parents[2]
API_URL = "https://api.openai.com/v1/responses"


def load_prompt_rows(path: Path) -> list[dict]:
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
    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, http.client.IncompleteRead, http.client.RemoteDisconnected, ssl.SSLError) as exc:
            if attempt >= retries:
                raise
            sleep_seconds = min(2 ** attempt, 30)
            print(f"transient network error, retrying in {sleep_seconds}s: {exc}", flush=True)
            time.sleep(sleep_seconds)
    raise RuntimeError("unreachable retry state")


def extract_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"].strip()

    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def run_method(
    rows: list[dict],
    method: str,
    output_path: Path,
    api_key: str,
    model: str,
    max_output_tokens: int,
    limit: int | None,
    delay_seconds: float,
    resume: bool,
    retries: int,
) -> int:
    prompt_key = "direct_prompt" if method == "direct" else "sqlplus_prompt"
    done = existing_ids(output_path) if resume else set()
    selected_rows = rows[:limit] if limit is not None else rows
    count = 0

    for row in selected_rows:
        case_id = row["id"]
        if case_id in done:
            continue
        response = call_openai(api_key, model, row[prompt_key], max_output_tokens, retries)
        prediction = extract_text(response)
        append_jsonl(
            output_path,
            {
                "id": case_id,
                "prediction": prediction,
                "model": model,
                "method": method,
                "response_id": response.get("id"),
                "usage": response.get("usage", {}),
            },
        )
        count += 1
        print(f"{method}: wrote {case_id}", flush=True)
        if delay_seconds > 0:
            time.sleep(delay_seconds)
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default=str(ROOT / "data" / "baseline_prompts.jsonl"))
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--method", choices=["direct", "sqlplus", "both"], default="both")
    parser.add_argument("--direct-output", default=str(ROOT / "outputs" / "baseline" / "direct_model.jsonl"))
    parser.add_argument("--sqlplus-output", default=str(ROOT / "outputs" / "baseline" / "sqlplus_model.jsonl"))
    parser.add_argument("--max-output-tokens", type=int, default=1500)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_prompt_rows(Path(args.prompts))
    if args.dry_run:
        print(f"Loaded {len(rows)} prompt rows")
        print(f"Model: {args.model}")
        print(f"Method: {args.method}")
        print("Dry run did not call the OpenAI API")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set. Set it before running real model experiments.", file=sys.stderr)
        return 2

    total = 0
    if args.method in {"direct", "both"}:
        total += run_method(
            rows,
            "direct",
            Path(args.direct_output),
            api_key,
            args.model,
            args.max_output_tokens,
            args.limit,
            args.delay_seconds,
            args.resume,
            args.retries,
        )
    if args.method in {"sqlplus", "both"}:
        total += run_method(
            rows,
            "sqlplus",
            Path(args.sqlplus_output),
            api_key,
            args.model,
            args.max_output_tokens,
            args.limit,
            args.delay_seconds,
            args.resume,
            args.retries,
        )
    print(f"Wrote {total} predictions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
