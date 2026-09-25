"""Truemailer API - email trust and disposable-domain analysis."""
import asyncio
import json
import os
import re
import time
from typing import Any, Dict, Optional

import dns.resolver
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKLIST_LOCAL = os.path.join(BASE_DIR, "blocklist", "blocklist.txt")
ALLOWLIST_LOCAL = os.path.join(BASE_DIR, "allowlist", "allowlist.json")
CLIENTS_FILE = os.path.join(BASE_DIR, "clients.json")
DEFAULT_PORT = int(os.getenv("PORT", "8000"))
ADMIN_TOKEN = os.getenv("TRUEMAILER_ADMIN_TOKEN")

TEMP_PATTERNS = {
    "tempmail", "mailinator", "guerrillamail", "10minutemail", "dispostable",
    "trashmail", "sharklasers", "fakeinbox", "getnada", "yopmail", "spambox",
    "maildrop", "disposable", "temporary", "temp-mail", "mailpoof", "moakt",
    "dropmail", "mailnesia", "inboxkitten"
}
PROVIDERS = {
    "gmail.com": "Google Gmail", "googlemail.com": "Google Gmail",
    "outlook.com": "Microsoft Outlook", "hotmail.com": "Microsoft Outlook",
    "live.com": "Microsoft Outlook", "yahoo.com": "Yahoo Mail",
    "icloud.com": "Apple iCloud Mail", "proton.me": "Proton Mail",
    "protonmail.com": "Proton Mail", "zoho.com": "Zoho Mail",
    "aol.com": "AOL Mail", "rediffmail.com": "Rediffmail"
}


