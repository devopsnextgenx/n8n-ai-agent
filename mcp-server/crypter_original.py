from fastmcp import FastMCP
import base64
from typing import Optional

mcp = FastMCP("Base64MCP")

@mcp.tool()
def encrypt(data: str) -> str:
    """
    Accepts a base64 or raw string data, returns base64-encoded string.
    If input is not valid base64, treat as raw bytes (utf-8) then encode.
    """
    try:
        # If it's valid base64, decode first
        raw = base64.b64decode(data, validate=True)
    except Exception:
        # treat input as utf-8 text
        raw = data.encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


@mcp.tool()
def decrypt(encoded: str) -> Optional[str]:
    """
    Accepts a base64-encoded string, returns decoded string (utf-8) if possible,
    or returns None / error if decoding fails.
    """
    try:
        raw = base64.b64decode(encoded, validate=True)
        # Try decode to utf-8 string
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            # Return binary data as hex or repr if not valid UTF-8
            return raw.hex()
    except Exception:
        return None  # or raise a ToolError in FastMCP if supported

if __name__ == "__main__":
    mcp.run()
