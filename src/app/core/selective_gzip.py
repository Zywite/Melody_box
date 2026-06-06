"""Selective GZip middleware.

The stock :class:`starlette.middleware.gzip.GZipMiddleware` compresses
every response larger than ``minimum_size``, regardless of content type.
That wastes CPU on already-compressed payloads (mp3, mp4, webm, jpg, png, ...)
where gzip can only grow the body. This middleware inspects the
``Content-Type`` of each outgoing response and only compresses text-y
payloads.
"""

import gzip
from typing import Iterable

from starlette.types import ASGIApp, Message, Receive, Scope, Send


COMPRESSIBLE_PREFIXES: tuple[str, ...] = (
    "text/",
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-yaml",
    "image/svg+xml",
)


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
        "type": "http.response.start",
        "status": start.get("status", 200),
        "headers": out,
    }


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

            if message["type"] == "http.response.start":
                raw_headers = list(message.get("headers", []))
                ct = _header_value(raw_headers, b"content-type")
                ce = _header_value(raw_headers, b"content-encoding")
                if ce or not _is_compressible(ct):
                    compressible = False
                    await send(message)
                else:
                    compressible = True
                    start_captured = message
                return

            if message["type"] != "http.response.body":
                await send(message)
                return

            body = message.get("body", b"") or b""
            more_body = message.get("more_body", False)

            if compressible is False:
                await send(message)
                return

            if compressible is None:
                await send(message)
                return

            body_chunks.append(body)
            if more_body:
                return

            full_body = b"".join(body_chunks)
            assert start_captured is not None
            if len(full_body) >= self.minimum_size:
                compressed = gzip.compress(full_body, compresslevel=5)
                if len(compressed) < len(full_body):
                    await send(_make_compressed_start(start_captured, compressed))
                    await send({"type": "http.response.body", "body": compressed, "more_body": False})
                else:
                    await send(start_captured)
                    await send({"type": "http.response.body", "body": full_body, "more_body": False})
            else:
                await send(start_captured)
                await send({"type": "http.response.body", "body": full_body, "more_body": False})

            start_captured = None
            compressible = None
            body_chunks.clear()

        await self.app(scope, receive, send_wrapper)
