"""
SafePassage Second Brain - Open WebUI Pipe
Streams answers from the local FastAPI /ask/stream endpoint.
Install: Open WebUI > Workspace > Pipes > New Pipe > paste this file.
"""

import json

import requests
from pydantic import BaseModel, Field


def _detect_quick_replies(answer: str) -> list[str]:
    """
    Detect what quick replies are valid based on the answer text content.
    Returns a list of reply strings to show as hints, or [] if not a
    prompt-for-input response.
    """
    text = answer.strip()

    # Conflict resolution prompt
    if "KEEP NEW" in text and "KEEP OLD" in text:
        return ["KEEP NEW", "KEEP OLD"]

    # YES/NO confirmation prompt (post order or announcement preview)
    if "Reply YES to write to vault" in text or "Reply YES to confirm" in text:
        return ["YES", "NO"]

    # Wizard step 1 - community alias prompt
    if "Reply with your community alias" in text:
        return ["SR", "CBK", "MON", "GWT", "PBM", "CANCEL"]

    # Wizard step 2 - paste text prompt (free text input, no hint needed)
    if "Paste the post order text" in text:
        return []

    return []


class Pipe:
    class Valves(BaseModel):
        BASE_URL: str = Field(
            default="http://host.docker.internal:8000",
            description=(
                "Base URL of the SafePassage FastAPI backend. "
                "Use http://localhost:8000 if Open WebUI runs on the host. "
                "Use http://host.docker.internal:8000 if Open WebUI runs in Docker."
            ),
        )
        TOP_K: int = Field(default=5, description="Number of chunks to retrieve.")

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict) -> str:
        # Open WebUI sends the full chat transcript. Keep prior user turns only
        # so the backend can resolve community context without storing history.
        messages = body.get("messages", [])
        history = [
            m["content"]
            for m in messages[:-1]
            if m.get("role") == "user"
        ][-5:]

        # The current question is the most recent user message.
        question = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                question = m["content"]
                break
        if not question:
            yield "No question found in messages."
            return

        payload = {
            "question": question,
            "top_k": self.valves.TOP_K,
            "history": history,
        }

        stream_url = f"{self.valves.BASE_URL}/ask/stream"
        citations_data: dict | None = None
        streamed_any_token = False

        try:
            # Stream token events from FastAPI as they arrive.
            with requests.post(
                stream_url,
                json=payload,
                stream=True,
                timeout=90,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    decoded = (
                        line.decode("utf-8") if isinstance(line, bytes) else line
                    )
                    if not decoded.startswith("data:"):
                        continue
                    data_str = decoded[len("data:"):].strip()
                    if data_str == "[DONE]":
                        break
                    if data_str.startswith("[CITATIONS]"):
                        try:
                            citations_data = json.loads(
                                data_str[len("[CITATIONS]"):]
                            )
                            if not streamed_any_token:
                                synthetic_answer = citations_data.get("answer", "")
                                if synthetic_answer:
                                    yield synthetic_answer
                        except json.JSONDecodeError:
                            pass
                        continue

                    # Regular token event. It is JSON encoded by /ask/stream.
                    try:
                        token = json.loads(data_str)
                        streamed_any_token = True
                        yield token
                    except json.JSONDecodeError:
                        continue

        except Exception as error:
            # If streaming is unavailable, fall back to the existing /ask API.
            try:
                fallback = requests.post(
                    f"{self.valves.BASE_URL}/ask",
                    json=payload,
                    timeout=90,
                )
                fallback.raise_for_status()
                data = fallback.json()
                yield data.get("answer", f"Error: {error}")
                citations_data = data
            except Exception as fallback_error:
                yield f"SafePassage backend unavailable: {fallback_error}"
                return

        # Append structured citations, confidence, and warnings after the answer.
        if citations_data:
            citations = citations_data.get("answer_citations", [])
            warnings = citations_data.get("warnings", [])
            confidence = citations_data.get("retrieval_confidence", "")
            reason = citations_data.get("confidence_reason", "")

            footer_parts: list[str] = []

            if citations:
                footer_parts.append("\n\n**Sources:**")
                for c in citations:
                    src = c.get("source_file", "")
                    sec = c.get("section", "")
                    sid = c.get("source_id", "")
                    footer_parts.append(f"[{sid}] {src} - {sec}")

            if confidence:
                footer_parts.append(
                    f"\n**Confidence:** {confidence}"
                )
                if reason:
                    footer_parts.append(f"**Reason:** {reason}")

            if warnings:
                footer_parts.append("\n**Warnings:**")
                for w in warnings:
                    footer_parts.append(f"- {w}")

            if footer_parts:
                yield "\n".join(footer_parts)

        # Quick reply hints - shown when the response is a prompt-for-input
        quick_replies = _detect_quick_replies(
            citations_data.get("answer", "") if citations_data else ""
        )
        if quick_replies:
            pills = "  ·  ".join(f"**{r}**" for r in quick_replies)
            yield f"\n\n---\n💬 Quick reply: {pills}"
