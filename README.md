# Truemailer — Email Trust Analysis API

Truemailer is an email verification and trust-analysis service for detecting disposable addresses, checking DNS/MX infrastructure, identifying providers, and explaining why an address received its result.

## Current architecture

- **Main repo:** `truemailer` — canonical backend, verification engine, and verification data.
- **Production web:** `truemailer-web` — existing Cloudflare/GitHub Pages frontend. Kept separate so the live deployment is not disrupted.
- **Legacy blocklist repo:** `truemailer-blocklist-data` — not used by the production API; its useful data has been consolidated into the main repo.
- **API hosting:** existing Render deployment.
- **Frontend hosting:** existing Cloudflare/GitHub Pages deployment.

The existing Render API URL is intentionally unchanged:

```text
https://truemailer-api.onrender.com
```

## Verification endpoint

```text
POST /verify
```

Request:

```json
{
  "email": "user@example.com"
}
```

The endpoint also accepts an optional `X-API-Key` header or `api_key` request field for client usage limits.

## Verification result

The current response can include:

- `valid` — overall verification result
- `syntax_valid` — email syntax check
- `domain_exists` — DNS resolution result
- `mx` — real MX-record availability
- `mx_hosts` — discovered MX hosts
- `is_disposable` / `disposable` — disposable-domain result
- `blocklisted` — local blocklist match
- `allowlisted` — local allowlist match
- `provider` — recognized mail provider
- `suspicious_indicators` — reasons for concern
- `trust_score` / `score` — 0–100 trust score
- `reason` — human-readable explanation
- `remote_disposable` — optional external disposable signal

Example:

```json
{
  "email": "user@example.com",
  "domain": "example.com",
  "valid": true,
  "syntax_valid": true,
  "domain_exists": true,
  "mx": true,
  "mx_hosts": ["mail.example.com"],
  "is_disposable": false,
  "blocklisted": false,
  "allowlisted": false,
  "provider": null,
  "suspicious_indicators": [],
  "trust_score": 85,
  "score": 85,
  "reason": "Domain resolves and accepts email via MX"
}
```

## Checks performed

1. Syntax validation
2. DNS domain resolution
3. Real MX-record lookup
4. Disposable/temporary-domain detection
5. Local blocklist and allowlist checks
6. Known provider detection
7. Suspicious-domain indicators
8. Trust/risk scoring
9. Human-readable reason
10. Optional external disposable-domain signal

## Data layout

```text
truemailer/
├── main.py
├── blocklist/
│   └── blocklist.txt
├── allowlist/
│   └── allowlist.json
├── clients.json
├── frontend/
│   └── index.html
├── ARCHITECTURE.md
└── README.md
```

## Deployment

No hosting migration is required for the current architecture. Keep the existing Render service and existing Cloudflare/GitHub Pages frontend URL while the consolidated main repository is developed and tested.

## Safety notes

Do not commit production secrets, admin tokens, private API keys, or real customer data. Configure `TRUEMAILER_ADMIN_TOKEN` and other deployment secrets through the hosting provider's secret/environment-variable settings.

## License

MIT License

## Developer

Ashish Naik  
GitHub: https://github.com/ashishnaikbackup