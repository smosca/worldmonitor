#!/usr/bin/env python3
import json
import re
from pathlib import Path

FILE_PATH = Path("/Users/simonemosca/Documents/Develop/worldmonitor/vercel.json")

# =========================================
# CONFIG: qui decidi chi può embeddare
# =========================================
FRAME_ANCESTORS = [
    "https://3n2um923wmstyjim99tvvgdll0fklroa.ui.nabu.casa",
    "http://homeassistant.local:8123",
    "http://192.168.1.2:8123",
    "https://vanshion.9zeri.com",
]

TARGET_SOURCE = "/(.*)"  # il blocco headers principale

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def update_csp(csp: str) -> str:
    csp_norm = normalize_spaces(csp)
    if not csp_norm.endswith(";"):
        csp_norm += ";"

    frame_val = "frame-ancestors " + " ".join(FRAME_ANCESTORS) + ";"
    if re.search(r"(^|;\s*)frame-ancestors\s+[^;]*;", csp_norm):
        csp_norm = re.sub(
            r"(^|;\s*)frame-ancestors\s+[^;]*;",
            lambda m: m.group(1) + frame_val,
            csp_norm,
        )
    else:
        if "base-uri" in csp_norm:
            csp_norm = re.sub(
                r"(^|;\s*)base-uri\s+[^;]*;",
                lambda m: "; " + frame_val + " " + m.group(0).lstrip("; ").rstrip() + ";",
                csp_norm,
                count=1,
            )
            csp_norm = normalize_spaces(csp_norm).rstrip(";") + ";"
        else:
            csp_norm += " " + frame_val

    base_val = "base-uri 'self';"
    if re.search(r"(^|;\s*)base-uri\s+[^;]*;", csp_norm):
        csp_norm = re.sub(
            r"(^|;\s*)base-uri\s+[^;]*;",
            lambda m: m.group(1) + base_val,
            csp_norm,
        )
    else:
        csp_norm += " " + base_val

    csp_norm = re.sub(r"\s*;\s*", "; ", csp_norm).strip()
    if not csp_norm.endswith(";"):
        csp_norm += ";"
    return csp_norm

def main():
    if not FILE_PATH.exists():
        raise SystemExit(f"File not found: {FILE_PATH}")

    data = json.loads(FILE_PATH.read_text(encoding="utf-8"))

    changed = False

    headers_blocks = data.get("headers", [])
    for block in headers_blocks:
        if block.get("source") != TARGET_SOURCE:
            continue

        hdrs = block.get("headers", [])

        # Remove X-Frame-Options entirely (case-insensitive)
        new_hdrs = []
        for h in hdrs:
            k = (h.get("key") or "").lower().strip()
            if k == "x-frame-options":
                changed = True
                continue
            new_hdrs.append(h)
        hdrs = new_hdrs

        # Update CSP header
        for h in hdrs:
            if (h.get("key") or "").lower().strip() == "content-security-policy":
                old = h.get("value") or ""
                new = update_csp(old)
                if new != old:
                    h["value"] = new
                    changed = True

        block["headers"] = hdrs

    FILE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("✅ Patched vercel.json" if changed else "ℹ️ No changes needed")

if __name__ == "__main__":
    main()