def load_domains(path: str) -> set[str]:
    """Load either newline-separated domains or a JSON array/object of domains."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            return set()
        if path.endswith(".json"):
            data = json.loads(raw)
            if isinstance(data, list):
                values = data
            elif isinstance(data, dict):
                values = data.get("domains", data.get("blocklist", []))
            else:
                values = []
        else:
            values = raw.splitlines()
        result = set()
        for value in values:
            value = str(value).strip().lower()
            if not value or value.startswith("#"):
                continue
            if "@" in value and value.count("@") == 1:
                value = value.split("@", 1)[1]
            result.add(value.strip("."))
        return result
    except (OSError, ValueError, TypeError) as exc:
        print(f"Could not load {path}: {exc}")
        return set()


def load_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, TypeError):
        return default


BLOCKSET = load_domains(BLOCKLIST_LOCAL)
ALLOWSET = load_domains(ALLOWLIST_LOCAL)
CLIENTS = load_json(CLIENTS_FILE, {
    "demo": {"key": "demo_key_123", "name": "Demo Client", "limit_per_day": 250, "usage": {}}
})

app = FastAPI(title="Truemailer API", version="2.0.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


class VerifyRequest(BaseModel):
    email: EmailStr
    api_key: Optional[str] = None


def client_for_key(key: Optional[str]):
    if not key:
        return None, None
    for client_id, data in CLIENTS.items():
        if data.get("key") == key:
            return client_id, data
    return None, None


def usage_today(client_id: str) -> int:
    return int(CLIENTS.get(client_id, {}).get("usage", {}).get(time.strftime("%Y-%m-%d"), 0))


def increment_usage(client_id: str) -> None:
    today = time.strftime("%Y-%m-%d")
    data = CLIENTS.setdefault(client_id, {})
    usage = data.setdefault("usage", {})
    usage[today] = usage.get(today, 0) + 1
    try:
        with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(CLIENTS, f, indent=2)
    except OSError:
        pass


def dns_check(domain: str) -> tuple[bool, bool, list[str]]:
    """Return (domain_resolves, has_mx, mx_hosts). A fallback A/AAAA record is not called MX."""
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0
    resolver.timeout = 2.0
    has_mx = False
    mx_hosts: list[str] = []
    try:
        answers = resolver.resolve(domain, "MX")
        mx_hosts = sorted({str(a.exchange).rstrip(".") for a in answers})
        has_mx = bool(mx_hosts)
    except Exception:
        pass
    resolves = has_mx
    if not resolves:
        for record_type in ("A", "AAAA"):
            try:
                resolver.resolve(domain, record_type)
                resolves = True
                break
            except Exception:
                continue
    return resolves, has_mx, mx_hosts


async def remote_disposable_check(domain: str) -> Optional[bool]:
    """Best-effort external signal. Unknown is treated as unknown, never disposable."""
    try:
        async with httpx.AsyncClient(timeout=3.5) as client:
            response = await client.get(f"https://open.kickbox.com/v1/disposable/{domain}")
            if response.status_code == 200:
                payload = response.json()
                value = payload.get("disposable")
                return bool(value) if isinstance(value, bool) else None
    except Exception:
        return None
    return None


def calculate_score(*, syntax: bool, resolves: bool, mx: bool, disposable: bool,
                    blocklisted: bool, allowlisted: bool, provider: Optional[str],
                    remote_disposable: Optional[bool]) -> int:
    if disposable or blocklisted:
        return 0
    score = 20 if syntax else 0
    score += 20 if resolves else 0
    score += 30 if mx else 0
    score += 15 if provider else 0
    score += 15 if allowlisted else 0
    if remote_disposable is False:
        score += 5
    return min(100, score)


async def evaluate_email(email: str) -> Dict[str, Any]:
    email = str(email).strip().lower()
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""
    provider = PROVIDERS.get(domain)
    allowlisted = domain in ALLOWSET
    blocklisted = domain in BLOCKSET
    pattern = next((p for p in TEMP_PATTERNS if p in domain), None)

    result: Dict[str, Any] = {
        "email": email, "domain": domain, "valid": False,
        "is_disposable": False, "disposable": False, "provider": provider,
        "syntax_valid": True, "domain_exists": False, "mx": False,
        "mx_hosts": [], "blocklisted": blocklisted, "allowlisted": allowlisted,
        "suspicious_indicators": [], "trust_score": 0, "reason": ""
    }

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        result.update(syntax_valid=False, reason="Invalid email syntax")
        result["suspicious_indicators"] = ["Invalid email format"]
        return result

    if blocklisted:
        result.update(is_disposable=True, disposable=True, reason="Domain found in local disposable blocklist")
        result["suspicious_indicators"].append("Blocklisted domain")
        return result

    if pattern:
        result.update(is_disposable=True, disposable=True, reason=f"Disposable pattern matched: {pattern}")
        result["suspicious_indicators"].append(f"Disposable-looking domain pattern: {pattern}")
        return result

    resolves, has_mx, mx_hosts = await asyncio.to_thread(dns_check, domain)
    result.update(domain_exists=resolves, mx=has_mx, mx_hosts=mx_hosts)
    if not resolves:
        result.update(reason="Domain does not resolve in DNS")
        result["suspicious_indicators"].append("No DNS A/AAAA/MX resolution")
        return result
    if not has_mx:
        result["suspicious_indicators"].append("No MX record found")

    remote = await remote_disposable_check(domain)
    result["remote_disposable"] = remote
    if remote is True:
        result.update(is_disposable=True, disposable=True, reason="Marked disposable by external disposable-domain check")
        result["suspicious_indicators"].append("External disposable signal")
        return result

    score = calculate_score(
        syntax=True, resolves=resolves, mx=has_mx, disposable=False,
        blocklisted=False, allowlisted=allowlisted, provider=provider,
        remote_disposable=remote
    )
    result["trust_score"] = score
    result["valid"] = resolves and (has_mx or allowlisted)
    if result["valid"]:
        result["reason"] = "Domain resolves and accepts email via MX" if has_mx else "Allowlisted domain with DNS resolution"
    else:
        result["reason"] = "Domain exists but no MX record was found"
    return result


@app.get("/status")
async def status():
    return {"ok": True, "version": app.version, "block_count": len(BLOCKSET), "allow_count": len(ALLOWSET), "clients": len(CLIENTS)}


@app.post("/verify")
async def verify_endpoint(req: VerifyRequest, x_api_key: Optional[str] = Header(None)):
    key = x_api_key or req.api_key
    client_id, client_data = client_for_key(key)
    if client_id:
        limit = int(client_data.get("limit_per_day", 250))
        if usage_today(client_id) >= limit:
            raise HTTPException(status_code=429, detail="daily limit exceeded")

    result = await evaluate_email(str(req.email))
    if client_id:
        increment_usage(client_id)
    return result


def require_admin(token: Optional[str]) -> None:
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/admin/clients")
async def list_clients(x_admin_token: Optional[str] = Header(None)):
    require_admin(x_admin_token)
    return {cid: {k: v for k, v in data.items() if k != "key"} for cid, data in CLIENTS.items()}


@app.post("/admin/update-lists")
async def update_lists(payload: Dict[str, Any], x_admin_token: Optional[str] = Header(None)):
    require_admin(x_admin_token)
    allow = sorted({str(x).strip().lower() for x in payload.get("allow", []) if str(x).strip()})
    block = sorted({str(x).strip().lower() for x in payload.get("block", []) if str(x).strip()})
    os.makedirs(os.path.dirname(ALLOWLIST_LOCAL), exist_ok=True)
    with open(ALLOWLIST_LOCAL, "w", encoding="utf-8") as f:
        json.dump(allow, f, indent=2)
    with open(BLOCKLIST_LOCAL, "w", encoding="utf-8") as f:
        f.write("\n".join(block) + ("\n" if block else ""))
    global ALLOWSET, BLOCKSET
    ALLOWSET, BLOCKSET = set(allow), set(block)
    return {"updated": True, "allow_count": len(ALLOWSET), "block_count": len(BLOCKSET)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=DEFAULT_PORT)
