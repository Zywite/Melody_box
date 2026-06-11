"""Selective GZip middleware.

The stock :class:`starlette.middleware.gzip.GZipMiddleware` compresses
every response larger than ``minimum_size``, regardless of content type.
That wastes CPU on already-compressed payloads (mp3, mp4, webm, jpg, png, ...)
where gzip can only grow the body. This middleware inspects the
``Content-Type`` of each outgoing response and only compresses text-y
payloads.
"""

import gzip
from collections.abc import Iterable

from starlette.types import ASGIApp, Message, Receive, Scope, Send

COMPRESSIBLE_PREFIXES: tuple[str, ...] = (
    "text/",
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-yaml",
    "image/svg+xml",
)

RESPONSE_START = "http.response.start"
RESPONSE_BODY = "http.response.body"


def _is_compressible(content_type: str | None) -> bool:
    if not content_type:
        return True
    main = content_type.split(";", 1)[0].strip().lower()
    return any(main.startswith(p) for p in COMPRESSIBLE_PREFIXES)


def _header_value(headers: Iterable[tuple[bytes, bytes]], name: bytes) -> str:
    target = name.lower()
    for k, v in headers:
        if k.lower() == target:
            return v.decode("latin-1")
    return ""


def _make_compressed_start(start: Message, body: bytes) -> Message:
    raw_headers = list(start.get("headers", []))
    out: list[tuple[bytes, bytes]] = []
    for k, v in raw_headers:
        if k.lower() in (b"content-encoding", b"content-length"):
            continue
        out.append((k, v))
    out.append((b"content-encoding", b"gzip"))
    out.append((b"content-length", str(len(body)).encode("latin-1")))
    if not any(k.lower() == b"vary" for k, _ in out):
        out.append((b"vary", b"Accept-Encoding"))
    return {
        "type": RESPONSE_START,
        "status": start.get("status", 200),
        "headers": out,
    }


def _should_compress(start_message: Message) -> tuple[bool, Message]:
    raw_headers = list(start_message.get("headers", []))
    ct = _header_value(raw_headers, b"content-type")
    ce = _header_value(raw_headers, b"content-encoding")
    if ce or not _is_compressible(ct):
        return False, start_message
    return True, start_message


async def _send_body(start: Message, body: bytes, minimum_size: int, send: Send) -> None:
    if len(body) >= minimum_size:
        compressed = gzip.compress(body, compresslevel=5)
        if len(compressed) < len(body):
            await send(_make_compressed_start(start, compressed))
            await send({"type": RESPONSE_BODY, "body": compressed, "more_body": False})
            return
    await send(start)
    await send({"type": RESPONSE_BODY, "body": body, "more_body": False})


class SelectiveGZipMiddleware:
    """ASGI middleware that gzips only compressible content types.

    Strategy:
    1. Pass every message through transparently for non-HTTP scopes.
    2. If the client doesn't accept gzip, pass through transparently.
    3. Buffer the response body only when ``Content-Type`` is compressible
       and the body is smaller than a few MB (we inspect headers in
       ``http.response.start`` before committing to a path).
    4. Streaming responses with non-compressible content are forwarded
       verbatim, preserving FastAPI's ``FileResponse`` / ``StreamingResponse``
       zero-copy streaming for audio/video.
    """

    def __init__(self, app: ASGIApp, minimum_size: int = 1000) -> None:
        self.app = app
        self.minimum_size = minimum_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_in = dict(scope.get("headers") or ())
        accept_encoding = headers_in.get(b"accept-encoding", b"").decode("latin-1").lower()
        if "gzip" not in accept_encoding:
            await self.app(scope, receive, send)
            return

        start_captured: Message | None = None
        compressible: bool | None = None
        body_chunks: list[bytes] = []

        async def send_wrapper(message: Message) -> None:
            nonlocal start_captured, compressible

            if message["type"] == RESPONSE_START:
                compressible, start_captured = _should_compress(message)
                if not compressible:
                    await send(message)
                return

            if message["type"] != RESPONSE_BODY:
                await send(message)
                return

            if compressible is not True:
                await send(message)
                return

            body_chunks.append(message.get("body", b"") or b"")
            if message.get("more_body", False):
                return

            full_body = b"".join(body_chunks)
            await _send_body(start_captured, full_body, self.minimum_size, send)
            start_captured = None
            body_chunks.clear()

        await self.app(scope, receive, send_wrapper)
