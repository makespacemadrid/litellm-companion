"""Proxy FastAPI application for OpenAI-compatible requests."""
from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import create_engine, ensure_minimum_schema, get_session, init_session_maker
from shared.crud import get_config
from shared.db_models import Model, Provider


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _messages_to_prompt(messages: object) -> str:
    """Convert chat messages into a plain prompt string."""
    if not isinstance(messages, list):
        return ""
    parts: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content", "")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
            content_text = "\n".join(text_parts)
        else:
            content_text = content if isinstance(content, str) else ""
        if role:
            parts.append(f"{role}: {content_text}".strip())
        else:
            parts.append(content_text)
    return "\n".join([p for p in parts if p])


def _sanitize_messages(messages: object) -> list[dict]:
    """Normalize messages to avoid null content errors."""
    if not isinstance(messages, list):
        return []
    sanitized = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        msg = dict(message)
        if "content" not in msg or msg["content"] is None:
            msg["content"] = ""
        sanitized.append(msg)
    return sanitized


def create_app() -> FastAPI:
    app = FastAPI(title="LiteLLM Proxy")

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "info").upper())
    logger = logging.getLogger("proxy")
    log_requests = _env_flag("PROXY_LOG_REQUESTS", False)
    log_body = _env_flag("PROXY_LOG_BODY", False)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Proxy service starting...")
        engine = create_engine()
        init_session_maker(engine)
        await ensure_minimum_schema(engine)
        logger.info("Proxy service ready")
        yield

    app.router.lifespan_context = lifespan

    async def _proxy_to_litellm(
        request: Request,
        target_path: str,
        session: AsyncSession,
    ):
        """Proxy OpenAI-compatible requests to LiteLLM with optional completion fallback."""
        config = await get_config(session)
        if not config.litellm_base_url:
            raise HTTPException(400, "LiteLLM destination not configured")

        raw_body = await request.body()
        try:
            payload = await request.json()
        except Exception:
            payload = None

        normalized_payload = False
        force_completion = False
        dropped_keys = []
        compat_mode = None

        if isinstance(payload, dict) and "messages" not in payload and "input" in payload:
            input_value = payload.get("input")
            if isinstance(input_value, list):
                payload = dict(payload)
                payload["messages"] = input_value
                payload.pop("input", None)
                normalized_payload = True
            elif isinstance(input_value, str):
                payload = dict(payload)
                payload["prompt"] = input_value
                payload.pop("input", None)
                normalized_payload = True
                force_completion = True

        if isinstance(payload, dict) and "messages" not in payload and "prompt" in payload:
            prompt_value = payload.get("prompt")
            if isinstance(prompt_value, list):
                if all(isinstance(item, dict) for item in prompt_value):
                    payload = dict(payload)
                    payload["messages"] = prompt_value
                    payload.pop("prompt", None)
                    normalized_payload = True
                elif all(isinstance(item, str) for item in prompt_value):
                    payload = dict(payload)
                    payload["prompt"] = "\n".join(prompt_value)
                    normalized_payload = True

        if isinstance(payload, dict):
            model_name = payload.get("model")
            if isinstance(model_name, str):
                compat_result = await session.execute(
                    select(Model)
                    .join(Provider)
                    .where(Provider.type == "compat", Model.model_id == model_name)
                )
                compat_model = compat_result.scalars().first()
                if compat_model:
                    compat_mode = (compat_model.user_params_dict or {}).get("mode")
                    if compat_mode == "completion" and "messages" in payload:
                        payload = dict(payload)
                        payload["prompt"] = _messages_to_prompt(payload.get("messages"))
                        payload.pop("messages", None)
                        normalized_payload = True
                        force_completion = True

            if "messages" in payload:
                sanitized_messages = _sanitize_messages(payload.get("messages"))
                if sanitized_messages != payload.get("messages"):
                    payload = dict(payload)
                    payload["messages"] = sanitized_messages
                    normalized_payload = True

        if isinstance(payload, dict):
            allowed_chat = {
                "model",
                "messages",
                "stream",
                "temperature",
                "top_p",
                "max_tokens",
                "n",
                "stop",
                "presence_penalty",
                "frequency_penalty",
                "logit_bias",
                "user",
                "tools",
                "tool_choice",
                "response_format",
                "seed",
                "stream_options",
            }
            allowed_completion = {
                "model",
                "prompt",
                "stream",
                "temperature",
                "top_p",
                "max_tokens",
                "n",
                "stop",
                "presence_penalty",
                "frequency_penalty",
                "logit_bias",
                "user",
                "suffix",
                "best_of",
                "logprobs",
                "echo",
            }
            if force_completion:
                allowed = allowed_completion
            else:
                allowed = allowed_chat if "messages" in payload else allowed_completion
            filtered_payload = {key: value for key, value in payload.items() if key in allowed}
            dropped_keys = [key for key in payload.keys() if key not in allowed]
            if filtered_payload != payload:
                payload = filtered_payload
                normalized_payload = True

        if normalized_payload:
            raw_body = json.dumps(payload, ensure_ascii=True).encode("utf-8")

        payload_keys = sorted(payload.keys()) if isinstance(payload, dict) else None
        raw_preview = raw_body.decode("utf-8", errors="ignore")
        if len(raw_preview) > 2000:
            raw_preview = raw_preview[:2000] + "...(truncated)"

        source_path = target_path
        if target_path.endswith("/v1/chat/completions"):
            has_messages = isinstance(payload, dict) and "messages" in payload
            has_prompt = isinstance(payload, dict) and "prompt" in payload
            messages_value = payload.get("messages") if isinstance(payload, dict) else None
            messages_missing = not isinstance(messages_value, list) or len(messages_value) == 0
            if not has_prompt and raw_body:
                body_text = raw_body.decode("utf-8", errors="ignore")
                has_prompt = "\"prompt\"" in body_text
            if compat_mode == "completion":
                target_path = "/v1/completions"
            elif force_completion or (has_prompt and (messages_missing or not has_messages)):
                target_path = "/v1/completions"
            elif not has_messages and (payload is None):
                target_path = "/v1/completions"

            if log_requests:
                logger.info(
                    "Proxy request: path=%s reroute=%s has_messages=%s messages_missing=%s has_prompt=%s normalized=%s compat_mode=%s dropped=%s keys=%s body_preview=%s",
                    request.url.path,
                    target_path,
                    has_messages,
                    messages_missing,
                    has_prompt,
                    normalized_payload,
                    compat_mode,
                    dropped_keys,
                    payload_keys,
                    raw_preview if log_body else "(disabled)",
                )
        else:
            if log_requests:
                logger.info(
                    "Proxy request: path=%s compat_mode=%s dropped=%s keys=%s body_preview=%s",
                    request.url.path,
                    compat_mode,
                    dropped_keys,
                    payload_keys,
                    raw_preview if log_body else "(disabled)",
                )

        base_url = config.litellm_base_url.rstrip("/")
        url = f"{base_url}{target_path}"

        headers = {}
        auth_header = request.headers.get("authorization")
        if auth_header:
            headers["authorization"] = auth_header
        elif config.litellm_api_key:
            headers["authorization"] = f"Bearer {config.litellm_api_key}"

        content_type = request.headers.get("content-type")
        if content_type:
            headers["content-type"] = content_type

        stream = False
        if isinstance(payload, dict):
            stream = bool(payload.get("stream"))
        request_model = payload.get("model") if isinstance(payload, dict) else None

        wrap_completion_to_chat = (
            source_path.endswith("/v1/chat/completions")
            and target_path.endswith("/v1/completions")
        )

        timeout = httpx.Timeout(60.0, read=None if stream else 60.0)

        if stream:

            async def _iter():
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream(
                        request.method,
                        url,
                        headers=headers,
                        content=raw_body,
                    ) as resp:
                        if resp.status_code >= 400:
                            body = await resp.aread()
                            body_preview = body.decode("utf-8", errors="ignore")
                            if len(body_preview) > 2000:
                                body_preview = body_preview[:2000] + "...(truncated)"
                            logger.error(
                                "Proxy error: status=%s url=%s body=%s",
                                resp.status_code,
                                str(resp.url),
                                body_preview,
                            )
                            yield body
                            return
                        if not wrap_completion_to_chat:
                            async for chunk in resp.aiter_bytes():
                                yield chunk
                            return

                        sent_role = False
                        async for line in resp.aiter_lines():
                            if not line:
                                continue
                            if not line.startswith("data:"):
                                continue
                            data = line[len("data:"):].strip()
                            if data == "[DONE]":
                                yield b"data: [DONE]\n\n"
                                return
                            try:
                                payload_json = json.loads(data)
                            except json.JSONDecodeError:
                                continue
                            choices = payload_json.get("choices") or []
                            if not choices:
                                continue
                            choice = choices[0]
                            delta = {}
                            if not sent_role:
                                delta["role"] = "assistant"
                                sent_role = True
                            text = choice.get("text")
                            if isinstance(text, str) and text:
                                delta["content"] = text
                            finish_reason = choice.get("finish_reason")
                            chunk = {
                                "id": payload_json.get("id"),
                                "object": "chat.completion.chunk",
                                "created": payload_json.get("created"),
                                "model": payload_json.get("model") or request_model,
                                "choices": [
                                    {
                                        "index": choice.get("index", 0),
                                        "delta": delta,
                                        "finish_reason": finish_reason,
                                    }
                                ],
                            }
                            yield f"data: {json.dumps(chunk, ensure_ascii=True)}\n\n".encode("utf-8")

            return StreamingResponse(_iter(), media_type="text/event-stream")

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.request(
                request.method,
                url,
                headers=headers,
                content=raw_body,
            )
            resp.raise_for_status()
            data = resp.json()
            if wrap_completion_to_chat and isinstance(data, dict):
                choices = data.get("choices") or []
                converted_choices = []
                for choice in choices:
                    text = choice.get("text") if isinstance(choice, dict) else None
                    converted_choices.append(
                        {
                            "index": choice.get("index", 0) if isinstance(choice, dict) else 0,
                            "message": {"role": "assistant", "content": text or ""},
                            "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
                        }
                    )
                data = {
                    "id": data.get("id"),
                    "object": "chat.completion",
                    "created": data.get("created"),
                    "model": data.get("model") or request_model,
                    "choices": converted_choices,
                    "usage": data.get("usage"),
                }
            return JSONResponse(data)

    @app.post("/v1/chat/completions")
    async def proxy_chat_completions(
        request: Request,
        session: AsyncSession = Depends(get_session),
    ):
        return await _proxy_to_litellm(request, "/v1/chat/completions", session)

    @app.post("/v1/completions")
    async def proxy_completions(
        request: Request,
        session: AsyncSession = Depends(get_session),
    ):
        return await _proxy_to_litellm(request, "/v1/completions", session)

    return app
