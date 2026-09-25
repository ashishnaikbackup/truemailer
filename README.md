# Truemailer — Email Trust Analysis

Truemailer is an email verification and trust-analysis service for detecting disposable addresses, checking DNS/MX infrastructure, identifying providers, and explaining why an address received its result.

## Current architecture

The project is now consolidated around the **`truemailer`** repository.

- **Main repo:** `truemailer` — canonical backend, verification engine, blocklist/allowlist data, Cloudflare Worker and frontend.
- **API hosting:** existing Render deployment.
- **Frontend/edge hosting:** existing Cloudflare Worker + Workers Assets deployment from this repository.
- **Legacy `truemailer-web`:** no longer required as the production source after the consolidated deployment is verified.
- **Legacy `truemailer-blocklist-data`:** its useful disposable-domain data has been consolidated into `blocklist/blocklist.txt`.

The production API URL remains unchanged:

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

The response can include:

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
- `remote_disposable` — optional external disposable-domain signal

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

## Frontend

The frontend lives at `frontend/index.html` and is served through Cloudflare Workers Assets. The Cloudflare Worker in `cloudflare/worker.js` keeps the Render API behind the same edge deployment for `/verify`, `/status`, and `/health` while serving the frontend for other routes.

The verifier deliberately renders API failures on the same page instead of navigating back to the beginning.

## Reliability / keepalive

Render can sleep when a free service is inactive. Truemailer therefore has two complementary liveness mechanisms:

- **UptimeRobot** monitors `https://truemailer-api.onrender.com/health`.
- **GitHub Actions** runs `render-keepalive.yml` every five minutes and pings the same cheap `/health` endpoint with retries.

The health endpoint performs no DNS/MX verification, so monitoring does not consume verification work.

The keepalive reduces cold-start-related monitor failures but cannot guarantee availability if Render, GitHub Actions, DNS, or the network has an independent outage.

## Deployment

### Render

Keep the existing Render service and API URL. The `/health` endpoint is the liveness target and `/verify` remains the verification endpoint.

### Cloudflare

The Worker is deployed from the `main` branch with Workers Assets pointing to `./frontend`.

```text
name = "truemailer"
main = "cloudflare/worker.js"

[assets]
directory = "./frontend"
binding = "ASSETS"
```

No production API migration is required: the Render URL remains unchanged.

## Safety notes

Do not commit production secrets, admin tokens, private API keys, or real customer data. Configure deployment secrets through the hosting provider's secret/environment-variable settings.

## Limitations

Truemailer does **not** prove that a specific mailbox exists. DNS and MX checks establish domain/mail-server capability, not inbox ownership or deliverability.

The trust score is a rule-based signal from the checks currently available. It is not a guarantee that a person, mailbox, or domain is trustworthy.

## License

MIT License

## Developer

Ashish Naik
GitHub: https://github.com/ashishnaikbackup
