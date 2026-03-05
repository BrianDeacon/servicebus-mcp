def decode_body(msg) -> str:
    body = msg.body
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    if hasattr(body, "__iter__") and not isinstance(body, str):
        chunks = b"".join(body)
        return chunks.decode("utf-8", errors="replace")
    return str(body)


def decode_properties(props: dict | None) -> dict:
    if not props:
        return {}
    return {
        (k.decode("utf-8", errors="replace") if isinstance(k, bytes) else str(k)):
        (v.decode("utf-8", errors="replace") if isinstance(v, bytes) else v)
        for k, v in props.items()
    }
