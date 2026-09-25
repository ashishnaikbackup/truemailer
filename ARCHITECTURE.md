# Truemailer architecture

## Canonical project

`truemailer` is the canonical source for the API, verification engine, allowlist, blocklist and project documentation.

## Production frontend

`truemailer-web` remains the production frontend repository because the existing Cloudflare Pages deployment points to it. The latest frontend is also synchronized into `frontend/index.html` in this repository by the `Sync Truemailer Web into Main` GitHub Actions workflow.

This keeps the current Cloudflare/Render setup unchanged while giving the main repository a complete project snapshot.

## Blocklist data

The useful disposable-domain data already lives in `blocklist/` in the main repository and is what the API reads. The separate `truemailer-blocklist-data` repository currently contains only an empty `public_blocklist.json` and an old demo `keys.json`; neither should replace the working data in this repository.

## Deployment

Current flow:

Cloudflare Pages -> `truemailer-web` -> `https://truemailer-api.onrender.com/verify` -> Truemailer API/DNS/blocklist checks.

Do not change Render or Cloudflare configuration as part of repository cleanup.
